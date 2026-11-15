"""
Génère les 5 figures matplotlib à partir des CSV produits par le pipeline.

Usage :
    python scripts/generer_figures.py

Prérequis : `python -m closing.run` doit avoir été exécuté préalablement
pour produire les CSV dans data/raw/ et data/processed/.
"""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DIR_RAW  = os.path.join(REPO, "data", "raw")
DIR_PROC = os.path.join(REPO, "data", "processed")
DIR_OUT  = os.path.join(REPO, "outputs")
os.makedirs(DIR_OUT, exist_ok=True)

# Charger les donnees
df_sinistres = pd.read_csv(os.path.join(DIR_RAW, "sinistres.csv"))
df_paiements = pd.read_csv(os.path.join(DIR_RAW, "paiements.csv"))
triangle = pd.read_csv(os.path.join(DIR_PROC, "triangle_paiements_cumules.csv"),
                       index_col="annee_survenance")
ult_vrai = pd.read_csv(os.path.join(DIR_PROC, "ultimate_vrai_par_annee.csv"),
                       index_col="annee_survenance")["ultimate_vrai_total"]
df_synthese = pd.read_csv(os.path.join(DIR_PROC, "m2_synthese_provisionnement.csv"))
df_lat      = pd.read_csv(os.path.join(DIR_PROC, "m3_liability_adequacy_test.csv"))
df_prov     = pd.read_csv(os.path.join(DIR_PROC, "m3_provisions_techniques_totales.csv"))
df_bm       = pd.read_csv(os.path.join(DIR_PROC, "m4_boni_mali_global.csv"))
df_bm_seg   = pd.read_csv(os.path.join(DIR_PROC, "m4_boni_mali_par_segment.csv"),
                          index_col=0)
df_compte   = pd.read_csv(os.path.join(DIR_PROC, "m5_compte_technique.csv"))


# ============================================================================ #
# Figure 1 - Validation du portefeuille (4 panels)
# ============================================================================ #

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle("Module 1 — Validation visuelle du portefeuille MTPL simulé",
             fontsize=14, fontweight="bold")

ax = axes[0, 0]
for garantie, couleur in [("MATERIEL", "steelblue"), ("CORPOREL", "darkred")]:
    valeurs = df_sinistres.loc[df_sinistres["garantie"] == garantie, "ultimate_vrai"]
    ax.hist(valeurs, bins=60, range=(0, 50_000), alpha=0.6, color=couleur,
            label=f"{garantie} (n={len(valeurs):,})".replace(",", " "))
ax.set_xlabel("Ultimate vrai (€)"); ax.set_ylabel("Nombre de sinistres")
ax.set_title("(a) Distribution des sinistres par garantie")
ax.legend(); ax.grid(alpha=0.3)

ax = axes[0, 1]
data = triangle.values / 1e6
im = ax.imshow(data, aspect="auto", cmap="YlOrRd")
ax.set_xticks(range(triangle.shape[1])); ax.set_xticklabels(triangle.columns)
ax.set_yticks(range(triangle.shape[0])); ax.set_yticklabels(triangle.index)
ax.set_xlabel("Année de développement"); ax.set_ylabel("Année de survenance")
ax.set_title("(b) Triangle des paiements cumulés (M€)")
for i in range(data.shape[0]):
    for j in range(data.shape[1]):
        if not np.isnan(data[i, j]):
            ax.text(j, i, f"{data[i, j]:.2f}", ha="center", va="center",
                    color="black", fontsize=9)
plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

ax = axes[1, 0]
df_2021 = df_paiements[df_paiements["annee_survenance"] == 2021]
for garantie, couleur in [("MATERIEL", "steelblue"), ("CORPOREL", "darkred")]:
    p = (df_2021[df_2021["garantie"] == garantie]
         .groupby("annee_developpement")["paiement_incremental"].sum()
         .reindex(range(5), fill_value=0.0))
    pct = p.cumsum() / p.sum()
    ax.plot(pct.index, pct.values, "o-", color=couleur, label=garantie, linewidth=2)
ax.set_xlabel("Année de développement"); ax.set_ylabel("% Ultimate cumulé payé")
ax.set_title("(c) Vitesse de développement (cohorte 2021)")
ax.set_ylim(0, 1.05); ax.grid(alpha=0.3); ax.legend()

ax = axes[1, 1]
paiements_obs = df_paiements.groupby("annee_survenance")["paiement_incremental"].sum()
indices = ult_vrai.index.tolist()
largeur = 0.35; positions = np.arange(len(indices))
ax.bar(positions - largeur/2, ult_vrai.values / 1e6, largeur,
       color="indianred", label="Ultimate vrai")
