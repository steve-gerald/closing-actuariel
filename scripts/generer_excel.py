"""
================================================================================
MODULE 6 — GENERATION DU CLASSEUR EXCEL DE PILOTAGE DU CLOSING
================================================================================

Produit un classeur Excel formate, structure en onglets standardises, qui
constitue le livrable de pilotage remis au management a chaque cloture :

    0. Synthese       : indicateurs cles + statut des controles
    1. Triangle       : triangle des paiements cumules
    2. Provisionnement : ultimate par methode + IBNR
    3. LAT_IFRS4      : test d'adequation par segment
    4. Boni_Mali      : run-off par cohorte et segment
    5. Compte_Technique : P&L technique + ratios
    6. Controles      : journal des controles de coherence

Les ratios et totaux sont des FORMULES Excel vivantes (pas des valeurs figees),
afin que le classeur se recalcule si les donnees source changent.
================================================================================
"""

import os
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DIR_PROC = os.path.join(REPO, "data", "processed")
DIR_OUT  = os.path.join(REPO, "outputs")

# --- Palette et styles ------------------------------------------------------ #
POLICE      = "Arial"
BLEU_FONCE  = "1F3864"
BLEU_MOYEN  = "2E5496"
BLEU_CLAIR  = "D6E0F0"
GRIS_CLAIR  = "F2F2F2"
VERT        = "C6EFCE"
ROUGE       = "FFC7CE"
JAUNE       = "FFF2CC"

f_titre   = Font(name=POLICE, size=14, bold=True, color="FFFFFF")
f_entete  = Font(name=POLICE, size=10, bold=True, color="FFFFFF")
f_normal  = Font(name=POLICE, size=10)
f_gras    = Font(name=POLICE, size=10, bold=True)
f_total   = Font(name=POLICE, size=10, bold=True, color="FFFFFF")

fill_titre  = PatternFill("solid", fgColor=BLEU_FONCE)
fill_entete = PatternFill("solid", fgColor=BLEU_MOYEN)
fill_total  = PatternFill("solid", fgColor=BLEU_MOYEN)
fill_clair  = PatternFill("solid", fgColor=BLEU_CLAIR)
fill_gris   = PatternFill("solid", fgColor=GRIS_CLAIR)
fill_vert   = PatternFill("solid", fgColor=VERT)
fill_rouge  = PatternFill("solid", fgColor=ROUGE)
fill_jaune  = PatternFill("solid", fgColor=JAUNE)

bord_fin = Border(*[Side(style="thin", color="BFBFBF")] * 4)
centre   = Alignment(horizontal="center", vertical="center")
gauche   = Alignment(horizontal="left", vertical="center")
droite   = Alignment(horizontal="right", vertical="center")

FMT_EUR = '#,##0 "€";(#,##0) "€";"-"'
FMT_PCT = '0.0%'


def style_entete(ws, ligne, n_cols, debut_col=1):
    for c in range(debut_col, debut_col + n_cols):
        cell = ws.cell(row=ligne, column=c)
        cell.font = f_entete
        cell.fill = fill_entete
        cell.alignment = centre
        cell.border = bord_fin


def titre_onglet(ws, texte, n_cols):
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=n_cols)
    cell = ws.cell(row=1, column=1, value=texte)
    cell.font = f_titre
    cell.fill = fill_titre
    cell.alignment = centre
    ws.row_dimensions[1].height = 24


# ---------------------------------------------------------------------------- #
# CHARGEMENT DES DONNEES
# ---------------------------------------------------------------------------- #

triangle    = pd.read_csv(os.path.join(DIR_PROC, "triangle_paiements_cumules.csv"))
m2_synthese = pd.read_csv(os.path.join(DIR_PROC, "m2_synthese_provisionnement.csv"))
m2_ibnr     = pd.read_csv(os.path.join(DIR_PROC, "m2_IBNR.csv"))
m3_lat      = pd.read_csv(os.path.join(DIR_PROC, "m3_liability_adequacy_test.csv"))
m4_global   = pd.read_csv(os.path.join(DIR_PROC, "m4_boni_mali_global.csv"))
m4_seg      = pd.read_csv(os.path.join(DIR_PROC, "m4_boni_mali_par_segment.csv"),
                          index_col=0)
m5_compte   = pd.read_csv(os.path.join(DIR_PROC, "m5_compte_technique.csv"))
m6_journal  = pd.read_csv(os.path.join(DIR_PROC, "m6_journal_controles.csv"))

wb = Workbook()


