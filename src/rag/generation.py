"""Génération des réponses avec sources

Fonction principale : 
    repondre_avec_sources(question) -> dict
        - Récupère les fiches pertinentes via chercher()
        - Passe question + contexte au LLM (Claude)
        - Rend la réponse avec citation des sources
"""