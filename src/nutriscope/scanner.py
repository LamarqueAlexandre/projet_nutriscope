import base64
import json
import time

from openai import OpenAI
from pathlib import Path

MODEL = 'qwen3-vl:4b-instruct'
BASE_URL = 'http://localhost:11434/v1'
API_KEY = 'ollama'
TEMPERATURE = 0

PROMPT = """Retourne moi les informations du produit et ses informations
nutritionnelles au format JSON.

Si tu n'as pas les informations pour identifier le produit, n'invente rien.
Si tu ne trouves pas de valeurs pour un nutriment, ne mets pas 0, mets null.
Si tu vois le chevron inférieur "<", tu mets ce qu'il a après comme valeur et tu ajoutes la clé du nutriment dans la liste "inferieur_a".
Exemple : Si tu vois "dont acides gras saturés < 0,1 g", tu mets 0.1 dans "satures" (pas dans "lipides") et tu ajoutes "satures" dans "inferieur_a".
Si tu ne trouves rien à mettre dans alertes, mets une liste vide []

Voici le format attendu :

{
  "statut": "verifie" | "non_verifie" | "illisible",
  "produit": {
    "nom": <texte> | null, 
    "marque": <texte> | null, 
    "code_barres": <texte> | null
  },
  "base": "100 g" | "100 ml" | null,
  "nutriments": {
    "kj": <nombre> | null,
    "kcal": <nombre> | null,
    "lipides": <nombre> | null,
    "satures": <nombre> | null,
    "glucides": <nombre> | null,
    "sucres": <nombre> | null,
    "fibres": <nombre> | null,
    "proteines": <nombre> | null,
    "sel": <nombre> | null
  },
  "inferieur_a": [<clés de nutriments>],
  "ingredients": [<texte>] | null,
  "alertes": [<texte>]
}
"""

PRODUCT_DATA_TEMPLATE = {
    "statut": None,
    "produit": {
        "nom": None,
        "marque": None,
        "code_barres": None,
    },
    "base": None,
    "nutriments": {
        "kj": None,
        "kcal": None,
        "lipides": None,
        "satures": None,
        "glucides": None,
        "sucres": None,
        "fibres": None,
        "proteines": None,
        "sel": None
    },
    "inferieur_a": [],
    "ingredients": None,
    "fiche_catalogue": None,
    "ecarts": [],
    "alertes": [],
    "mesures": {
        "appels_modele": 0,
        "latence_s": 0,
        "tokens_entree": 0,
        "tokens_sortie": 0
    },
}

def scanner_etiquette(image: Path):
    client = OpenAI(
        base_url=BASE_URL,
        api_key=API_KEY
    )

    if isinstance(image, bytes):
        image_bytes = image
    else:
        image_bytes = Path(image).read_bytes()

    encoded_image = base64.b64encode(image_bytes).decode('ascii')
    url_image = f'data:image/jpeg;base64,{encoded_image}'

    messages = [{'role': 'user', 'content': [
        {'type': 'text', 'text': PROMPT},
        {'type': 'image_url', 'image_url': {'url': url_image}}
    ]}]

    debut = time.perf_counter()

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=TEMPERATURE
        )
        latence = time.perf_counter() - debut

        data = json.loads(response.choices[0].message.content)
    except Exception as exception:
        resultat = PRODUCT_DATA_TEMPLATE.copy()
        resultat['statut'] = 'illisible'
        resultat['alertes'] = [f'Erreur lors du scan : {str(exception)}']
        
        return resultat

    resultat = PRODUCT_DATA_TEMPLATE.copy()
    resultat["statut"] = data.get("statut")
    resultat["produit"] = data.get("produit", resultat["produit"])
    resultat["base"] = data.get("base")
    resultat["nutriments"] = data.get("nutriments", resultat["nutriments"])
    resultat["inferieur_a"] = data.get("inferieur_a", [])
    resultat["ingredients"] = data.get("ingredients")
    resultat["alertes"] = data.get("alertes", [])
    
    if resultat['statut'] == 'verifie' and resultat['fiche_catalogue'] is None:
        resultat['statut'] = 'non_verifie'

    resultat["mesures"] = {
        "appels_modele": 1,
        "latence_s": round(latence, 1),
        "tokens_entree": response.usage.prompt_tokens,
        "tokens_sortie": response.usage.completion_tokens
    }

    return resultat
