"""
Module 5 — Compte technique non-vie.

Construit le P&L technique de l'exercice de souscription, brut et net de
réassurance, par segment, avec calcul des ratios S/P, frais et combiné.

Le boni-mali sur exercices antérieurs est integré comme item séparé du
compte (convention IFRS / Solvabilité II).
"""

import numpy as np
import pandas as pd

from . import config as cfg


# ---------------------------------------------------------------------------- #
def calculer_reassurance_xl(df_sinistres, exercice,
                            priorite=None, chargement=None):
    """
    Calcule les recuperations XL et la prime de reassurance cedee par segment
    pour la cohorte d'un exercice donne.

    Le reassureur prend en charge la part de chaque sinistre au-dela de la
    priorite. La prime cedee est calculee en chargeant les recuperations
    attendues du chargement reassureur.

    Returns
    -------
    pd.DataFrame
        Une ligne par segment, colonnes :
        Segment, N_sinistres_touches, Recuperations, Prime_cedee.
    """
    if priorite   is None: priorite   = cfg.PRIORITE_XL
    if chargement is None: chargement = cfg.CHARGEMENT_REASS

    sin_exercice = df_sinistres[df_sinistres["annee_survenance"] == exercice]
    lignes = []
    for seg in sorted(sin_exercice["segment"].unique()):
        sin_seg = sin_exercice[sin_exercice["segment"] == seg]
        excedents = np.maximum(sin_seg["ultimate_vrai"] - priorite, 0.0)
        recup = float(excedents.sum())
        n_touches = int((excedents > 0).sum())
        prime_cedee = recup * (1 + chargement)
        lignes.append({
            "Segment":              seg,
            "N_sinistres_touches":  n_touches,
            "Recuperations":        recup,
            "Prime_cedee":          prime_cedee,
        })
    return pd.DataFrame(lignes)


# ---------------------------------------------------------------------------- #
def construire_compte_technique(primes_par_segment,
                                charge_courant_par_segment,
                                boni_mali_par_segment,
                                reassurance_par_segment,
                                taux_frais_acq=None,
                                taux_frais_gest=None):
    """
    Assemble le compte technique non-vie par segment, avec ligne TOTAL.

    Structure :
        (+) Primes acquises
        (-) Charge sinistres courant
        (+/-) Boni-mali anterieurs        [boni: +, mali: - reduit la charge]
        (-) Frais d'acquisition
        (-) Frais de gestion
        (=) Resultat technique BRUT
        (-) Prime reass. cedee
        (+) Recuperations reass.
        (=) Resultat technique NET

    Ratios :
        S/P courant       = Charge courant / Primes
        S/P comptable     = (Charge courant - boni-mali) / Primes
        Ratio de frais    = Frais totaux / Primes
        Ratio combine     = S/P comptable + Ratio de frais

    Returns
    -------
    pd.DataFrame
        Une ligne par segment + TOTAL, colonnes detaillees ci-dessus.
    """
    if taux_frais_acq  is None: taux_frais_acq  = cfg.TAUX_FRAIS_ACQUISITION
    if taux_frais_gest is None: taux_frais_gest = cfg.TAUX_FRAIS_GESTION

    reass_dict = reassurance_par_segment.set_index("Segment").to_dict("index")
    segments = list(primes_par_segment.index)

    lignes = []
    for seg in segments:
        primes      = float(primes_par_segment[seg])
        charge_cour = float(charge_courant_par_segment[seg])
        bm          = float(boni_mali_par_segment[seg])
        frais_acq   = primes * taux_frais_acq
        frais_gest  = primes * taux_frais_gest

        # Convention : un boni (bm > 0) reduit la charge comptable
        charge_compta = charge_cour - bm
        resultat_brut = primes - charge_compta - frais_acq - frais_gest

        prime_cedee = reass_dict.get(seg, {}).get("Prime_cedee", 0.0)
        recup       = reass_dict.get(seg, {}).get("Recuperations", 0.0)
        resultat_net = resultat_brut - prime_cedee + recup

        lignes.append({
            "Segment":          seg,
            "Primes_acquises":  primes,
            "Charge_courant":   charge_cour,
            "Boni_mali":        bm,
            "Charge_comptable": charge_compta,
            "Frais_acquisition": frais_acq,
            "Frais_gestion":    frais_gest,
            "Resultat_brut":    resultat_brut,
            "Prime_reass_cedee": prime_cedee,
            "Recup_reass":      recup,
            "Resultat_net":     resultat_net,
            "SP_courant":       charge_cour / primes,
            "SP_comptable":     charge_compta / primes,
            "Ratio_frais":      (frais_acq + frais_gest) / primes,
            "Ratio_combine":    (charge_compta + frais_acq + frais_gest) / primes,
        })

    df = pd.DataFrame(lignes)

    # Ligne TOTAL
    total = {"Segment": "TOTAL"}
    for col in ["Primes_acquises", "Charge_courant", "Boni_mali",
                "Charge_comptable", "Frais_acquisition", "Frais_gestion",
                "Resultat_brut", "Prime_reass_cedee", "Recup_reass",
                "Resultat_net"]:
        total[col] = df[col].sum()
    total["SP_courant"]    = total["Charge_courant"]   / total["Primes_acquises"]
    total["SP_comptable"]  = total["Charge_comptable"] / total["Primes_acquises"]
    total["Ratio_frais"]   = (total["Frais_acquisition"] + total["Frais_gestion"]) \
                             / total["Primes_acquises"]
    total["Ratio_combine"] = total["SP_comptable"] + total["Ratio_frais"]
    df = pd.concat([df, pd.DataFrame([total])], ignore_index=True)

    return df
