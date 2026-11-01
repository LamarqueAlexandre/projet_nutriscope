-- schema.sql : base NutriScope (version squelette)
-- Rejouable : les tables sont supprimées puis recréées à chaque exécution.

-- Suppression dans l'ordre inverse des dépendances (liaisons, puis tables de base)
DROP TABLE IF EXISTS products_categories CASCADE;
DROP TABLE IF EXISTS products_brands CASCADE;
DROP TABLE IF EXISTS nutrients CASCADE;
DROP TABLE IF EXISTS categories CASCADE;
DROP TABLE IF EXISTS brands CASCADE;
DROP TABLE IF EXISTS products CASCADE;

-- Tables de référence
CREATE TABLE brands (
    id   SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE categories (
    id  SERIAL PRIMARY KEY,
    tag TEXT NOT NULL UNIQUE
);

-- Produits
CREATE TABLE products (
    code             TEXT PRIMARY KEY,
    product_name     TEXT,
    pnns_groups_1    TEXT,
    nutriscore_score INTEGER,
    nutriscore_grade TEXT
);

CREATE TABLE nutrients (
    product_code                   TEXT PRIMARY KEY REFERENCES products(code) ON DELETE CASCADE,
    energy_kcal_100g               NUMERIC,
    sugars_100g                    NUMERIC,
    carbohydrates_100g             NUMERIC,
    fat_100g                       NUMERIC,
    saturated_fat_100g             NUMERIC,
    salt_100g                      NUMERIC,
    sodium_100g                    NUMERIC,
    fiber_100g                     NUMERIC,
    proteins_100g                  NUMERIC,
    fruits_vegetables_legumes_100g NUMERIC
);

-- Tables de liaison (relations plusieurs-à-plusieurs)
CREATE TABLE products_brands (
    product_code TEXT    NOT NULL REFERENCES products(code) ON DELETE CASCADE,
    brand_id     INTEGER NOT NULL REFERENCES brands(id) ON DELETE CASCADE,
    PRIMARY KEY (product_code, brand_id)
);

CREATE TABLE products_categories (
    product_code TEXT    NOT NULL REFERENCES products(code) ON DELETE CASCADE,
    category_id  INTEGER NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
    PRIMARY KEY (product_code, category_id)
);

-- Index sur le sens inverse des liaisons (la clé composite couvre déjà product_code d'abord)
CREATE INDEX idx_products_brands_brand ON products_brands(brand_id);
CREATE INDEX idx_products_categories_category ON products_categories(category_id);