# Module 1 — Note de validation du portefeuille simulé

**Périmètre :** branche MTPL (RC automobile), portefeuille simulé sur 5 années de survenance (2021–2025), observation au 31/12/2025.

---

## 1. Volumétrie produite

| Indicateur | Valeur | Commentaire |
|---|---|---|
| Polices générées | 50 000 | Croissance commerciale +5 % p.a. |
| Mix Particuliers / Flottes | 80 % / 20 % | Cible respectée |
| Sinistres déclarés | 3 468 | Fréquence empirique 6,94 % |
| Mix Matériel / Corporel | 85 % / 15 % | 2 953 matériels, 515 corporels |
| Flux de paiements observés | 10 081 lignes | Sous diagonale du triangle |
| Primes acquises totales | 32,7 M€ | |
| Charge ultime vraie | 19,3 M€ | Vérité terrain conservée |
| Paiements observés au 31/12/2025 | 13,8 M€ | |
| **Écart à provisionner** | **5,6 M€** | Cible des méthodes de M2 |
| Ratio S/P brut | 59,1 % | Cohérent MTPL belge |

## 2. Contrôles de cohérence

> **En clair —** *Avant tout calcul de provisionnement, on vérifie que le portefeuille simulé n'a pas de comportement aberrant. Trois contrôles standards en clôture actuarielle :*

**Contrôle 1 — Fréquence théorique vs empirique.**
Cible théorique : 0,80 × 6 % + 0,20 × 10 % = **6,80 %**.
Empirique : **6,94 %**. Écart de +0,14 point, dans la marge d'erreur attendue pour 50 000 polices (variance Poisson).

**Contrôle 2 — Vitesse de développement.**
Le pattern empirique observé sur la cohorte 2021 (5 ans visibles) reproduit bien les patterns théoriques injectés :
- Matériel : 70 → 92 → 98 → 100 → 100 % (court-tail)
- Corporel : 22 → 51 → 74 → 91 → 100 % (long-tail)

**Contrôle 3 — Diagonale du triangle.**
Les paiements de l'année calendaire 2025 (diagonale du triangle) sont distribués cohéremment entre les 5 cohortes de survenance, avec une décroissance pour les cohortes anciennes (peu de paiements résiduels) et une montée pour la cohorte 2025 (paiements première année).

## 3. Signal métier identifié pour les modules suivants

> **À noter —** *La cohorte 2023 présente un Ultimate vrai anormalement élevé (5,38 M€ vs ~3,5 M€ pour les autres années). C'est dû à 2-3 sinistres corporels lourds. Cette anomalie est conservée volontairement : elle générera un **mali** en M4 lorsque Chain-Ladder, qui s'appuie sur le pattern moyen historique, sous-estimera initialement la charge ultime de cette année. C'est exactement le type de signal qu'une équipe de Technical Risk Monitoring doit détecter et expliquer au management.*

## 4. Fichiers produits

```
data/raw/
├── polices.csv                              (50 000 lignes)
├── sinistres.csv                            (3 468 lignes, avec ultimate_vrai)
└── paiements.csv                            (10 081 lignes)

data/processed/
├── triangle_paiements_cumules.csv           (5 × 5, sous-diagonale NaN)
├── triangle_paiements_incrementaux.csv      (5 × 5)
└── ultimate_vrai_par_annee.csv              (vérité terrain pour backtest)

outputs/
└── m1_validation_portefeuille.png           (figure d'EDA en 2×2)
```

## 5. Limites et hypothèses retenues

- **Exposition** : prise à 1 an plein pour chaque police (pas de pro-rata de souscription). À raffiner si on veut tester des effets de saisonnalité.
- **Pas de réassurance** : la charge brute = charge nette dans cette version. La réassurance sera introduite au M5 (compte technique).
- **Pas de catastrophes naturelles** : seuls les sinistres attritionnels sont simulés. Pour un portefeuille MTPL pur, c'est acceptable ; pour de l'habitation ou de la flotte transport, il faudrait ajouter une couche cat.
- **Pas de RBNS dossier-par-dossier** : seuls les paiements sont simulés. La provision dossier-dossier sera introduite implicitement en M4 (via la décomposition boni-mali).
- **Inflation constante 2,5 %** : pas de choc inflationniste type 2022-2023. Réaliste mais conservateur pour la suite (les méthodes de provisionnement classiques fonctionnent bien dans ce régime).

## 6. Prochaine étape : Module 2 — Provisionnement

Le triangle des paiements cumulés est prêt pour :
1. **Chain-Ladder déterministe** : estimation des link ratios et projection.
2. **Bornhuetter-Ferguson** : intégration d'un a priori de S/P.
3. **Mack stochastique** : estimation de la variance des IBNR + intervalle de confiance 99,5 %.

La vérité terrain (`ultimate_vrai_par_annee.csv`) permettra de **backtester chacune des trois méthodes** sur la cohorte 2021 (où la quasi-totalité de l'Ultimate est observé) et de diagnostiquer le biais Chain-Ladder sur la cohorte 2023 anormale.
