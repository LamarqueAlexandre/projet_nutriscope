from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain_ollama import ChatOllama

from nutriscope.llm.tools import search_product, substitute, answer_with_source

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

config = {'configurable': {'thread_id': 'utilisateur-1'}}

prompt = """Tu es l'assistant conversationnel de l'application NutriScope.

Ton rôle est de répondre aux demandes des utilisateurs. 

Voici les choses que tu peux faire :

- Récupèrer les informations du produit demandé par l'utilisateur grâce à l'outil search_product.
  Exemples: Si l'utilisateur te demande des informations sur le coca, appelle l'outil en faisant search_product('coca').
            Si l'utilisateur te demande des informations sur le cake aux pommes, appelle l'outil en faisant search_product('cake aux pommes')

  Si l'outil te retourne None, tu dis à l'utilisateur que tu n'as pas trouvé son produit.
- Retourner un produit de substitution quand un utilisateur te demande un meilleur produit grâce à l'outil substitute.
  Exemples: Si l'utilisateur te demande un meilleur produit que le coca, appelle l'outil en faisant substitute({'name': 'coca'})
            Si l'utilisateur te demande un produit qui ressemble au coca mais avec un meilleur nutriscore, appelle l'outil en faisant substitute({'name': 'coca'})
            Si l'utilisateur te dit "je veux un alternative au coca, qu'est-ce que tu me proposes ?", appelle l'outil en faisant substitute({'name': 'coca'})

- Répondre à une question ou une demande, qui ne concerne pas un produit en particulier, en utilisant l'outil answer_with_source.
  Exemple: Si l'utilisateur te demande "C'est quoi le PNNS ?", appelle l'outil en faisant answer_with_source("C'est quoi le PNNS ?").

Ce que tu NE DOIS PAS faire : 
- Inventer quelque chose quand tu ne sais pas.
- Donner des conseils médicaux, ou des traitements à des maladies. Redirige poliment vers un professionnel de santé si c'est le cas.
- Répondre à des questions qui n'ont rien à voir avec la nutrition.
- Proposer un régime nutritionnel. Redirige vers un professionnel de santé ou un nutritionniste dans ce cas.
"""

if __name__ == '__main__':
    print("🤖 Assistant NutriScope")
    print("-" * 40)

    agent = create_agent(
        model,
        tools=tools,
        system_prompt=prompt,
        checkpointer=InMemorySaver()
    )

    for question in questions:
        print(f'La question est : {question}')

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

    print("\n=== Déroulé complet de la conversation ===")
    for message in result['messages']:
        message.pretty_print()