# ============================================================================ #
# ONGLET 0 — SYNTHESE
# ============================================================================ #

ws = wb.active
ws.title = "0_Synthese"
titre_onglet(ws, "PILOTAGE DU CLOSING — SYNTHESE (exercice 2025)", 4)

ws["A3"] = "Indicateur clé"
ws["B3"] = "Valeur"
style_entete(ws, 3, 2)

# Indicateurs (on reference les autres onglets via formules)
indics = [
    ("Primes acquises (€)",         "='5_Compte_Technique'!E5"),
    ("Charge sinistres courant (€)","='5_Compte_Technique'!E6"),
    ("Boni-mali exercices antérieurs (€)", "='5_Compte_Technique'!E7"),
    ("Résultat technique net (€)",  "='5_Compte_Technique'!E13"),
    ("Ratio S/P comptable",         "='5_Compte_Technique'!E16"),
    ("Ratio combiné",               "='5_Compte_Technique'!E18"),
    ("PSAP - sinistres à payer (€)","=SUM('2_Provisionnement'!F4:F8)"),
    ("UPR - primes non acquises (€)","='3_LAT_IFRS4'!B6"),
    ("URR - risque en cours (€)",   "='3_LAT_IFRS4'!F6"),
]
ligne = 4
for libelle, formule in indics:
    ws.cell(row=ligne, column=1, value=libelle).font = f_normal
    c = ws.cell(row=ligne, column=2, value=formule)
    c.font = f_gras
    if "Ratio" in libelle:
        c.number_format = FMT_PCT
    else:
        c.number_format = FMT_EUR
    ws.cell(row=ligne, column=1).border = bord_fin
    c.border = bord_fin
    ws.cell(row=ligne, column=1).fill = fill_gris if ligne % 2 == 0 else PatternFill()
    ligne += 1

# Statut des controles
ligne += 1
ws.cell(row=ligne, column=1, value="STATUT DES CONTRÔLES").font = f_gras
ligne += 1
ws.cell(row=ligne, column=1, value="Nombre de contrôles")
ws.cell(row=ligne, column=2, value="=COUNTA('6_Controles'!A5:A20)").font = f_gras
ligne += 1
ws.cell(row=ligne, column=1, value="Alertes")
c_alerte = ws.cell(row=ligne, column=2,
                   value='=COUNTIF(\'6_Controles\'!B5:B20,"ALERTE")')
c_alerte.font = f_gras
c_alerte.fill = fill_jaune

ws.column_dimensions["A"].width = 38
ws.column_dimensions["B"].width = 20


# ============================================================================ #
# ONGLET 1 — TRIANGLE
# ============================================================================ #

ws = wb.create_sheet("1_Triangle")
titre_onglet(ws, "TRIANGLE DES PAIEMENTS CUMULES (€)", triangle.shape[1] + 1)

# Entetes
ws.cell(row=3, column=1, value="Année survenance")
for j, col in enumerate(triangle.columns[1:], start=2):
    ws.cell(row=3, column=j, value=f"Dev {col}")
style_entete(ws, 3, triangle.shape[1])

for i, (_, row) in enumerate(triangle.iterrows(), start=4):
    ws.cell(row=i, column=1, value=int(row.iloc[0])).font = f_gras
    ws.cell(row=i, column=1).fill = fill_clair
    for j, val in enumerate(row.iloc[1:], start=2):
        c = ws.cell(row=i, column=j)
        if pd.notna(val):
            c.value = float(val)
            c.number_format = FMT_EUR
        c.font = f_normal
        c.border = bord_fin

ws.column_dimensions["A"].width = 16
for j in range(2, triangle.shape[1] + 1):
    ws.column_dimensions[get_column_letter(j)].width = 14


# ============================================================================ #
# ONGLET 2 — PROVISIONNEMENT
# ============================================================================ #

ws = wb.create_sheet("2_Provisionnement")
titre_onglet(ws, "PROVISIONNEMENT — ULTIMATE PAR METHODE", 6)

entetes = ["Année", "Ultimate vrai", "Chain-Ladder", "CL + queue", "BF", "IBNR (BF)"]
for j, h in enumerate(entetes, start=1):
    ws.cell(row=3, column=j, value=h)
style_entete(ws, 3, 6)

