from langchain_core.tools import tool

products = [
    {
        'name': 'coca',
        'code': '5000112356001',
        'nutriscore': 'E',
        'unite': 'pour 100 ml',
        'source': 'Base de test NutriScope, code-barres 5000112356001',
        'nutriments': {
            'sucres': 10.6,
            'glucides': 11.5,
            'calories': 42,
            'sodium': 0.009
        }
    },
    {
        'name': 'jus d\'orange',
        'code': '3016816039043',
        'nutriscore': 'B',
        'unite': 'pour 100 ml',
        'source': 'Base de test NutriScope, code-barres 3016816039043',
        'nutriments': {
            'sucres': 8.1,
            'glucides': 11.8,
            'calories': 47,
            'sodium': 0.001
        }
    },
    {
        'name': 'eau',
        'code': '5449000050044',
        'nutriscore': 'A',
        'unite': 'pour 100 ml',
        'source': 'Base de test NutriScope, code-barres 5449000050044',
        'nutriments': {
            'sucres': 0,
            'glucides': 0,
            'calories': 0,
            'sodium': 0
        }
    },
    {
        'name': 'lait',
        'code': '3033490134132',
        'nutriscore': 'B',
        'unite': 'pour 100 ml',
        'source': 'Base de test NutriScope, code-barres 3033490134132',
        'nutriments': {
            'sucres': 4.8,
            'glucides': 4.8,
            'calories': 61,
            'sodium': 0.044
        }
    },
    {
        'name': 'pomme',
        'code': '5000226000045',
        'nutriscore': 'A',
        'unite': 'pour 100 g',
        'source': 'Base de test NutriScope, code-barres 5000226000045',
        'nutriments': {
            'sucres': 10.4,
            'glucides': 13.8,
            'calories': 52,
            'sodium': 0.002
        }
    },
    {
        'name': 'pain',
        'code': '3083681046129',
        'nutriscore': 'C',
        'unite': 'pour 100 g',
        'source': 'Base de test NutriScope, code-barres 3083681046129',
        'nutriments': {
            'sucres': 4.2,
            'glucides': 49,
            'calories': 265,
            'sodium': 0.56
        }
    },
    {
        'name': 'poulet-filet',
        'code': '3267340001239',
        'nutriscore': 'A',
        'unite': 'pour 100 g',
        'source': 'Base de test NutriScope, code-barres 3267340001239',
        'nutriments': {
            'sucres': 0,
            'glucides': 0,
            'calories': 165,
            'sodium': 0.063
        }
    },
    {
        'name': 'yaourt',
        'code': '3033491349004',
        'nutriscore': 'B',
        'unite': 'pour 100 g',
        'source': 'Base de test NutriScope, code-barres 3033491349004',
        'nutriments': {
            'sucres': 3.6,
            'glucides': 3.6,
            'calories': 59,
            'sodium': 0.046
        }
    },
    {
        'name': 'banane',
        'code': '5000227006729',
        'nutriscore': 'B',
        'unite': 'pour 100 g',
        'source': 'Base de test NutriScope, code-barres 5000227006729',
        'nutriments': {
            'sucres': 12.2,
            'glucides': 23,
            'calories': 89,
            'sodium': 0.001
        }
    },
    {
        'name': 'fromage',
        'code': '3033490024121',
        'nutriscore': 'D',
        'unite': 'pour 100 g',
        'source': 'Base de test NutriScope, code-barres 3033490024121',
        'nutriments': {
            'sucres': 0.7,
            'glucides': 1.3,
            'calories': 402,
            'sodium': 0.65
        }
    }
]

products_index = {product['name']: product for product in products}

@tool(parse_docstring=True)
def search_product(name: str) -> dict:
    """Cherche un produit PAR SON NOM et retourne ses informations nutritionnelles.
       Utilise-moi quand l'utilisateur demande des informations sur UN PRODUIT SPECIFIQUE.

    Args:
        name: C'est le nom du produit recherché par l'utilisateur 

    Returns:
        Un dictionnaire contenant les informations du produit demandé, None si le produit n'est pas retrouvé.
    """

    try:
        return products_index[name]
    except KeyError:
        return None

@tool(parse_docstring=True)
def substitute(produit: dict) -> dict:
    """Propose UN PRODUIT MEILLEUR pour remplacer un produit existant.
       Utilise-moi quand l'utilisateur demande une ALTERNATIVE ou une SUBSTITUTION
    
    Args:
        produit: une fiche produit au format JSON

    Returns:
        Un dictionnaire contenant le produit de substitution recommandé
    """

    substitute_product = {
        'name': 'coca cola zero',
        'code': '00123456',
        'nutriscore': 'C',
        'unite': 'pour 100 ml',
        'source': 'Base de test NutriScope, code-barres 00123456',
        'nutriments': {
            'sucres': 0,
            'glucides': 0,
            'calories': 1,
            'sodium': 0.009
        }
    }

    return substitute_product

@tool(parse_docstring=True)
def answer_with_source(question: str) -> str:
    """Répond à une demande ou question sur la nutrition (ex: 'Comment calcule-t-on le nutriscore ?').
       Utilise moi pour les questions QUI NE CONCERNENT PAS UN PRODUIT PARTICULIER

    Args:
        question: La question posée par l'utilisateur.
    
    Returns:
        Une réponse texte basée sur les sources trouvées dans la vectordb
    """

    return 'Cet outil est en cours de développement'
