"""
Module 4 — Analyse boni-mali (run-off des provisions).

Mesure la variation de l'estimation de la charge ultime entre deux clôtures
successives, par cohorte d'année de survenance et par segment.

Convention :
    Boni-mali = Ultimate(N-1) - Ultimate(N)
    > 0  ->  BONI (l'estimation a baissé, provision libérée)
    < 0  ->  MALI (l'estimation a monté, provision renforcée)
"""

import numpy as np
import pandas as pd

from . import portefeuille as pf
from . import reserving as rs


# ---------------------------------------------------------------------------- #
def calculer_boni_mali(df_paiements, annee_cloture_n, annee_cloture_prec,
                      filtre_segment=None):
    """
    Reconstruit les triangles aux deux clotures, calcule l'Ultimate
    Chain-Ladder a chaque date, et retourne le boni-mali par cohorte.

    Parameters
    ----------
    df_paiements : pd.DataFrame
    annee_cloture_n : int
        Cloture courante (e.g. 2025).
    annee_cloture_prec : int
        Cloture precedente (e.g. 2024).
    filtre_segment : str, optional

    Returns
    -------
    pd.DataFrame
        Une ligne par cohorte commune aux deux clotures, colonnes :
        Annee_survenance, Ultimate_N1, Ultimate_N, Boni_mali,
        Variation_pct, Nature.
    """
    tri_prec = pf.construire_triangle(df_paiements, annee_cloture_prec,
                                       filtre_segment=filtre_segment)
    tri_n    = pf.construire_triangle(df_paiements, annee_cloture_n,
                                       filtre_segment=filtre_segment)

    T_prec_proj, _ = rs.projection_chain_ladder(tri_prec)
    T_n_proj, _    = rs.projection_chain_ladder(tri_n)

    ult_prec = pd.Series(T_prec_proj[:, -1], index=tri_prec.index)
    ult_n    = pd.Series(T_n_proj[:, -1], index=tri_n.index)

    cohortes = [a for a in ult_prec.index if a in ult_n.index]
    lignes = []
    for a in cohortes:
        bm = ult_prec[a] - ult_n[a]
        nature = "BONI" if bm > 0 else ("MALI" if bm < 0 else "NEUTRE")
        lignes.append({
            "Annee_survenance":      int(a),
            "Ultimate_N1":           float(ult_prec[a]),
            "Ultimate_N":            float(ult_n[a]),
            "Ultimate_cloture_2024": float(ult_prec[a]),  # alias pour compat
            "Ultimate_cloture_2025": float(ult_n[a]),     # alias pour compat
            "Boni_mali":             float(bm),
            "Variation_pct":         float(bm / ult_prec[a] * 100) if ult_prec[a] > 0 else 0.0,
            "Nature":                nature,
        })
    return pd.DataFrame(lignes)


# ---------------------------------------------------------------------------- #
def boni_mali_par_segment(df_paiements, segments,
                          annee_cloture_n, annee_cloture_prec):
    """
    Decline l'analyse boni-mali par segment et produit un tableau croise
    segment x cohorte.

    Returns
    -------
    pd.DataFrame
        Index = segments, colonnes = annees de survenance + TOTAL.
    """
    bm_dict = {}
    for seg in segments:
        df_bm_seg = calculer_boni_mali(
            df_paiements, annee_cloture_n, annee_cloture_prec,
            filtre_segment=seg
        )
        bm_dict[seg] = dict(zip(
            df_bm_seg["Annee_survenance"], df_bm_seg["Boni_mali"]
        ))
    df = pd.DataFrame(bm_dict).T
    df["TOTAL"] = df.sum(axis=1)
    return df