ax.bar(positions + largeur/2, paiements_obs.values / 1e6, largeur,
       color="steelblue", label="Paiements observés")
ax.set_xticks(positions); ax.set_xticklabels(indices)
ax.set_xlabel("Année de survenance"); ax.set_ylabel("Montant (M€)")
ax.set_title("(d) Ultimate vrai vs paiements observés")
ax.legend(); ax.grid(alpha=0.3, axis="y")
ecart = (ult_vrai.sum() - paiements_obs.sum()) / 1e6
ax.text(0.02, 0.95, f"Écart à provisionner : {ecart:.1f} M€",
        transform=ax.transAxes, fontsize=10,
        bbox=dict(boxstyle="round", facecolor="lightyellow", alpha=0.8),
        verticalalignment="top")

plt.tight_layout()
plt.savefig(os.path.join(DIR_OUT, "m1_validation_portefeuille.png"),
            dpi=120, bbox_inches="tight")
plt.close()
print(f"  -> m1_validation_portefeuille.png")


# ============================================================================ #
# Figure 2 - Provisionnement
# ============================================================================ #

fig, axes = plt.subplots(1, 2, figsize=(15, 6))
fig.suptitle("Module 2 — Comparaison des méthodes de provisionnement",
             fontsize=14, fontweight="bold")

ax = axes[0]
largeur = 0.2; positions = np.arange(len(df_synthese))
ax.bar(positions - 1.5*largeur, df_synthese["Ultimate_vrai"] / 1e6, largeur,
       color="indianred", label="Vérité terrain")
ax.bar(positions - 0.5*largeur, df_synthese["CL_sans_queue"] / 1e6, largeur,
       color="steelblue", label="Chain-Ladder vanille")
ax.bar(positions + 0.5*largeur, df_synthese["CL_avec_queue"] / 1e6, largeur,
       color="navy", label="CL + queue")
ax.bar(positions + 1.5*largeur, df_synthese["BF"] / 1e6, largeur,
       color="seagreen", label="Bornhuetter-Ferguson")
ax.set_xticks(positions); ax.set_xticklabels(df_synthese["Annee"])
ax.set_xlabel("Année de survenance"); ax.set_ylabel("Ultimate (M€)")
ax.set_title("(a) Ultimate par méthode vs vérité terrain")
ax.legend(loc="upper left", fontsize=9); ax.grid(alpha=0.3, axis="y")

ax = axes[1]
z = 2.576
yerr = (z * df_synthese["Mack_SE"]) / 1e6
ax.errorbar(positions, df_synthese["CL_sans_queue"] / 1e6, yerr=yerr,
            fmt="o", color="steelblue", markersize=8, capsize=8, capthick=2,
            linewidth=2, label="CL ± IC 99,5 % (Mack)")
ax.plot(positions, df_synthese["Ultimate_vrai"] / 1e6, "x", color="indianred",
        markersize=12, markeredgewidth=3, label="Vérité terrain")
ax.set_xticks(positions); ax.set_xticklabels(df_synthese["Annee"])
ax.set_xlabel("Année de survenance"); ax.set_ylabel("Ultimate (M€)")
ax.set_title("(b) Mack stochastique — IC 99,5 %")
ax.legend(); ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(DIR_OUT, "m2_comparaison_methodes.png"),
            dpi=120, bbox_inches="tight")
plt.close()
print(f"  -> m2_comparaison_methodes.png")


# ============================================================================ #
# Figure 3 - LAT
# ============================================================================ #

fig, axes = plt.subplots(1, 2, figsize=(15, 6))
fig.suptitle("Module 3 — Liability Adequacy Test (IFRS 4)",
             fontsize=14, fontweight="bold")

ax = axes[0]
segs = df_lat["Segment"].tolist()
positions = np.arange(len(segs)); largeur = 0.35
ax.bar(positions - largeur/2, df_lat["UPR_net"] / 1e6, largeur,
       color="steelblue", label="UPR net de DAC")
ax.bar(positions + largeur/2, df_lat["Best_Estimate"] / 1e6, largeur,
       color="indianred", label="Best Estimate")
for i, r in df_lat.iterrows():
    couleur = "green" if r["Resultat_test"] == "OK" else "red"
    ax.text(i, max(r["UPR_net"], r["Best_Estimate"]) / 1e6 + 0.05,
            r["Resultat_test"], ha="center", fontweight="bold",
            color=couleur, fontsize=11)
ax.set_xticks(positions); ax.set_xticklabels(segs)
ax.set_ylabel("Montant (M€)")
ax.set_title("(a) Test d'adéquation par segment")
ax.legend(); ax.grid(alpha=0.3, axis="y")

