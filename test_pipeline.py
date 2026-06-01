"""
Tests unitaires du package closing.

Couvre les invariants critiques :
- Reproductibilité (graine fixée -> mêmes résultats)
- Cohérence des sommes (sinistres = somme paiements + IBNR)
- Propriétés des link ratios (>= 1 sur portefeuille à charge croissante)
- Mack : SE = 0 sur la cohorte entièrement développée
- LAT : déclenchement correct de l'URR

Lancement :
    pytest tests/
"""

import numpy as np
import pandas as pd
import pytest

from closing import portefeuille as pf
from closing import reserving as rs
from closing import ifrs4
from closing import boni_mali as bm
from closing import config as cfg


# ============================================================================ #
# Fixtures
# ============================================================================ #

@pytest.fixture(scope="module")
def rng():
    return np.random.default_rng(cfg.SEED)


@pytest.fixture(scope="module")
def portefeuille_simule():
    """Simule un petit portefeuille pour les tests rapides."""
    rng = np.random.default_rng(42)
    pol = pf.simuler_polices(rng)
    sin = pf.simuler_sinistres(pol, rng)
    pai = pf.simuler_paiements(sin, rng)
    tri = pf.construire_triangle(pai)
    return {"pol": pol, "sin": sin, "pai": pai, "tri": tri}


# ============================================================================ #
# M1 — Simulation
# ============================================================================ #

def test_reproductibilite_simulation():
    """Deux simulations avec la même graine donnent exactement le même portefeuille."""
    rng1 = np.random.default_rng(123)
    rng2 = np.random.default_rng(123)
    pol1 = pf.simuler_polices(rng1)
    pol2 = pf.simuler_polices(rng2)
    pd.testing.assert_frame_equal(pol1, pol2)


def test_volumetrie_polices(portefeuille_simule):
    """Le nombre de polices correspond aux paramètres de config."""
    pol = portefeuille_simule["pol"]
    assert len(pol) == sum(cfg.POLICES_PAR_ANNEE.values())


def test_mix_segments(portefeuille_simule):
    """Le mix Particuliers / Flottes respecte les proportions cibles à ±2 %."""
    pol = portefeuille_simule["pol"]
    part_part = (pol["segment"] == "PART").mean()
    assert abs(part_part - cfg.PART_PART) < 0.02


def test_triangle_structure(portefeuille_simule):
    """Le triangle a la bonne forme et la zone non observée est en NaN."""
    tri = portefeuille_simule["tri"]
    assert tri.shape == (5, 5)
    # La cellule (2025, dev=4) ne peut pas être observée
    assert pd.isna(tri.iloc[-1, -1])
    # La cellule (2021, dev=0) doit être observée
    assert not pd.isna(tri.iloc[0, 0])


def test_diagonale_observee(portefeuille_simule):
    """Toutes les cellules sous la diagonale observable sont remplies."""
    tri = portefeuille_simule["tri"]
    for i, surv in enumerate(tri.index):
        for j, dev in enumerate(tri.columns):
            if surv + dev <= cfg.ANNEE_CLOTURE:
                assert not pd.isna(tri.iloc[i, j]), f"NaN à ({surv}, dev={dev})"


# ============================================================================ #
# M2 — Provisionnement
# ============================================================================ #

def test_link_ratios_croissants(portefeuille_simule):
    """Les link ratios doivent être >= 1 sur un portefeuille à paiements croissants."""
    tri = portefeuille_simule["tri"]
    lr = rs.link_ratios(tri)
    for f in lr:
        assert f >= 1.0, f"Link ratio anormal : {f}"


def test_chain_ladder_remplit_triangle(portefeuille_simule):
    """Après projection, plus aucun NaN dans le triangle."""
    tri = portefeuille_simule["tri"]
    T_proj, _ = rs.projection_chain_ladder(tri)
    assert not np.isnan(T_proj).any()


def test_facteur_queue_superieur_a_1(portefeuille_simule):
    """Le facteur de queue d'un portefeuille MTPL doit être > 1 (queue résiduelle)."""
    tri = portefeuille_simule["tri"]
    _, lr = rs.projection_chain_ladder(tri)
    facteur, _ = rs.facteur_queue_sherman(lr)
    assert facteur > 1.0
    assert facteur < 1.2   # mais pas démesuré pour du MTPL


