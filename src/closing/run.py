"""
Point d'entrée CLI du pipeline de clôture.

Usage :
    python -m closing.run
    python -m closing.run --quiet
    python -m closing.run --strict   (code 1 si alerte)
"""

import argparse
import os
import sys

from .pipeline import executer_closing


def main():
    parser = argparse.ArgumentParser(
        description="Pipeline de clôture actuarielle non-vie"
    )
    parser.add_argument("--quiet", action="store_true",
                        help="Mode silencieux (pas de log)")
    parser.add_argument("--strict", action="store_true",
                        help="Code de sortie 1 si au moins une alerte de controle "
                             "(utile pour bloquer une chaine automatisee)")
    parser.add_argument("--repo", default=None,
                        help="Répertoire racine du projet (défaut : auto)")
    args = parser.parse_args()

    # Detection automatique du repertoire projet
    if args.repo is None:
        # Le script est dans src/closing/, on remonte de 2 niveaux
        repo = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..")
        )
    else:
        repo = os.path.abspath(args.repo)

    print("=" * 70)
    print(" CLOSING ACTUARIEL — Pipeline de cloture trimestrielle")
    print("=" * 70)
    print(f" Repertoire projet : {repo}")
    print()

    resultats = executer_closing(repo, verbose=not args.quiet)

    print()
    print("=" * 70)
    print(" RESUME DU CLOSING")
    print("=" * 70)
    df_compte = resultats["compte_technique"]
    tot = df_compte[df_compte["Segment"] == "TOTAL"].iloc[0]
    print(f"  Primes acquises       : {tot['Primes_acquises']:>14,.0f} EUR"
          .replace(",", " "))
    print(f"  Resultat technique net : {tot['Resultat_net']:>14,.0f} EUR"
          .replace(",", " "))
    print(f"  Ratio combine global  : {tot['Ratio_combine']:>14.1%}")
    print(f"  Boni-mali (run-off)   : {resultats['boni_mali']['Boni_mali'].sum():>+14,.0f} EUR"
          .replace(",", " "))
    print(f"  Alertes de controle   : {resultats['n_alertes']:>14d}")
    print()

    # Par defaut, les alertes sont un resultat metier (signal a analyser) et non
    # une erreur technique : le programme se termine normalement.
    # Avec --strict, toute alerte renvoie le code 1 (blocage de la chaine BAU).
    if args.strict and resultats["n_alertes"] > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
