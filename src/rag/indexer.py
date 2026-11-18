"""Indexation rejouable des fiches produits dans Chroma (TP 19, étape 1).

Usage, à la racine du dépôt :
  python -m src.rag.indexer                    # toutes les fiches de data/corpus/fiches
  python -m src.rag.indexer --reconstruire     # repart d'une collection vide
  python -m src.rag.indexer --limite 500       # repli : fiches citées dans eval/questions.csv
                                               # + 500 fiches tirées avec une graine fixe

Fourni : le réglage commun, la lecture des fichiers, le repli, la ligne de commande.
À écrire : TODO 1 (metadonnees_de) et TODO 2 (indexer).
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import time
from pathlib import Path
from typing import Any

import chromadb

from src.rag.embeddings import TAILLE_LOT, Vectoriseur, embed_documents

RACINE = Path(__file__).resolve().parents[2]
DOSSIER_FICHES = RACINE / "data" / "corpus" / "fiches"
CHEMIN_INDEX = RACINE / "data" / "index"
CHEMIN_QUESTIONS = RACINE / "eval" / "questions.csv"
NOM_COLLECTION = "fiches"
CLES = ("code", "nom", "marque", "rayon", "nutriscore", "source")


def collection_fiches(chemin: str | Path = CHEMIN_INDEX, reconstruire: bool = False) -> Any:
    """Le réglage commun à toutes les équipes : distance cosinus, aucun modèle d'embeddings caché."""
    client = chromadb.PersistentClient(path=str(chemin))
    if reconstruire:
        try:
            client.delete_collection(NOM_COLLECTION)
        except Exception:  # la collection n'existait pas encore
            pass
    return client.get_or_create_collection(
        NOM_COLLECTION,
        configuration={"hnsw": {"space": "cosine"}},
        embedding_function=None,  # aucun modèle caché : on fournit nos vecteurs
    )


def metadonnees_de(meta: dict[str, Any]) -> dict[str, Any]:
    """Les métadonnées d'une fiche, à partir d'une ligne de metadonnees.jsonl.

    - Exactement les six clés de CLES, ni plus ni moins.
    - Une valeur absente ou vide ("") devient None : inconnue, jamais 0, jamais chaîne vide.
    - Le code reste une chaîne, sans espace autour : un code-barres n'est pas un nombre.
    """

    return {
        'code': (meta.get('code') or None) and meta.get('code').strip(),
        'nom': (meta.get('nom') or None) and meta.get('nom').strip(),
        'marque': (meta.get('marque') or None) and meta.get('marque').strip(),
        'rayon': (meta.get('rayon') or None) and meta.get('rayon').strip(),
        'nutriscore': (meta.get('nutriscore') or None) and meta.get('nutriscore').strip(),
        'source': (meta.get('source') or None) and meta.get('source').strip(),
    }


def lire_fiches(dossier: str | Path = DOSSIER_FICHES) -> list[dict[str, Any]]:
    """Une entrée par produit : {"id": "fiche:<code>", "texte": ..., "metadonnees": {...}}.

    Les métadonnées viennent de metadonnees.jsonl. Un code présent deux fois n'est gardé qu'une fois.
    """
    dossier = Path(dossier)
    chemin_meta = dossier / "metadonnees.jsonl"
    if not chemin_meta.exists():
        raise FileNotFoundError(f"{chemin_meta} introuvable : générez d'abord les fiches (python -m src.corpus.fiches).")
    fiches: dict[str, dict[str, Any]] = {}
    for ligne in chemin_meta.read_text(encoding="utf-8").splitlines():
        if not ligne.strip():
            continue
        metadonnees = metadonnees_de(json.loads(ligne))
        code = metadonnees["code"]
        fiches[f"fiche:{code}"] = {
            "id": f"fiche:{code}",
            "texte": (dossier / f"{code}.txt").read_text(encoding="utf-8"),
            "metadonnees": metadonnees,
        }
    return list(fiches.values())


def indexer(fiches: list[dict[str, Any]], collection: Any, vectoriser: Vectoriseur = embed_documents,
            taille_lot: int = TAILLE_LOT, bavard: bool = False) -> int:
    """Range les fiches dans la collection, par lots de `taille_lot`. Rend collection.count().

    - Relancer l'indexation ne crée aucun doublon, et une fiche modifiée remplace l'ancienne.
      Lisez la différence entre collection.add() et collection.upsert() dans la documentation de Chroma.
    - Pour chaque lot, Chroma attend quatre listes alignées : ids, embeddings (vectoriser(textes)),
      documents (les textes) et metadatas.
    - Envoyez toutes les clés, None compris : une clé envoyée à None est supprimée dans Chroma,
      alors qu'une clé omise garderait son ancienne valeur.
    """
    for debut in range(0, len(fiches), taille_lot):
        lot = fiches[debut:debut + taille_lot]

        ids = [fiche['id'] for fiche in lot]
        textes = [fiche['texte'] for fiche in lot]
        metadatas = [fiche['metadonnees'] for fiche in lot]

        embeddings = vectoriser(textes)

        collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=textes,
            metadatas=metadatas
        )

    return collection.count()


def ids_cites(chemin_questions: str | Path = CHEMIN_QUESTIONS) -> set[str]:
    """Les fiches citées dans sources_attendues, toutes questions confondues."""
    with open(chemin_questions, encoding="utf-8", newline="") as f:
        lignes = list(csv.DictReader(f, delimiter=";"))
    return {s.strip() for l in lignes for s in (l.get("sources_attendues") or "").split("|")
            if s.strip().startswith("fiche:")}


def selection_repli(fiches: list[dict[str, Any]], chemin_questions: str | Path, limite: int,
                    graine: int = 42) -> list[dict[str, Any]]:
    """Repli : les fiches citées par le jeu d'évaluation + `limite` fiches tirées au hasard."""
    cites = ids_cites(chemin_questions)
    gardees = [f for f in fiches if f["id"] in cites]
    autres = [f for f in fiches if f["id"] not in cites]
    random.Random(graine).shuffle(autres)
    return gardees + autres[:limite]


def main() -> None:
    parser = argparse.ArgumentParser(description="Indexe les fiches produits dans Chroma.")
    parser.add_argument("--fiches", default=str(DOSSIER_FICHES))
    parser.add_argument("--index", default=str(CHEMIN_INDEX))
    parser.add_argument("--reconstruire", action="store_true", help="repart d'une collection vide")
    parser.add_argument("--limite", type=int, default=None, help="repli : fiches citées + N fiches tirées")
    parser.add_argument("--questions", default=str(CHEMIN_QUESTIONS))
    args = parser.parse_args()

    fiches = lire_fiches(args.fiches)
    if args.limite is not None:
        fiches = selection_repli(fiches, args.questions, args.limite)
        print(f"Repli : {len(fiches)} fiches. Score flatteur (moins de concurrents) : index complet dès que possible.")
    collection = collection_fiches(args.index, reconstruire=args.reconstruire)
    debut = time.perf_counter()
    total = indexer(fiches, collection, bavard=True)
    duree = time.perf_counter() - debut
    print(f"{len(fiches)} fiches vectorisées et indexées en {duree:.1f} s "
          f"({len(fiches) / duree:.1f} fiches/s). Collection : {total} fiches.")


if __name__ == "__main__":
    main()