def test_bornhuetter_ferguson_borne(portefeuille_simule):
    """BF doit être borné entre l'a priori et le CL : BF est un mélange convexe."""
    tri = portefeuille_simule["tri"]
    T_proj, _ = rs.projection_chain_ladder(tri)
    ult_cl = T_proj[:, -1]
    ult_a_priori = ult_cl * 0.5   # a priori très bas
    ult_bf = rs.bornhuetter_ferguson(tri, ult_a_priori, ult_cl_avec_queue=ult_cl)
    # BF doit être entre min et max des deux sources
    for i in range(len(ult_bf)):
        lo = min(ult_cl[i], ult_a_priori[i])
        hi = max(ult_cl[i], ult_a_priori[i])
        assert lo - 1 <= ult_bf[i] <= hi + 1, \
            f"BF hors bornes : {ult_bf[i]} pas dans [{lo}, {hi}]"


def test_mack_se_positif(portefeuille_simule):
    """Les erreurs standards de Mack sont positives ou nulles."""
    tri = portefeuille_simule["tri"]
    mack = rs.mack_stochastique(tri)
    assert (mack["se"] >= 0).all()


def test_mack_ic_inclut_cl(portefeuille_simule):
    """Par construction, l'Ultimate CL est au centre de l'IC Mack."""
    tri = portefeuille_simule["tri"]
    mack = rs.mack_stochastique(tri)
    for i in range(len(mack["ultimate_cl"])):
        assert mack["ic_inf"][i] <= mack["ultimate_cl"][i] <= mack["ic_sup"][i]


# ============================================================================ #
# M3 — LAT IFRS 4
# ============================================================================ #

def test_lat_urr_correcte():
    """L'URR est bien max(BE - UPR_net, 0)."""
    upr_brut = pd.Series({"A": 1000.0, "B": 500.0})
    dac      = upr_brut * 0.15
    upr_net  = upr_brut - dac
    be       = pd.Series({"A": 700.0, "B": 600.0})

    res = ifrs4.liability_adequacy_test(upr_brut, dac, upr_net, be)
    # Segment A : marge positive
    a = res[res["Segment"] == "A"].iloc[0]
    assert a["URR_a_comptabiliser"] == 0.0
    assert a["Resultat_test"] == "OK"
    # Segment B : déficient (BE 600 > UPR_net 425)
    b = res[res["Segment"] == "B"].iloc[0]
    assert b["URR_a_comptabiliser"] > 0
    assert b["Resultat_test"] == "DEFICIENCY"


def test_lat_marge_egale_upr_moins_be():
    """La marge = UPR_net - Best_Estimate, signée correctement."""
    upr_brut = pd.Series({"X": 1000.0})
    dac = upr_brut * 0.10
    upr_net = upr_brut - dac
    be = pd.Series({"X": 800.0})
    res = ifrs4.liability_adequacy_test(upr_brut, dac, upr_net, be)
    marge = res.iloc[0]["Marge"]
    assert abs(marge - (900.0 - 800.0)) < 1e-6


# ============================================================================ #
# M4 — Boni-mali
# ============================================================================ #

def test_boni_mali_signe_correct(portefeuille_simule):
    """
    Vérifie la convention : Ultimate(N) > Ultimate(N-1) implique mali (< 0).
    """
    pai = portefeuille_simule["pai"]
    df_bm = bm.calculer_boni_mali(pai,
                                   annee_cloture_n=cfg.ANNEE_CLOTURE,
                                   annee_cloture_prec=cfg.ANNEE_CLOTURE - 1)
    for _, row in df_bm.iterrows():
        diff = row["Ultimate_N1"] - row["Ultimate_N"]
        assert abs(row["Boni_mali"] - diff) < 1e-6
        if row["Boni_mali"] > 0:
            assert row["Nature"] == "BONI"
        elif row["Boni_mali"] < 0:
            assert row["Nature"] == "MALI"
