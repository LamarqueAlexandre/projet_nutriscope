from pathlib import Path

def scanner_etiquette(image: Path) -> dict:
    return {
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