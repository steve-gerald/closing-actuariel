"""
Module 2 — Provisionnement des sinistres.

Implémente de manière procédurale et lisible quatre méthodes de
provisionnement : Chain-Ladder déterministe, facteur de queue (Sherman),
Bornhuetter-Ferguson, et Mack stochastique avec intervalle de confiance.

Aucune dépendance à une bibliothèque actuarielle externe. Le triangle est
manipulé sous forme d'array numpy pour faciliter la gestion des NaN.

Fonctions exposées :
    link_ratios(triangle)                -> list
    projection_chain_ladder(triangle)    -> (np.ndarray, list)
    facteur_queue_sherman(link_ratios)   -> (float, dict)
    bornhuetter_ferguson(triangle, ult_a_priori) -> np.ndarray
    mack_stochastique(triangle)          -> dict
"""

import numpy as np

from . import config as cfg


# ---------------------------------------------------------------------------- #
def link_ratios(triangle):
    """
    Calcule les link ratios Chain-Ladder par approche volume-weighted average.

    Pour chaque transition j -> j+1 :
        f_j = sum_i C_{i, j+1} / sum_i C_{i, j}    pour les i ou les deux
                                                    cellules sont observees.

    Parameters
    ----------
    triangle : pd.DataFrame ou np.ndarray
        Triangle cumule avec NaN dans la partie non observee.

    Returns
    -------
    list of float
        Link ratios f_0, f_1, ..., f_{n-2}.
    """
    T = np.asarray(triangle, dtype=float)
    n_annees, n_dev = T.shape
    lr = []
    for j in range(n_dev - 1):
        mask = ~np.isnan(T[:, j]) & ~np.isnan(T[:, j + 1])
        if mask.sum() == 0:
            lr.append(1.0)
            continue
        num = T[mask, j + 1].sum()
        den = T[mask, j].sum()
        lr.append(num / den if den > 0 else 1.0)
    return lr


# ---------------------------------------------------------------------------- #
def projection_chain_ladder(triangle):
    """
    Projete le triangle aux cellules manquantes par Chain-Ladder vanille.

    Returns
    -------
    T_proj : np.ndarray
        Triangle complet projete (taille identique au triangle d'entree).
    lr : list of float
        Link ratios utilises pour la projection.
    """
    T = np.asarray(triangle, dtype=float).copy()
    n_annees, n_dev = T.shape
    lr = link_ratios(T)

    for i in range(n_annees):
        obs = np.where(~np.isnan(T[i, :]))[0]
        if len(obs) == 0:
            continue
        derniere = obs.max()
        for j in range(derniere, n_dev - 1):
            T[i, j + 1] = T[i, j] * lr[j]
    return T, lr


# ---------------------------------------------------------------------------- #
def facteur_queue_sherman(lr):
    """
    Ajustement exponentiel de Sherman (1984) sur les link ratios pour
    extrapoler le facteur de queue (developpement au-dela de la derniere
    colonne observee).

    Modele : ln(f_j - 1) = a + b * j

    Returns
    -------
    facteur_queue : float
        Facteur multiplicatif applique a l'Ultimate Chain-Ladder.
    diag : dict
        Diagnostic : {a, b, lr_extrapoles}
    """
    log_y = np.log(np.array(lr) - 1.0)
    x = np.arange(len(lr))
    # Regression lineaire simple manuelle (sans scipy)
    b = ((x - x.mean()) * (log_y - log_y.mean())).sum() \
        / ((x - x.mean()) ** 2).sum()
    a = log_y.mean() - b * x.mean()

    # Extrapolation des 3 link ratios suivants
    lr_extrap = [np.exp(a + b * j) + 1.0 for j in [4, 5, 6]]
    facteur = float(np.prod(lr_extrap))

    return facteur, {"a": float(a), "b": float(b),
                     "lr_extrapoles": [float(x) for x in lr_extrap]}


