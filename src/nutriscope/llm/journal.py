import time
from langchain_core.callbacks import BaseCallbackHandler


class Journal(BaseCallbackHandler):
    """Note chaque étape de l'agent : type, nom, durée et tokens. Jamais le texte des messages."""

    def __init__(self):
        self.lignes = []
        self.debuts = {}

    def on_chat_model_start(self, serialized, messages, *, run_id, **kwargs):
        self.debuts[run_id] = time.perf_counter()

    def on_llm_end(self, response, *, run_id, **kwargs):
        duree = time.perf_counter() - self.debuts[run_id]
        message = response.generations[0][0].message

        outils_demandes = []
        for appel in message.tool_calls:
            outils_demandes.append(appel["name"])
        if outils_demandes:
            nom = ", ".join(outils_demandes)
        else:
            nom = "réponse"

        tokens = message.usage_metadata
        self.lignes.append({"étape": "modèle", "nom": nom, "durée (s)": round(duree, 2),
                            "tokens entrée": tokens["input_tokens"], "tokens sortie": tokens["output_tokens"]})

    def on_tool_start(self, serialized, input_str, *, run_id, **kwargs):
        self.debuts[run_id] = time.perf_counter()

    def on_tool_end(self, output, *, run_id, **kwargs):
        duree = time.perf_counter() - self.debuts[run_id]
        self.lignes.append({"étape": "outil", "nom": output.name, "durée (s)": round(duree, 2),
                            "tokens entrée": 0, "tokens sortie": 0})