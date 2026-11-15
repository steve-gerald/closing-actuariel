"""
Module 3 — Liability Adequacy Test sous référentiel IFRS 4.

Vérifie que la provision pour primes non acquises (UPR), nette des frais
d'acquisition reportés (DAC), suffit à couvrir le best estimate des charges
futures sur la période non couverte. Si non, une provision pour risque en
cours (URR) doit être comptabilisée.

Fonctions exposées :
    calculer_upr_dac(polices, rng, taux_dac)        -> dict
    best_estimate_par_segment(upr, sp, frais)       -> pd.Series
    liability_adequacy_test(upr_net, best_estimate) -> pd.DataFrame
"""

import numpy as np
import pandas as pd

from . import config as cfg


# ---------------------------------------------------------------------------- #
def calculer_upr_dac(df_polices, rng, taux_dac=None):
    """
    Calcule l'UPR et le DAC sur la cohorte de l'annee de cloture.

    Methode 1/24 : on tire un mois de souscription uniforme [1..12] et la
    part de prime NON acquise au 31/12 est (mois - 0.5) / 12.

    Parameters
    ----------
    df_polices : pd.DataFrame
    rng : np.random.Generator
    taux_dac : float, optional
        Defaut : config.TAUX_FRAIS_ACQUISITION

    Returns
    -------
    dict avec :
        - upr_par_segment : pd.Series
        - dac_par_segment : pd.Series
        - upr_net_par_segment : pd.Series
        - polices_enrichies : pd.DataFrame (mois et part non acquise ajoutes)
    """
    if taux_dac is None:
        taux_dac = cfg.TAUX_FRAIS_ACQUISITION

    pol_cloture = df_polices[
        df_polices["annee_souscription"] == cfg.ANNEE_CLOTURE
    ].copy()

    pol_cloture["mois_souscription"] = rng.integers(1, 13, size=len(pol_cloture))
    pol_cloture["part_non_acquise"] = (pol_cloture["mois_souscription"] - 0.5) / 12
    pol_cloture["upr"] = pol_cloture["prime_acquise"] * pol_cloture["part_non_acquise"]

    upr_seg = pol_cloture.groupby("segment")["upr"].sum()
    dac_seg = upr_seg * taux_dac
    upr_net = upr_seg - dac_seg

    return {
        "upr_par_segment":     upr_seg,
        "dac_par_segment":     dac_seg,
        "upr_net_par_segment": upr_net,
        "polices_enrichies":   pol_cloture,
    }


# ---------------------------------------------------------------------------- #
def best_estimate_par_segment(upr_brut, sp_par_segment,
                              taux_gestion=None, taux_sinistres=None):
    """
    Calcule le best estimate des charges futures par segment.

        BE = UPR_brut * (S/P + frais_gestion + frais_sinistres)

    Les frais d'acquisition ne sont pas recomptes ici : ils sont deja
    dans le DAC.

    Parameters
    ----------
    upr_brut : pd.Series
    sp_par_segment : pd.Series
    taux_gestion, taux_sinistres : float, optional

    Returns
    -------
    pd.Series
        Best estimate par segment.
    """
    if taux_gestion   is None: taux_gestion   = cfg.TAUX_FRAIS_GESTION
    if taux_sinistres is None: taux_sinistres = cfg.TAUX_FRAIS_SINISTRES

    be = pd.Series(dtype=float)
    for seg in upr_brut.index:
        ratio_charge = sp_par_segment[seg] + taux_gestion + taux_sinistres
        be[seg] = upr_brut[seg] * ratio_charge
    return be


# ---------------------------------------------------------------------------- #
def liability_adequacy_test(upr_brut, dac, upr_net, best_estimate):
    """
    Realise le LAT par segment et calcule l'URR (Unexpired Risk Reserve).

    Test : UPR_net >= Best_Estimate ?
      - oui : OK, pas de provision complementaire
      - non : DEFICIENCY, URR = BE - UPR_net a comptabiliser

    Returns
    -------
    pd.DataFrame
        Une ligne par segment, colonnes :
        UPR_brut, DAC, UPR_net, Best_Estimate, Marge, URR, Resultat_test.
    """
    lignes = []
    for seg in upr_brut.index:
        marge = upr_net[seg] - best_estimate[seg]
        urr   = max(-marge, 0.0)
        statut = "OK" if marge >= 0 else "DEFICIENCY"
        lignes.append({
            "Segment":             seg,
            "UPR_brut":            float(upr_brut[seg]),
            "DAC":                 float(dac[seg]),
            "UPR_net":             float(upr_net[seg]),
            "Best_Estimate":       float(best_estimate[seg]),
            "Marge":               float(marge),
            "URR_a_comptabiliser": float(urr),
            "Resultat_test":       statut,
        })
    return pd.DataFrame(lignes)