# ---------------------------------------------------------------------------- #
def bornhuetter_ferguson(triangle, ult_a_priori, ult_cl_avec_queue=None):
    """
    Methode Bornhuetter-Ferguson : melange a priori et observation.

        Ultimate_BF = Paiements_observes + (1 - %_developpe) * Ultimate_a_priori

    Le %_developpe est calcule a partir de l'Ultimate Chain-Ladder
    (avec facteur de queue si fourni) qui sert de reference.

    Parameters
    ----------
    triangle : pd.DataFrame ou np.ndarray
        Triangle cumule observe.
    ult_a_priori : np.ndarray
        Ultimate a priori par cohorte (S/P x Primes acquises).
    ult_cl_avec_queue : np.ndarray, optional
        Si fourni, sert de reference pour calculer le %_developpe.

    Returns
    -------
    ult_bf : np.ndarray
    """
    T = np.asarray(triangle, dtype=float)
    n_annees = T.shape[0]

    if ult_cl_avec_queue is None:
        T_proj, _ = projection_chain_ladder(T)
        ult_cl_avec_queue = T_proj[:, -1]

    ult_bf = np.zeros(n_annees)
    for i in range(n_annees):
        obs = np.where(~np.isnan(T[i, :]))[0]
        if len(obs) == 0:
            ult_bf[i] = ult_a_priori[i]
            continue
        derniere = obs.max()
        paiement = T[i, derniere]
        pct_dev = paiement / ult_cl_avec_queue[i] if ult_cl_avec_queue[i] > 0 else 1.0
        ult_bf[i] = paiement + (1 - pct_dev) * ult_a_priori[i]
    return ult_bf


# ---------------------------------------------------------------------------- #
def mack_stochastique(triangle):
    """
    Estimateur de la variance de prediction Mack (1993).

    Pour chaque cohorte i :
        MSEP_i = Ultimate_i^2 *
                 sum_{k=derniere_obs}^{n-2} [
                     (sigma_k^2 / f_k^2) * (1/C_{i,k} + 1/sum_C_k)
                 ]

    L'erreur standard SE_i = sqrt(MSEP_i).
    L'intervalle de confiance a 99,5 % : Ultimate +/- 2.576 * SE.

    Returns
    -------
    dict avec :
        - ultimate_cl
        - se               : erreurs standards
        - ic_inf, ic_sup   : bornes IC 99,5 %
        - sigma_k2         : variances par colonne
        - link_ratios
    """
    T = np.asarray(triangle, dtype=float)
    n_annees, n_dev = T.shape
    T_proj, lr = projection_chain_ladder(T)
    ult_cl = T_proj[:, -1]

    # Calcul des sigma_k^2
    sigma_k2 = np.zeros(n_dev - 1)
    for k in range(n_dev - 1):
        mask = ~np.isnan(T[:, k]) & ~np.isnan(T[:, k + 1])
        I_k = mask.sum()

        if I_k <= 1:
            # Extrapolation Mack 1993
            sigma_k2[k] = min(
                sigma_k2[k-1] ** 2 / max(sigma_k2[k-2], 1e-9),
                min(sigma_k2[k-1], sigma_k2[k-2])
            )
        else:
            f_ind = T[mask, k + 1] / T[mask, k]
            sigma_k2[k] = (T[mask, k] * (f_ind - lr[k]) ** 2).sum() / (I_k - 1)

    # Calcul du MSEP par cohorte
    msep = np.zeros(n_annees)
    for i in range(n_annees):
        obs = np.where(~np.isnan(T[i, :]))[0]
        if len(obs) == 0 or obs.max() == n_dev - 1:
            msep[i] = 0.0
            continue
        derniere = obs.max()
        somme = 0.0
        for k in range(derniere, n_dev - 1):
            mask = ~np.isnan(T[:, k]) & ~np.isnan(T[:, k + 1])
            sum_Ck = T[mask, k].sum()
            C_ik = T_proj[i, k]
            somme += (sigma_k2[k] / lr[k] ** 2) * (1 / C_ik + 1 / sum_Ck)
        msep[i] = ult_cl[i] ** 2 * somme

    se = np.sqrt(msep)
    # Quantile 99.5 % de la loi Normale standard
    z = 2.576
    return {
        "ultimate_cl":  ult_cl,
        "se":           se,
        "ic_inf":       ult_cl - z * se,
        "ic_sup":       ult_cl + z * se,
        "sigma_k2":     sigma_k2,
        "link_ratios":  lr,
    }