for i, (_, row) in enumerate(m2_synthese.iterrows(), start=4):
    ws.cell(row=i, column=1, value=int(row["Annee"])).font = f_gras
    ws.cell(row=i, column=1).fill = fill_clair
    valeurs = [row["Ultimate_vrai"], row["CL_sans_queue"],
               row["CL_avec_queue"], row["BF"]]
    for j, v in enumerate(valeurs, start=2):
        c = ws.cell(row=i, column=j, value=float(v))
        c.number_format = FMT_EUR
        c.font = f_normal
        c.border = bord_fin
    # IBNR = BF - paiements observes (formule vivante : on prend depuis m2_ibnr)
    ibnr_val = m2_ibnr.iloc[i-4]["IBNR_BF"]
    c = ws.cell(row=i, column=6, value=float(ibnr_val))
    c.number_format = FMT_EUR
    c.font = f_normal
    c.border = bord_fin

# Ligne TOTAL avec formules
ligne_tot = 4 + len(m2_synthese)
ws.cell(row=ligne_tot, column=1, value="TOTAL").font = f_total
ws.cell(row=ligne_tot, column=1).fill = fill_total
for j in range(2, 7):
    col = get_column_letter(j)
    c = ws.cell(row=ligne_tot, column=j,
                value=f"=SUM({col}4:{col}{ligne_tot-1})")
    c.number_format = FMT_EUR
    c.font = f_total
    c.fill = fill_total

ws.column_dimensions["A"].width = 10
for j in range(2, 7):
    ws.column_dimensions[get_column_letter(j)].width = 15


# ============================================================================ #
# ONGLET 3 — LAT IFRS 4
# ============================================================================ #

ws = wb.create_sheet("3_LAT_IFRS4")
titre_onglet(ws, "LIABILITY ADEQUACY TEST (IFRS 4)", 7)

entetes = ["Segment", "UPR brut", "DAC", "UPR net",
           "Best Estimate", "URR", "Test"]
for j, h in enumerate(entetes, start=1):
    ws.cell(row=3, column=j, value=h)
style_entete(ws, 3, 7)

for i, (_, row) in enumerate(m3_lat.iterrows(), start=4):
    ws.cell(row=i, column=1, value=row["Segment"]).font = f_gras
    ws.cell(row=i, column=1).fill = fill_clair
    # UPR brut et best estimate en valeurs ; UPR net et URR en formules
    ws.cell(row=i, column=2, value=float(row["UPR_brut"])).number_format = FMT_EUR
    ws.cell(row=i, column=3, value=float(row["DAC"])).number_format = FMT_EUR
    # UPR net = UPR brut - DAC (formule)
    ws.cell(row=i, column=4, value=f"=B{i}-C{i}").number_format = FMT_EUR
    ws.cell(row=i, column=5, value=float(row["Best_Estimate"])).number_format = FMT_EUR
    # URR = max(BE - UPR net ; 0) (formule)
    ws.cell(row=i, column=6, value=f"=MAX(E{i}-D{i},0)").number_format = FMT_EUR
    # Test (formule conditionnelle)
    c_test = ws.cell(row=i, column=7, value=f'=IF(F{i}>0,"DEFICIENCY","OK")')
    c_test.alignment = centre
    if row["Resultat_test"] == "DEFICIENCY":
        c_test.fill = fill_rouge
    else:
        c_test.fill = fill_vert
    for j in range(1, 8):
        ws.cell(row=i, column=j).font = f_normal
        ws.cell(row=i, column=j).border = bord_fin

# Ligne TOTAL
ligne_tot = 4 + len(m3_lat)
ws.cell(row=ligne_tot, column=1, value="TOTAL").font = f_total
ws.cell(row=ligne_tot, column=1).fill = fill_total
for j in [2, 3, 4, 5, 6]:
    col = get_column_letter(j)
    c = ws.cell(row=ligne_tot, column=j,
                value=f"=SUM({col}4:{col}{ligne_tot-1})")
    c.number_format = FMT_EUR
    c.font = f_total
    c.fill = fill_total

ws.column_dimensions["A"].width = 12
for j in range(2, 8):
    ws.column_dimensions[get_column_letter(j)].width = 15


# ============================================================================ #
# ONGLET 4 — BONI-MALI
# ============================================================================ #

ws = wb.create_sheet("4_Boni_Mali")
titre_onglet(ws, "ANALYSE BONI-MALI (run-off 2024 -> 2025)", 4)

# Tableau par cohorte
ws.cell(row=3, column=1, value="Par année de survenance").font = f_gras
entetes = ["Année", "Ultimate 2024", "Ultimate 2025", "Boni-mali"]
for j, h in enumerate(entetes, start=1):
    ws.cell(row=4, column=j, value=h)
style_entete(ws, 4, 4)

