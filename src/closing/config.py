"""
Hyperparamètres centralisés du pipeline de clôture.

Tous les paramètres sensibles (graine aléatoire, taux de frais, seuils
d'alerte, hypothèses actuarielles) sont rassemblés ici afin de garantir
la reproductibilité et de faciliter la révision par un actuaire réviseur.

En production, ce fichier serait versionné sous Git pour tracer l'évolution
des hypothèses entre clôtures successives.
"""

# ============================================================================ #
# REPRODUCTIBILITE
# ============================================================================ #

SEED = 20260527   # graine du generateur aleatoire (reproductibilite)


# ============================================================================ #
# PERIMETRE TEMPOREL
# ============================================================================ #

ANNEES_SURVENANCE = [2021, 2022, 2023, 2024, 2025]
ANNEE_CLOTURE     = 2025
N_ANNEES_DEV_MAX  = 5


# ============================================================================ #
# VOLUMETRIE DU PORTEFEUILLE
# ============================================================================ #

POLICES_PAR_ANNEE = {
    2021:  9_000,
    2022:  9_500,
    2023: 10_000,
    2024: 10_500,
    2025: 11_000,
}

# Mix segments
PART_PART   = 0.80   # Particuliers
PART_FLOTTE = 0.20   # Flottes

# Mix garanties
PART_MATERIEL = 0.85
PART_CORPOREL = 0.15


# ============================================================================ #
# HYPOTHESES ACTUARIELLES (sinistralite)
# ============================================================================ #

# Frequence Poisson annuelle par segment
FREQ_PART   = 0.06
FREQ_FLOTTE = 0.10

# Severite Lognormale par garantie
SEV_MAT_MU,    SEV_MAT_SIGMA    = 7.5, 0.8    # mediane ~1 800 €
SEV_CORP_MU,   SEV_CORP_SIGMA   = 9.0, 1.4    # mediane ~8 100 €, queue epaisse

# Primes annuelles par segment (loi Lognormale)
PRIME_PART_MOY,   PRIME_PART_CV   = 480,   0.20
PRIME_FLOTTE_MOY, PRIME_FLOTTE_CV = 1_350, 0.25

# Patterns de paiement cumules (% de l'Ultimate par annee de dev)
PATTERN_MATERIEL = [0.70, 0.92, 0.98, 1.00, 1.00]   # court-tail
PATTERN_CORPOREL = [0.20, 0.45, 0.65, 0.80, 0.88]   # long-tail (queue 12%)

# Inflation annuelle des couts
INFLATION_ANNUELLE = 0.025


# ============================================================================ #
# PROVISIONNEMENT (M2)
# ============================================================================ #

SP_A_PRIORI_BF      = 0.60    # S/P a priori pour Bornhuetter-Ferguson
NIVEAU_CONFIANCE    = 0.995   # Solvabilite II


# ============================================================================ #
# LAT IFRS 4 (M3)
# ============================================================================ #

TAUX_FRAIS_ACQUISITION = 0.15   # commissions reportees -> DAC
TAUX_FRAIS_GESTION     = 0.12   # frais d'administration
TAUX_FRAIS_SINISTRES   = 0.05   # ULAE (frais de gestion des sinistres)


# ============================================================================ #
# REASSURANCE (M5)
# ============================================================================ #

PRIORITE_XL      = 150_000   # priorite par sinistre (€)
CHARGEMENT_REASS = 0.15      # chargement du reassureur


# ============================================================================ #
# CONTROLES DE COHERENCE (M6)
# ============================================================================ #

SEUIL_MALI_COHORTE      = 0.05   # mali > 5 % d'une cohorte -> alerte
SEUIL_COMBINE_RENTABLE  = 1.00   # combine < 100 % attendu
SEUIL_RECONCILIATION    = 0.01   # ecart de reconciliation < 1 %