ax = axes[1]
labels = ["PSAP\n(sinistres)", "UPR\n(primes\nnon acquises)", "URR\n(risque\nen cours)"]
montants = df_prov[df_prov["Provision"] != "TOTAL"]["Montant"].values / 1e6
couleurs = ["darkslateblue", "steelblue", "crimson"]
barres = ax.bar(labels, montants, color=couleurs)
for b, m in zip(barres, montants):
    ax.text(b.get_x() + b.get_width()/2, b.get_height() + 0.05,
            f"{m:.2f} M€", ha="center", fontweight="bold")
ax.set_ylabel("Montant (M€)")
ax.set_title(f"(b) Provisions techniques totales : "
             f"{df_prov[df_prov['Provision']=='TOTAL']['Montant'].values[0]/1e6:.2f} M€")
ax.grid(alpha=0.3, axis="y")

plt.tight_layout()
plt.savefig(os.path.join(DIR_OUT, "m3_liability_adequacy_test.png"),
            dpi=120, bbox_inches="tight")
plt.close()
print(f"  -> m3_liability_adequacy_test.png")


# ============================================================================ #
# Figure 4 - Boni-mali
# ============================================================================ #

fig, axes = plt.subplots(1, 2, figsize=(15, 6))
fig.suptitle("Module 4 — Analyse boni-mali (run-off 2024 → 2025)",
             fontsize=14, fontweight="bold")

ax = axes[0]
annees = df_bm["Annee_survenance"].tolist()
valeurs = df_bm["Boni_mali"].values / 1e3
couleurs = ["seagreen" if v > 0 else "indianred" for v in valeurs]
barres = ax.bar(range(len(annees)), valeurs, color=couleurs)
ax.axhline(0, color="black", linewidth=0.8)
for i, (b, v) in enumerate(zip(barres, valeurs)):
    offset = 5 if v > 0 else -15
    ax.text(i, v + offset, f"{v:+.0f}k", ha="center", fontweight="bold", fontsize=9)
ax.set_xticks(range(len(annees))); ax.set_xticklabels(annees)
ax.set_xlabel("Année de survenance"); ax.set_ylabel("Boni-mali (k€)")
ax.set_title("(a) Boni-mali par année de survenance")
ax.grid(alpha=0.3, axis="y")

ax = axes[1]
cohortes = [c for c in df_bm_seg.columns if c != "TOTAL"]
largeur = 0.35; positions = np.arange(len(cohortes))
segments = list(df_bm_seg.index)
for idx, seg in enumerate(segments):
    vals = [df_bm_seg.loc[seg, c] / 1e3 for c in cohortes]
    decalage = (idx - (len(segments) - 1) / 2) * largeur
    ax.bar(positions + decalage, vals, largeur, label=seg)
ax.axhline(0, color="black", linewidth=0.8)
ax.set_xticks(positions); ax.set_xticklabels(cohortes)
ax.set_xlabel("Année de survenance"); ax.set_ylabel("Boni-mali (k€)")
ax.set_title("(b) Boni-mali par segment et année")
ax.legend(); ax.grid(alpha=0.3, axis="y")

plt.tight_layout()
plt.savefig(os.path.join(DIR_OUT, "m4_boni_mali.png"),
            dpi=120, bbox_inches="tight")
plt.close()
print(f"  -> m4_boni_mali.png")


# ============================================================================ #
# Figure 5 - Compte technique
# ============================================================================ #

fig, ax = plt.subplots(figsize=(11, 6))
fig.suptitle("Module 5 — Ratio combiné par segment (exercice 2025)",
             fontsize=14, fontweight="bold")

segs_plot = df_compte["Segment"].tolist()
positions = np.arange(len(segs_plot))
sp = df_compte["SP_comptable"].values * 100
fr = df_compte["Ratio_frais"].values * 100

ax.bar(positions, sp, color="indianred", label="S/P comptable")
ax.bar(positions, fr, bottom=sp, color="steelblue", label="Ratio de frais")
ax.axhline(100, color="black", linestyle="--", linewidth=1.5,
           label="Seuil de rentabilité")
for i, s in enumerate(segs_plot):
    combine = sp[i] + fr[i]
    couleur = "green" if combine < 100 else "red"
    ax.text(i, combine + 1.5, f"{combine:.1f}%", ha="center",
            fontweight="bold", color=couleur)
ax.set_xticks(positions); ax.set_xticklabels(segs_plot)
ax.set_ylabel("Ratio combiné (%)")
ax.legend(loc="upper left", fontsize=9); ax.grid(alpha=0.3, axis="y")

plt.tight_layout()
plt.savefig(os.path.join(DIR_OUT, "m5_resultat_technique.png"),
            dpi=120, bbox_inches="tight")
plt.close()
print(f"  -> m5_resultat_technique.png")

print("\n  5 figures generees dans outputs/")
