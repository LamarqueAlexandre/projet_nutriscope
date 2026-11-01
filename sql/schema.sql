DROP TABLE IF EXISTS products_categories CASCADE;
DROP TABLE IF EXISTS products_brands CASCADE;
DROP TABLE IF EXISTS nutrients CASCADE;
DROP TABLE IF EXISTS categories CASCADE;
DROP TABLE IF EXISTS brands CASCADE;
DROP TABLE IF EXISTS products CASCADE;

CREATE TABLE brands (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    tag TEXT NOT NULL UNIQUE
);

CREATE TABLE products (
    code TEXT PRIMARY KEY,
    name TEXT,
    pnns_groups_1 TEXT,
    nutriscore_score INTEGER,
    nutriscore_grade TEXT
);

CREATE TABLE nutrients (
    product_code TEXT PRIMARY KEY REFERENCES products(code) ON DELETE CASCADE,
    energy_kcal_100g NUMERIC,
    sugars_100g NUMERIC,
    carbohydrated_100g NUMERIC,
    saturated_fat_100g NUMERIC,
    salt_100g NUMERIC,
    sodium_100g NUMERIC,
    fiber_100g NUMERIC,
    proteins_100g NUMERIC,
    fruits_vegetables_nuts_100g NUMERIC
);