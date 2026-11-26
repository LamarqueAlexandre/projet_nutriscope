from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain_ollama import ChatOllama

from nutriscope.llm.journal import Journal
from nutriscope.llm.prompts import SYSTEM_PROMPT_V2
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
    'Et en bio ?',
    'Je suis diabétique, est-ce que je peux boire du coca ?',
    'Le pain contient-il des arachides ? Je suis allergique.',
    'Quelle est la capitale de l\'Italie ?'
]

if __name__ == '__main__':
    print("🤖 Assistant NutriScope")
    print("-" * 40)

    agent = create_agent(
        model,
        tools=tools,
        system_prompt=SYSTEM_PROMPT_V2,
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