for i, (_, row) in enumerate(m4_global.iterrows(), start=5):
    ws.cell(row=i, column=1, value=int(row["Annee_survenance"])).font = f_gras
    ws.cell(row=i, column=1).fill = fill_clair
    ws.cell(row=i, column=2,
            value=float(row["Ultimate_cloture_2024"])).number_format = FMT_EUR
    ws.cell(row=i, column=3,
            value=float(row["Ultimate_cloture_2025"])).number_format = FMT_EUR
    # Boni-mali = Ult 2024 - Ult 2025 (formule)
    c = ws.cell(row=i, column=4, value=f"=B{i}-C{i}")
    c.number_format = FMT_EUR
    if row["Boni_mali"] < 0:
        c.fill = fill_rouge
    else:
        c.fill = fill_vert
    for j in range(1, 5):
        ws.cell(row=i, column=j).font = f_normal
        ws.cell(row=i, column=j).border = bord_fin

ligne_tot = 5 + len(m4_global)
ws.cell(row=ligne_tot, column=1, value="TOTAL").font = f_total
ws.cell(row=ligne_tot, column=1).fill = fill_total
for j in [2, 3, 4]:
    col = get_column_letter(j)
    c = ws.cell(row=ligne_tot, column=j,
                value=f"=SUM({col}5:{col}{ligne_tot-1})")
    c.number_format = FMT_EUR
    c.font = f_total
    c.fill = fill_total

ws.column_dimensions["A"].width = 10
for j in range(2, 5):
    ws.column_dimensions[get_column_letter(j)].width = 16


# ============================================================================ #
# ONGLET 5 — COMPTE TECHNIQUE
# ============================================================================ #

ws = wb.create_sheet("5_Compte_Technique")
titre_onglet(ws, "COMPTE TECHNIQUE NON-VIE (exercice 2025)", 5)

# On reconstruit le compte avec FLOTTE / PART / TOTAL en colonnes
ws.cell(row=3, column=1, value="Poste").font = f_entete
ws.cell(row=3, column=1).fill = fill_entete
cols_seg = ["FLOTTE", "PART", "TOTAL"]
# colonnes C, D, E
for idx, seg in enumerate(cols_seg):
    c = ws.cell(row=3, column=3 + idx, value=seg)
    c.font = f_entete
    c.fill = fill_entete
    c.alignment = centre
ws.cell(row=3, column=2, value="").fill = fill_entete

# Donnees par poste : (libelle, cle dans m5_compte, format)
postes = [
    ("(+) Primes acquises",          "Primes_acquises"),
    ("(-) Charge sinistres courant", "Charge_courant"),
    ("(+/-) Boni-mali antérieurs",   "Boni_mali"),
    ("(-) Frais d'acquisition",      "Frais_acquisition"),
    ("(-) Frais de gestion",         "Frais_gestion"),
]

def val_seg(cle, seg):
    return float(m5_compte.loc[m5_compte["Segment"] == seg, cle].values[0])

ligne = 5
for libelle, cle in postes:
    ws.cell(row=ligne, column=1, value=libelle).font = f_normal
    for idx, seg in enumerate(["FLOTTE", "PART"]):
        c = ws.cell(row=ligne, column=3 + idx, value=val_seg(cle, seg))
        c.number_format = FMT_EUR
        c.font = f_normal
    # TOTAL = FLOTTE + PART (formule)
    c = ws.cell(row=ligne, column=5, value=f"=C{ligne}+D{ligne}")
    c.number_format = FMT_EUR
    c.font = f_gras
    ligne += 1

# Resultat technique brut = primes - charge - boni-mali deja en signe - frais
# On calcule : primes(5) - charge(6) + bonimali(7) - frais_acq(8) - frais_gest(9)
# Attention au signe du boni-mali : negatif = mali, donc on l'ajoute (il reduit)
ligne_brut = ligne
ws.cell(row=ligne_brut, column=1, value="(=) Résultat technique BRUT").font = f_gras
for col in ["C", "D", "E"]:
    c = ws.cell(row=ligne_brut, column={"C":3,"D":4,"E":5}[col],
                value=f"={col}5-{col}6+{col}7-{col}8-{col}9")
    c.number_format = FMT_EUR
    c.font = f_gras
    c.fill = fill_gris
ligne += 1

# Reassurance (valeurs depuis m5)
ws.cell(row=ligne, column=1, value="(-) Prime réass. cédée").font = f_normal
for idx, seg in enumerate(["FLOTTE", "PART"]):
    ws.cell(row=ligne, column=3+idx,
            value=val_seg("Prime_reass_cedee", seg)).number_format = FMT_EUR
