"""
Pipeline orchestrateur du closing actuariel.

Assemble les six modules en une chaîne reproductible :
    1. Simulation du portefeuille
    2. Provisionnement (Chain-Ladder, BF, Mack)
    3. LAT IFRS 4
    4. Boni-mali
    5. Compte technique
    6. Contrôles automatiques

Exporte tous les résultats intermédiaires sous data/processed/.
Retourne un dict structuré contenant toutes les sorties pour usage
en aval (génération du dashboard HTML, classeur Excel, reports).
"""

import os
import numpy as np
import pandas as pd

from . import config as cfg
from . import portefeuille as pf
from . import reserving as rs
from . import ifrs4
from . import boni_mali as bm
from . import compte_technique as ct
from . import controles


def executer_closing(repertoire_data, verbose=True):
    """
    Execute la chaine complete de cloture et retourne tous les resultats.

    Parameters
    ----------
    repertoire_data : str
        Repertoire racine du projet (contient data/raw et data/processed).
    verbose : bool
        Affiche la progression dans la console.

    Returns
    -------
    dict
        Toutes les sorties intermediaires et finales.
    """
    def log(msg):
        if verbose:
            print(msg)

    rng = np.random.default_rng(cfg.SEED)

    dir_raw  = os.path.join(repertoire_data, "data", "raw")
    dir_proc = os.path.join(repertoire_data, "data", "processed")
    os.makedirs(dir_raw,  exist_ok=True)
    os.makedirs(dir_proc, exist_ok=True)

    # ====================================================================== #
    # M1 — SIMULATION
    # ====================================================================== #
    log("[M1] Simulation du portefeuille...")
    df_polices   = pf.simuler_polices(rng)
    df_sinistres = pf.simuler_sinistres(df_polices, rng)
    df_paiements = pf.simuler_paiements(df_sinistres, rng)
    triangle     = pf.construire_triangle(df_paiements)

    df_polices.to_csv  (os.path.join(dir_raw,  "polices.csv"),   index=False)
    df_sinistres.to_csv(os.path.join(dir_raw,  "sinistres.csv"), index=False)
    df_paiements.to_csv(os.path.join(dir_raw,  "paiements.csv"), index=False)
    triangle.to_csv    (os.path.join(dir_proc, "triangle_paiements_cumules.csv"))

    ult_vrai = df_sinistres.groupby("annee_survenance")["ultimate_vrai"].sum()
    ult_vrai.to_csv(os.path.join(dir_proc, "ultimate_vrai_par_annee.csv"),
                    header=["ultimate_vrai_total"])

    log(f"    {len(df_polices):,} polices, {len(df_sinistres):,} sinistres, "
        f"{len(df_paiements):,} flux".replace(",", " "))

    # ====================================================================== #
    # M2 — PROVISIONNEMENT
    # ====================================================================== #
    log("[M2] Provisionnement (Chain-Ladder, BF, Mack)...")

    T_proj_cl, link_ratios = rs.projection_chain_ladder(triangle)
    ult_cl = T_proj_cl[:, -1]

    facteur_q, diag_q = rs.facteur_queue_sherman(link_ratios)
    ult_cl_q = ult_cl * facteur_q

    primes_par_annee = df_polices.groupby("annee_souscription")["prime_acquise"].sum()
    ult_a_priori = cfg.SP_A_PRIORI_BF * primes_par_annee.values
    ult_bf = rs.bornhuetter_ferguson(triangle, ult_a_priori,
                                      ult_cl_avec_queue=ult_cl_q)

    mack = rs.mack_stochastique(triangle)

    df_synthese = pd.DataFrame({
        "Annee":              list(triangle.index),
        "Ultimate_vrai":      ult_vrai.values,
        "CL_sans_queue":      ult_cl,
        "CL_avec_queue":      ult_cl_q,
        "BF":                 ult_bf,
        "Mack_SE":            mack["se"],
        "Mack_IC_inf":        mack["ic_inf"],
        "Mack_IC_sup":        mack["ic_sup"],
    })
    df_synthese.to_csv(os.path.join(dir_proc, "m2_synthese_provisionnement.csv"),
                       index=False)

    # IBNR par cohorte
    paiements_observes = np.array([
        triangle.iloc[i, np.where(~np.isnan(triangle.iloc[i, :]))[0].max()]
        for i in range(len(triangle))
    ])
    df_ibnr = pd.DataFrame({
        "Annee":              list(triangle.index),
        "Paiements_observes": paiements_observes,
        "IBNR_CL":            ult_cl   - paiements_observes,
        "IBNR_CL_queue":      ult_cl_q - paiements_observes,
        "IBNR_BF":            ult_bf   - paiements_observes,
    })
    df_ibnr.to_csv(os.path.join(dir_proc, "m2_IBNR.csv"), index=False)

    log(f"    Ultimate BF total : {ult_bf.sum():,.0f} EUR "
        f"(ecart vs verite : {(ult_bf.sum()/ult_vrai.sum()-1)*100:+.2f} %)"
        .replace(",", " "))

    # ====================================================================== #
    # M3 — LAT IFRS 4
    # ====================================================================== #
    log("[M3] Liability Adequacy Test IFRS 4...")

    upr_dac = ifrs4.calculer_upr_dac(df_polices, rng)
    upr_seg     = upr_dac["upr_par_segment"]
    dac_seg     = upr_dac["dac_par_segment"]
    upr_net_seg = upr_dac["upr_net_par_segment"]

    # S/P ultime par segment (verite terrain pour cle de ventilation)
    prime_seg  = df_polices.groupby("segment")["prime_acquise"].sum()
    charge_seg = df_sinistres.groupby("segment")["ultimate_vrai"].sum()
    sp_seg     = charge_seg / prime_seg

    be_seg = ifrs4.best_estimate_par_segment(upr_seg, sp_seg)
    df_lat = ifrs4.liability_adequacy_test(upr_seg, dac_seg, upr_net_seg, be_seg)
    df_lat.to_csv(os.path.join(dir_proc, "m3_liability_adequacy_test.csv"),
                  index=False)

    psap_total = df_ibnr["IBNR_BF"].sum()
    urr_total  = df_lat["URR_a_comptabiliser"].sum()
    df_prov_totales = pd.DataFrame({
        "Provision": ["PSAP_sinistres", "UPR_primes_non_acquises",
                      "URR_risque_en_cours", "TOTAL"],
        "Montant":   [psap_total, upr_seg.sum(), urr_total,
                      psap_total + upr_seg.sum() + urr_total],
    })
    df_prov_totales.to_csv(
        os.path.join(dir_proc, "m3_provisions_techniques_totales.csv"),
        index=False
    )

    log(f"    URR a comptabiliser : {urr_total:,.0f} EUR".replace(",", " "))

    # ====================================================================== #
    # M4 — BONI-MALI
    # ====================================================================== #
    log("[M4] Analyse boni-mali...")

    df_bm = bm.calculer_boni_mali(df_paiements,
                                   annee_cloture_n=cfg.ANNEE_CLOTURE,
                                   annee_cloture_prec=cfg.ANNEE_CLOTURE - 1)
    df_bm.to_csv(os.path.join(dir_proc, "m4_boni_mali_global.csv"), index=False)

    segments = sorted(df_polices["segment"].unique())
    df_bm_seg = bm.boni_mali_par_segment(df_paiements, segments,
                                          annee_cloture_n=cfg.ANNEE_CLOTURE,
                                          annee_cloture_prec=cfg.ANNEE_CLOTURE - 1)
    df_bm_seg.to_csv(os.path.join(dir_proc, "m4_boni_mali_par_segment.csv"))

    log(f"    Boni-mali global : {df_bm['Boni_mali'].sum():+,.0f} EUR"
        .replace(",", " "))

    # ====================================================================== #
    # M5 — COMPTE TECHNIQUE
    # ====================================================================== #
    log("[M5] Compte technique...")

    # Primes acquises et charge courant pour la cohorte de l'exercice
    primes_seg_n = df_polices[
        df_polices["annee_souscription"] == cfg.ANNEE_CLOTURE
    ].groupby("segment")["prime_acquise"].sum()

    # Ventilation de l'Ultimate BF de l'exercice par segment (prorata verite)
    sin_n = df_sinistres[df_sinistres["annee_survenance"] == cfg.ANNEE_CLOTURE]
    charge_vraie_n_seg = sin_n.groupby("segment")["ultimate_vrai"].sum()
    cle = charge_vraie_n_seg / charge_vraie_n_seg.sum()
    ult_bf_n_total = float(ult_bf[-1])   # derniere cohorte = exercice courant
    charge_cour_seg = ult_bf_n_total * cle

    # Boni-mali par segment
    bm_seg_serie = df_bm_seg["TOTAL"]

    # Reassurance XL
    df_reass = ct.calculer_reassurance_xl(df_sinistres, cfg.ANNEE_CLOTURE)

    df_compte = ct.construire_compte_technique(
        primes_par_segment=primes_seg_n,
        charge_courant_par_segment=charge_cour_seg,
        boni_mali_par_segment=bm_seg_serie,
        reassurance_par_segment=df_reass,
    )
    df_compte.to_csv(os.path.join(dir_proc, "m5_compte_technique.csv"),
                     index=False)

    combine_tot = df_compte.loc[df_compte["Segment"] == "TOTAL",
                                "Ratio_combine"].values[0]
    log(f"    Ratio combine global : {combine_tot:.1%}")

    # ====================================================================== #
    # M6 — CONTROLES DE COHERENCE
    # ====================================================================== #
    log("[M6] Controles de coherence...")

    df_journal = controles.executer_controles(
        ibnr_par_cohorte=df_ibnr["IBNR_BF"],
        boni_mali_global=df_bm,
        boni_mali_par_segment=df_bm_seg["TOTAL"],
        resultat_lat=df_lat,
        compte_technique=df_compte,
    )
    df_journal.to_csv(os.path.join(dir_proc, "m6_journal_controles.csv"),
                      index=False)

    n_alertes = (df_journal["Statut"] == "ALERTE").sum()
    log(f"    {n_alertes} alerte(s) sur {len(df_journal)} controles")

    # ====================================================================== #
    # RETOUR STRUCTURE
    # ====================================================================== #
    return {
        "polices":          df_polices,
        "sinistres":        df_sinistres,
        "paiements":        df_paiements,
        "triangle":         triangle,
        "ultimate_vrai":    ult_vrai,
        "synthese_prov":    df_synthese,
        "ibnr":             df_ibnr,
        "lat":              df_lat,
        "provisions_totales": df_prov_totales,
        "boni_mali":        df_bm,
        "boni_mali_seg":    df_bm_seg,
        "compte_technique": df_compte,
        "journal_controles": df_journal,
        "n_alertes":        int(n_alertes),
    }
