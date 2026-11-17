from pydantic import BaseModel, Field

class NutrimentLecture(BaseModel):
    """Schéma de validation pour les nutriments lus par le modèle"""
    kj: int | None = None
    kcal: int | None = None
    lipides: float | None = None
    satures: float | None = None
    glucides: float | None = None
    sucres: float | None = None
    fibres: float | None = None
    proteines: float | None = None
    sel: float | None = None

class ProduitLecture(BaseModel):
    """Schéma de validation pour les infos du produit"""
    nom: str | None = None
    marque: str | None = None
    code_barres: str | None = None

class LectureJSON(BaseModel):
    """Ce que le modèle retourne, validé"""
    statut: str
    produit: ProduitLecture
    base: str | None = None
    nutriments: NutrimentLecture
    inferieur_a: list[str] = []
    ingredients: list[str] | None = None
    alertes: list[str] = []