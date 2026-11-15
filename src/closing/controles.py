"""
Module 6 — Contrôles de cohérence automatiques du closing.

Six contrôles déterministes appliqués sur les résultats agrégés des modules
précédents, avec seuils d'alerte définis dans la configuration.

Chaque contrôle retourne un dict {Controle, Statut, Detail} ajouté au
journal des contrôles. Le journal est exporté au format CSV et alimente
l'onglet « 6_Controles » du classeur Excel de pilotage.
"""

import pandas as pd

from . import config as cfg


def _ctrl(libelle, ok, detail):
    return {
        "Controle": libelle,
        "Statut":   "OK" if ok else "ALERTE",
        "Detail":   detail,
    }


# ---------------------------------------------------------------------------- #
def executer_controles(ibnr_par_cohorte,
                       boni_mali_global,
                       boni_mali_par_segment,
                       resultat_lat,
                       compte_technique):
    """
    Execute les six controles de coherence et retourne le journal.

    Returns
    -------
    pd.DataFrame
        Une ligne par controle, colonnes : Controle, Statut, Detail.
    """
    journal = []

    # C1 - IBNR positif
    ibnr_min = float(ibnr_par_cohorte.min())
    journal.append(_ctrl(
        "C1 - IBNR positif sur toutes les cohortes",
        ibnr_min >= 0,
        f"IBNR minimum = {ibnr_min:,.0f} EUR".replace(",", " ")
    ))

    # C2 - Reconciliation boni-mali (global vs somme segments)
    bm_global   = float(boni_mali_global["Boni_mali"].sum()) \
                  if isinstance(boni_mali_global, pd.DataFrame) \
                  else float(boni_mali_global.sum())
    bm_segments = float(boni_mali_par_segment.sum())
    if bm_global != 0:
        ecart = abs(bm_global - bm_segments) / abs(bm_global)
    else:
        ecart = 0.0
    journal.append(_ctrl(
        "C2 - Reconciliation boni-mali (global vs segments)",
        ecart <= cfg.SEUIL_RECONCILIATION,
        f"Global {bm_global:,.0f} vs segments {bm_segments:,.0f} EUR "
        f"-> ecart {ecart:.2%} (seuil {cfg.SEUIL_RECONCILIATION:.0%})"
        .replace(",", " ")
    ))

    # C3 - Aucun mali significatif par cohorte
    malis_sig = boni_mali_global[
        boni_mali_global["Variation_pct"] < -cfg.SEUIL_MALI_COHORTE * 100
    ]
    journal.append(_ctrl(
        "C3 - Aucun mali significatif par cohorte",
        len(malis_sig) == 0,
        f"{len(malis_sig)} cohorte(s) avec mali > {cfg.SEUIL_MALI_COHORTE:.0%} : "
        f"{[int(a) for a in malis_sig['Annee_survenance'].values]}"
    ))

    # C4 - Aucun segment en premium deficiency (LAT)
    deficients = resultat_lat[resultat_lat["Resultat_test"] == "DEFICIENCY"]
    journal.append(_ctrl(
        "C4 - Aucun segment en premium deficiency (LAT)",
        len(deficients) == 0,
        f"{len(deficients)} segment(s) deficient(s) : "
        f"{[str(x) for x in deficients['Segment']]}"
    ))

    # C5 - Ratio combine global rentable
    combine_total = float(
        compte_technique.loc[compte_technique["Segment"] == "TOTAL",
                             "Ratio_combine"].values[0]
    )
    journal.append(_ctrl(
        "C5 - Ratio combine global rentable",
        combine_total < cfg.SEUIL_COMBINE_RENTABLE,
        f"Ratio combine = {combine_total:.1%} "
        f"(seuil {cfg.SEUIL_COMBINE_RENTABLE:.0%})"
    ))

    # C6 - Aucun segment en perte technique
    en_perte = compte_technique[
        (compte_technique["Segment"] != "TOTAL") &
        (compte_technique["Ratio_combine"] >= 1.00)
    ]
    journal.append(_ctrl(
        "C6 - Aucun segment en perte technique",
        len(en_perte) == 0,
        f"{len(en_perte)} segment(s) en perte : "
        f"{[str(x) for x in en_perte['Segment']]}"
    ))

    return pd.DataFrame(journal)
