# ADR 0001 — Pas de fine-tuning pour la v1 de NutriScope

- **Date** : 2026-11-30

## Contexte
Voici ce qu'on a actuellement dans le projet : 
* Un modèle de classification qui prédit le nutriscore
* Un modèle de substitution pour proposer une alternative plus saine
* Un scanner de produit pour reconnaitre le produit, l'étiquettes
* Un modèle LLM local - qwen3:8b - qui pourrait être amené à évoluer.

Le besoin : <br>
Répondre sur les produits, le Nutri-Score, et les substitutions, en citant ses sources, <br>
et en refusant les demandes hors périmètre.

## Options étudiées
1. Fine-tuner le LLM
2. Garder le modèle tel quel + prompt système + outils (+ RAG)

## Décision
On choisit l'option 2 : garder le modèle tel quel, avec un prompt système et des outils

## Justification
* Les données sont mises à jour régulièrement et le fine-tuning fixe les connaissances <br>
  dans le modèle à un instant T. Un assistant se servant des outils et du RAG lit les données à jour.
* Les sources doivent pouvoir être citées, et le fine-tuning ne permettra pas ce comportement, <br> alors que les outils le peuvent.
* Le coût d'un entraînement n'est pas à négliger, cela demande du temps, de la puissance de calcul <br> et des données récoltées, analysées et nettoyées à chaque entaînement.

## Conséquences
**Ce que ça apporte**
- Les réponses s'appuient sur des données à jour : quand une fiche produit change,
  l'assistant utilise directement la nouvelle fiche, sans réentraînement.
- Chaque réponse peut citer sa source, ce qui la rend vérifiable par l'utilisateur.
- Aucun entraînement à prévoir : pas de jeu de données à constituer, pas de GPU, pas de temps d'entraînement.

**Ce que ça coûte / ce qu'on accepte**
- La qualité des réponses dépend de la qualité du prompt système et des outils :
  si un outil ne trouve rien, l'assistant ne peut pas répondre sur le fond.
- Le prompt système et la description des outils sont envoyés à chaque appel au modèle :
  environ 900 tokens d'entrée dès la première question. Avec l'historique de la conversation,
  on atteint environ 1 500 tokens à la 4ᵉ question.
- Une question qui utilise un outil demande 2 appels au modèle (choix de l'outil, puis rédaction),
  soit environ 1,5 à 2 s par appel, et environ 6 s pour le tout premier appel (chargement du modèle).
- Un modèle de 8 milliards de paramètres peut ne pas toujours respecter les consignes du prompt :
  les premiers tests montrent des informations inventées et un tutoiement malgré la consigne.
  Le prompt sera donc ajusté et retesté.

*Mesures relevées le 2026-11-26 avec le journal de l'agent (`journal.py`), sur 4 questions
enchaînées dans une même conversation, avec qwen3:8b via Ollama en local et des outils aux
données fictives.*

**Dans quel cas on reviendrait sur cette décision**
- Si, malgré plusieurs versions du prompt, les tests montrent que l'assistant ne respecte pas
  le ton, le format des sources ou les refus attendus.
- Si on doit passer à un modèle plus petit (pour gagner en rapidité) qui ne suit plus
  correctement les consignes sans entraînement.