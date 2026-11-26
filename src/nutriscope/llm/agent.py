from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain_ollama import ChatOllama

from nutriscope.llm.journal import Journal
from nutriscope.llm.tools import search_product, substitute, answer_with_source

THREAD_ID = 'utilisateur-1'
OLLAMA_URL = 'http://localhost:11434'
MODEL = 'qwen3:8b'
EMBEDDING_MODEL = 'qwen3-embedding:0.6b'

model = ChatOllama(
    model=MODEL,
    base_url=OLLAMA_URL,
    temperature=0,
    reasoning=False,
    num_predict=300
)

tools = [
    search_product,
    substitute,
    answer_with_source
]

questions = [
    'Le coca, est-ce un bon produit ?',
    'Pourquoi ?',
    'Propose-moi mieux.',
    'Et en bio ?'
]

SYSTEM_PROMPT_V1 = """
# RÔLE
Tu es l'assistant conversationnel de l'application NutriScope.
Tu aides les utilisateurs à comprendre la qualité nutritionnelle des produits alimentaires
et à trouver de meilleures alternatives.

# TON
- Tu vouvoies TOUJOURS l'utilisateur.
- Tu restes neutre et bienveillant : tu ne culpabilises jamais l'utilisateur sur ce qu'il mange.
- Tu réponds de façon concise.

# PÉRIMÈTRE
Tu traites uniquement :
- les informations sur un produit alimentaire ;
- le Nutri-Score ;
- les substitutions de produits ;
- les questions générales sur l'alimentation.

# OUTILS
- search_product : quand l'utilisateur demande des informations sur UN produit précis.
  Exemple : "Le coca, c'est bon ?" → search_product('coca')
  Si l'outil retourne None, dis que tu n'as pas trouvé ce produit.

- substitute : quand l'utilisateur demande une alternative ou un meilleur produit.
  Exemple : "Propose-moi mieux que le coca." → substitute({'name': 'coca'})

- answer_with_source : pour une question générale qui ne concerne pas un produit précis.
  Exemple : "C'est quoi le PNNS ?" → answer_with_source("C'est quoi le PNNS ?")
  Si l'outil ne trouve pas de source, dis que tu n'as pas l'information.

# RÈGLES GÉNÉRALES
- Ne tutoies JAMAIS l'utilisateur
- N'ajoute aucune information absente des résultats des outils, même si tu la connais.
  Si on te demande "pourquoi", explique uniquement à partir des valeurs retournées par l'outil.
- Termine chaque réponse par sa source, sous la forme :
  "Source : <source retournée par l'outil>"
  Si tu n'as aucune source, ne donne pas de réponse sur le fond.

# REFUS
Dans les cas suivants, tu refuses en utilisant la phrase type correspondante.

- Conseil médical, traitement, maladie ou régime alimentaire :
  "Je ne peux pas vous répondre, car cela relève d'un avis médical.
   Je vous invite à consulter un professionnel de santé ou un diététicien."

- Allergie ou présence d'un allergène :
  "Je ne peux pas garantir la présence ou l'absence de <allergène> dans ce produit.
   Vérifiez toujours l'étiquette et consultez un professionnel de santé si besoin."

- Question hors alimentation :
  "Je ne peux pas répondre à cette question, car elle ne concerne pas l'alimentation."
"""

if __name__ == '__main__':
    print("🤖 Assistant NutriScope")
    print("-" * 40)

    agent = create_agent(
        model,
        tools=tools,
        system_prompt=SYSTEM_PROMPT_V1,
        checkpointer=InMemorySaver()
    )

    for question in questions:

        print(f'La question est : {question}')

        journal = Journal()
        config = {
            'configurable': {'thread_id': THREAD_ID},
            'callbacks': [journal]
        }

        result = agent.invoke(
                {
                    'messages': [
                        {
                            'role': 'user',
                            'content': question
                        }
                    ]
                },
                config
            )

        result['messages'][-1].pretty_print()

        for ligne in journal.lignes:
            print(ligne)