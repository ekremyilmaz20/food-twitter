import sqlite3

conn = sqlite3.connect("recipes.db")
cursor = conn.cursor()

users_table_sql = """
    CREATE TABLE IF NOT EXISTS User (
        user_id INTEGER PRIMARY KEY,
        username TEXT NOT NULL
    );
"""
cursor.execute(users_table_sql)

posts_table_sql = """
    CREATE TABLE IF NOT EXISTS Post (
        post_id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        recipe_id INTEGER UNIQUE,
        post_content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES User(user_id),  -- Foreign key referencing User table
        FOREIGN KEY (recipe_id) REFERENCES Recipe(recipe_id)
    );
"""
cursor.execute(posts_table_sql)

recipes_table_sql = """
    CREATE TABLE IF NOT EXISTS Recipe (
        recipe_id INTEGER PRIMARY KEY,
        recipe_name TEXT NOT NULL,
        ingredients TEXT NOT NULL,
        instructions TEXT NOT NULL,
        cooking_time INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
"""
cursor.execute(recipes_table_sql)

ingredients_table_sql = """
    CREATE TABLE IF NOT EXISTS Ingredient (
        ingredient_id INTEGER PRIMARY KEY,
        food_id INTEGER NOT NULL,
        recipe_id INTEGER NOT NULL,
        FOREIGN KEY (recipe_id) REFERENCES Recipe(recipe_id)
    );
"""
cursor.execute(ingredients_table_sql)

nutrition_details_table_sql = """
    CREATE TABLE IF NOT EXISTS NutritionDetail (
        detail_id INTEGER PRIMARY KEY,
        ingredient_id INTEGER NOT NULL,
        carbs REAL,
        protein REAL,
        fat REAL,
        FOREIGN KEY (ingredient_id) REFERENCES Ingredient(ingredient_id)
    );
"""
cursor.execute(nutrition_details_table_sql)

conn.commit()
conn.close()