ws.cell(row=ligne, column=5, value=f"=C{ligne}+D{ligne}").number_format = FMT_EUR
ligne_prime_reass = ligne
ligne += 1

ws.cell(row=ligne, column=1, value="(+) Récupérations réass.").font = f_normal
for idx, seg in enumerate(["FLOTTE", "PART"]):
    ws.cell(row=ligne, column=3+idx,
            value=val_seg("Recup_reass", seg)).number_format = FMT_EUR
ws.cell(row=ligne, column=5, value=f"=C{ligne}+D{ligne}").number_format = FMT_EUR
ligne_recup = ligne
ligne += 1

# Resultat net = brut - prime reass + recup
ligne_net = ligne
ws.cell(row=ligne_net, column=1, value="(=) Résultat technique NET").font = f_total
ws.cell(row=ligne_net, column=1).fill = fill_total
for col, cidx in [("C",3),("D",4),("E",5)]:
    c = ws.cell(row=ligne_net, column=cidx,
                value=f"={col}{ligne_brut}-{col}{ligne_prime_reass}+{col}{ligne_recup}")
    c.number_format = FMT_EUR
    c.font = f_total
    c.fill = fill_total
ligne += 2

# Ratios
ws.cell(row=ligne, column=1, value="RATIOS DE PILOTAGE").font = f_gras
ligne += 1
ligne_sp = ligne
ws.cell(row=ligne, column=1, value="S/P comptable").font = f_normal
for col, cidx in [("C",3),("D",4),("E",5)]:
    # (charge courant - bonimali) / primes
    c = ws.cell(row=ligne, column=cidx, value=f"=({col}6-{col}7)/{col}5")
    c.number_format = FMT_PCT
    c.font = f_normal
ligne += 1
ligne_frais = ligne
ws.cell(row=ligne, column=1, value="Ratio de frais").font = f_normal
for col, cidx in [("C",3),("D",4),("E",5)]:
    c = ws.cell(row=ligne, column=cidx, value=f"=({col}8+{col}9)/{col}5")
    c.number_format = FMT_PCT
    c.font = f_normal
ligne += 1
ws.cell(row=ligne, column=1, value="RATIO COMBINE").font = f_gras
for col, cidx in [("C",3),("D",4),("E",5)]:
    c = ws.cell(row=ligne, column=cidx, value=f"={col}{ligne_sp}+{col}{ligne_frais}")
    c.number_format = FMT_PCT
    c.font = f_gras
    # mise en couleur conditionnelle
    val_combine = val_seg("Ratio_combine", "TOTAL" if col=="E" else ("FLOTTE" if col=="C" else "PART"))
    c.fill = fill_rouge if val_combine >= 1.0 else fill_vert

# bordures generales
for r in range(3, ligne+1):
    for c in range(1, 6):
        ws.cell(row=r, column=c).border = bord_fin

ws.column_dimensions["A"].width = 30
ws.column_dimensions["B"].width = 3
for col in ["C", "D", "E"]:
    ws.column_dimensions[col].width = 15


# ============================================================================ #
# ONGLET 6 — CONTROLES
# ============================================================================ #

ws = wb.create_sheet("6_Controles")
titre_onglet(ws, "JOURNAL DES CONTROLES DE COHERENCE", 3)

entetes = ["Contrôle", "Statut", "Détail"]
for j, h in enumerate(entetes, start=1):
    ws.cell(row=4, column=j, value=h)
style_entete(ws, 4, 3)

for i, (_, row) in enumerate(m6_journal.iterrows(), start=5):
    ws.cell(row=i, column=1, value=row["Controle"]).font = f_normal
    c_statut = ws.cell(row=i, column=2, value=row["Statut"])
    c_statut.alignment = centre
    c_statut.fill = fill_vert if row["Statut"] == "OK" else fill_jaune
    c_statut.font = f_gras
    ws.cell(row=i, column=3, value=row["Detail"]).font = f_normal
    for j in range(1, 4):
        ws.cell(row=i, column=j).border = bord_fin

ws.column_dimensions["A"].width = 48
ws.column_dimensions["B"].width = 12
ws.column_dimensions["C"].width = 60


# ============================================================================ #
# SAUVEGARDE
# ============================================================================ #

chemin = os.path.join(DIR_OUT, "closing_pilotage_2025.xlsx")
wb.save(chemin)
print(f"     -> Classeur Excel : {chemin}")
