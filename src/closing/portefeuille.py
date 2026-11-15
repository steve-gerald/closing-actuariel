"""
Module 1 — Simulation du portefeuille MTPL.

Construit un portefeuille non-vie réaliste avec :
- polices souscrites sur 5 années,
- sinistres tirés selon fréquence Poisson et sévérité Lognormale,
- développement temporel des paiements (court vs long tail),
- conservation de la vérité terrain pour permettre le backtesting.

Fonctions exposées :
    simuler_polices(rng)              -> DataFrame
    simuler_sinistres(polices, rng)   -> DataFrame
    simuler_paiements(sinistres, rng) -> DataFrame
    construire_triangle(paiements)    -> DataFrame (triangle cumule)
"""

import numpy as np
import pandas as pd

from . import config as cfg


# ---------------------------------------------------------------------------- #
def simuler_polices(rng):
    """
    Simule les polices souscrites sur la periode 2021-2025.

    Parameters
    ----------
    rng : np.random.Generator

    Returns
    -------
    pd.DataFrame
        Colonnes : police_id, annee_souscription, segment, prime_acquise, exposition
    """
    polices = []
    pol_id = 1
    for annee, n_pol in cfg.POLICES_PAR_ANNEE.items():
        segments = rng.choice(
            ["PART", "FLOTTE"],
            size=n_pol,
            p=[cfg.PART_PART, cfg.PART_FLOTTE],
        )
        for seg in segments:
            # Tirage Lognormale parametree en moyenne et CV
            if seg == "PART":
                moy, cv = cfg.PRIME_PART_MOY, cfg.PRIME_PART_CV
            else:
                moy, cv = cfg.PRIME_FLOTTE_MOY, cfg.PRIME_FLOTTE_CV
            sigma = np.sqrt(np.log(1 + cv ** 2))
            mu    = np.log(moy) - 0.5 * sigma ** 2
            prime = float(rng.lognormal(mean=mu, sigma=sigma))

            polices.append({
                "police_id":         f"P{pol_id:07d}",
                "annee_souscription": int(annee),
                "segment":           seg,
                "prime_acquise":     round(prime, 2),
                "exposition":        1.0,
            })
            pol_id += 1
    return pd.DataFrame(polices)


# ---------------------------------------------------------------------------- #
def simuler_sinistres(df_polices, rng):
    """
    Simule les sinistres a partir des polices : frequence Poisson par segment,
    severite Lognormale par garantie, application de l'inflation annuelle.

    Parameters
    ----------
    df_polices : pd.DataFrame
    rng : np.random.Generator

    Returns
    -------
    pd.DataFrame
        Colonnes : sinistre_id, police_id, annee_survenance, segment,
                   garantie, ultimate_vrai
    """
    sinistres = []
    sin_id = 1
    for _, pol in df_polices.iterrows():
        freq = cfg.FREQ_PART if pol["segment"] == "PART" else cfg.FREQ_FLOTTE
        n_sin = rng.poisson(lam=freq * pol["exposition"])

        for _ in range(n_sin):
            # Tirage de la garantie
            garantie = rng.choice(
                ["MATERIEL", "CORPOREL"],
                p=[cfg.PART_MATERIEL, cfg.PART_CORPOREL],
            )
            # Severite
            if garantie == "MATERIEL":
                ult = rng.lognormal(mean=cfg.SEV_MAT_MU,  sigma=cfg.SEV_MAT_SIGMA)
            else:
                ult = rng.lognormal(mean=cfg.SEV_CORP_MU, sigma=cfg.SEV_CORP_SIGMA)

            # Application de l'inflation
            annees_ecoulees = pol["annee_souscription"] - cfg.ANNEES_SURVENANCE[0]
            ult *= (1 + cfg.INFLATION_ANNUELLE) ** annees_ecoulees

            sinistres.append({
                "sinistre_id":      f"S{sin_id:08d}",
                "police_id":        pol["police_id"],
                "annee_survenance": int(pol["annee_souscription"]),
                "segment":          pol["segment"],
                "garantie":         garantie,
                "ultimate_vrai":    round(ult, 2),
            })
            sin_id += 1
    return pd.DataFrame(sinistres)


# ---------------------------------------------------------------------------- #
def simuler_paiements(df_sinistres, rng):
    """
    Genere les flux de paiement de chaque sinistre selon son pattern de
    developpement (court-tail materiel, long-tail corporel), avec un bruit
    multiplicatif lognormal pour eviter un developpement deterministe.

    Seuls les paiements observes au 31/12/ANNEE_CLOTURE sont retournes.

    Parameters
    ----------
    df_sinistres : pd.DataFrame
    rng : np.random.Generator

    Returns
    -------
    pd.DataFrame
        Colonnes : sinistre_id, annee_survenance, annee_developpement,
                   annee_calendaire, segment, garantie, paiement_incremental
    """
    paiements = []
    for _, sin in df_sinistres.iterrows():
        pattern = (cfg.PATTERN_MATERIEL if sin["garantie"] == "MATERIEL"
                   else cfg.PATTERN_CORPOREL)
        pattern_inc = np.diff(np.concatenate([[0.0], pattern]))

        # Bruit multiplicatif lognormal autour de 1
        bruit = rng.lognormal(mean=-0.005, sigma=0.10, size=len(pattern_inc))
        pattern_bruite = pattern_inc * bruit

        for dev in range(cfg.N_ANNEES_DEV_MAX):
            annee_paiement = sin["annee_survenance"] + dev
            if annee_paiement > cfg.ANNEE_CLOTURE:
                continue
            montant = sin["ultimate_vrai"] * pattern_bruite[dev]
            paiements.append({
                "sinistre_id":          sin["sinistre_id"],
                "annee_survenance":     sin["annee_survenance"],
                "annee_developpement":  dev,
                "annee_calendaire":     annee_paiement,
                "garantie":             sin["garantie"],
                "segment":              sin["segment"],
                "paiement_incremental": round(max(montant, 0.0), 2),
            })
    return pd.DataFrame(paiements)


# ---------------------------------------------------------------------------- #
def construire_triangle(df_paiements,
                        annee_cloture=None,
                        filtre_segment=None):
    """
    Construit le triangle des paiements cumules visible a une date de cloture.

    Parameters
    ----------
    df_paiements : pd.DataFrame
    annee_cloture : int, optional
        Date de cloture (default : ANNEE_CLOTURE de la config).
    filtre_segment : str, optional
        Restreint le triangle a un segment ("PART" ou "FLOTTE").

    Returns
    -------
    pd.DataFrame
        Triangle 5x5 avec NaN au-dela de la sous-diagonale observee.
    """
    if annee_cloture is None:
        annee_cloture = cfg.ANNEE_CLOTURE

    df = df_paiements.copy()
    if filtre_segment is not None:
        df = df[df["segment"] == filtre_segment]
    df = df[df["annee_calendaire"] <= annee_cloture]
    df = df[df["annee_survenance"] <= annee_cloture]

    tri_inc = (
        df.groupby(["annee_survenance", "annee_developpement"])
          ["paiement_incremental"].sum()
          .unstack(fill_value=0.0)
          .sort_index()
    )
    tri_cum = tri_inc.cumsum(axis=1)

    # Masquer la zone non observee (survenance + dev > cloture)
    for i, surv in enumerate(tri_cum.index):
        for j, dev in enumerate(tri_cum.columns):
            if surv + dev > annee_cloture:
                tri_cum.iloc[i, j] = np.nan
    return tri_cum
