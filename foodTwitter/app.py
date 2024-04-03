from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

# Creates an instance for Flask application and determines the root path of application with the argument.
app = Flask(__name__)
# Sets configuration variable SQLALCHEMY_DATABASE_URI for the database that SQL Alchemy should use.
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///best_recipes.db"
# Sets configuration variable SQLALCHEMY_TRACK_MODIFICATIONS to increase performance.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Creates a SQL Alchemy object and links it with the Flask application instance
# To bind the application and database together.
db = SQLAlchemy(app)


# Defines a class named User to represent a table in the database, by inheriting the db.Model provided by SQL Alchemy
# With columns user_id (serving as the primary key) and username.
class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)


# Defines a class named Recipe to represent a table in database by inheriting the db.Model provided by SQL Alchemy
# With columns recipe_id (serving as the primary key), recipe_name, ingredients,
# instructions, cooking_time and created_at.
class Recipe(db.Model):
    recipe_id = db.Column(db.Integer, primary_key=True)
    recipe_name = db.Column(db.String(100), nullable=False)
    ingredients = db.Column(db.Text, nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    cooking_time = db.Column(db.Integer, nullable=False)
    # A timestamp field indicates the date and time when the recipe was created.
    # The server_default=db.func.current_timestamp() sets the default value to the current timestamp.
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False)

    """
    Converts a Recipe object into a dictionary to make it easier to store or manipulate.

    Returns:
        dict: A dictionary representation of the Recipe object.
              Each attribute of the Recipe is mapped to a key-value pair.
    """

    def serialize(self):
        return {
            'recipe_id': self.recipe_id,
            'recipe_name': self.recipe_name,
            'ingredients': self.ingredients,
            'instructions': self.instructions,
            'cooking_time': self.cooking_time,
            'created_at': self.created_at.isoformat()  # Format timestamp as ISO-8601 to ensure consistency.
        }


# Defines a class named Post to represent a table in the database by inheriting from db.Model provided by SQL Alchemy
# With columns post_id (serving as the primary key), user_id (a foreign key referencing user.user_id),
# recipe_id (a foreign key referencing recipe.recipe_id), post_content, and created_at.
class Post(db.Model):
    post_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.recipe_id'), unique=True)
    post_content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False)
    # Defines one-to-many relationship between Post and User tables that indicates each user can have multiple posts
    # While each post belongs to one user.
    # backref=db.backref('posts', lazy=True) argument establishes a back reference from User table to the Post table
    # To allow access to the posts made by a user. lazy=True parameter specifies lazy loading for the relationship
    # To ensure that related posts are loaded from the database only when explicitly accessed, to optimize performance
    # By minimizing unnecessary queries.
    user = db.relationship('User', backref=db.backref('posts', lazy=True))
    # Defines one-to-one relationship between Recipe and Post tables that indicates each post contains a single recipe.
    # backref=db.backref('post', lazy=True) argument establishes a back reference from Recipe table to the Post table
    # To allow access to the posts from within a recipe. lazy=True parameter specifies lazy loading for the relationship
    # To ensure that related posts are loaded from the database only when explicitly accessed, to optimize performance
    # By minimizing unnecessary queries.
    recipe = db.relationship('Recipe', backref=db.backref('post', lazy=True))


# Defines a class named Ingredient to represent a table in the database by inheriting from db.Model provided
# By SQL Alchemy with columns ingredient_id (serving as the primary key), food_id, and recipe_id (a foreign key
# Referencing recipe.recipe_id).
class Ingredient(db.Model):
    ingredient_id = db.Column(db.Integer, primary_key=True)
    food_id = db.Column(db.Integer, nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.recipe_id'), nullable=False)
    # Defines one-to-many relationship between the Ingredient and Recipe tables that indicates each recipe
    # Can have multiple ingredients. The backref='recipe_ingredients' argument establishes a back reference
    # From the Recipe table to the Ingredient table, allowing access to the ingredients associated with a recipe.
    # lazy=True parameter specifies lazy loading for the relationship to ensure that related posts are loaded
    # From the database only when explicitly accessed, to optimize performance by minimizing unnecessary queries.
    recipe = db.relationship('Recipe', backref='recipe_ingredients', lazy=True)


# Defines a class named NutritionDetail to represent a table in the database by inheriting from db.Model provided
# By SQL Alchemy with columns detail_id (serving as the primary key), ingredient_id (a foreign key
# Referencing ingredient.ingredient_id), carbs, protein, and fat.
class NutritionDetail(db.Model):
    detail_id = db.Column(db.Integer, primary_key=True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredient.ingredient_id'), nullable=False)
    carbs = db.Column(db.REAL)
    protein = db.Column(db.REAL)
    fat = db.Column(db.REAL)
    # Defines a one-to-many relationship between the Ingredient and NutritionDetail tables that indicates
    # Each ingredient can have multiple nutrition details. The backref=db.backref('nutrition_detail', lazy=True)
    # Argument establishes a back reference from the Ingredient table to the NutritionDetail table to
    # allow access to the nutrition details associated with an ingredient. lazy=True parameter specifies lazy loading
    # for the relationship to ensure that related posts are loaded from the database only when explicitly accessed,
    # to optimize performance by minimizing unnecessary queries.
    ingredient = db.relationship('Ingredient', backref=db.backref('nutrition_detail', lazy=True))


"""
Renders the index page of the web application.

Returns:
    str: HTML content for the index page.
"""


@app.route('/')
def index():
    return render_template('index.html')


"""
Handles the creation of a new recipe via a POST request.

This function retrieves data from the request form, creates a new Recipe object with the provided data, 
and adds it to the database. Prior to adding the new recipe, it is recommended to implement validation logic 
to ensure the integrity of the data. After successfully adding the recipe to the database, 
it redirects the user to the endpoint for retrieving all recipes.

Returns:
    werkzeug.wrappers.response.Response: A redirect response to the 'get_recipes' endpoint.
"""


@app.route('/recipes', methods=['POST'])
def create_recipe():
    data = request.form
    new_recipe = Recipe(
        recipe_name=data['recipe_name'],
        ingredients=data['ingredients'],
        instructions=data['instructions'],
        cooking_time=data['cooking_time'],
    )
    db.session.add(new_recipe)
    db.session.commit()

    return redirect(url_for('get_recipes'))


"""
Renders a web page displaying all available recipes.

This route queries the database for all Recipe objects, orders them by descending creation date,
and serializes each recipe into a dictionary format using the 'serialize' method.
The serialized recipe data is then passed to the 'all_recipes.html' template along with rendering.
This template is responsible for presenting the recipe data in a human-readable format on the web page.

Returns:
    flask.Response: A rendered HTML page displaying all available recipes.
"""


@app.route('/all_recipes')
def get_recipes():
    recipes = Recipe.query.order_by(Recipe.created_at.desc()).all()
    recipe_data = [recipe.serialize() for recipe in recipes]
    return render_template('all_recipes.html', recipes=recipe_data)


"""
Handles the updating of a specific recipe via a GET or POST request.

For a GET request, it retrieves the recipe with the specified 'recipe_id' from the database,
serializes it into a dictionary format, and passes the serialized data to the 'update_recipe.html' template for rendering.
If the specified recipe is not found in the database, it returns a 404 error response.

For a POST request, it retrieves the recipe with the specified 'recipe_id' from the database,
updates its attributes with the data received from the request form, and commits the changes to the database.
If the specified recipe is not found in the database, it returns a 404 error response.
After successfully updating the recipe, it redirects the user to the 'get_recipes' endpoint.

Parameters:
    recipe_id (int): The unique identifier of the recipe to be updated.

Returns:
    flask.Response: A rendered HTML page for GET request, or a redirect response for POST request.
"""


@app.route('/recipes/<int:recipe_id>', methods=['GET', 'POST'])
def update_recipe(recipe_id):
    if request.method == 'GET':
        recipe = Recipe.query.get(recipe_id)
        if not recipe:
            return jsonify({'error': 'Recipe not found'}), 404
        return render_template('update_recipe.html', recipe=recipe.serialize())  # Pass recipe data
    elif request.method == 'POST':
        data = request.form
        recipe = Recipe.query.get(recipe_id)
        if not recipe:
            return jsonify({'error': 'Recipe not found'}), 404
        recipe.recipe_name = data['recipe_name']
        recipe.ingredients = data['ingredients']
        recipe.instructions = data['instructions']
        recipe.cooking_time = data['cooking_time']
        db.session.commit()

        return redirect(url_for('get_recipes'))


"""
Handles the deletion of a specific recipe via a POST request.

This route retrieves the recipe identified by the provided 'recipe_id' from the database.
If the specified recipe is not found, it returns a 404 error response.
It then deletes all associated ingredients of the recipe from the database using the Ingredient model.
Subsequently, it deletes the recipe itself from the database.
After successful deletion, it redirects the user to the 'get_recipes' endpoint to view the updated list of recipes.

Parameters:
    recipe_id (int): The unique identifier of the recipe to be deleted.

Returns:
    werkzeug.wrappers.response.Response: A redirect response to the 'get_recipes' endpoint.
"""


@app.route('/recipes/<int:recipe_id>/delete', methods=['POST'])
def delete_recipe(recipe_id):
    recipe = Recipe.query.get(recipe_id)
    if not recipe:
        return jsonify({'error': 'Recipe not found'}), 404

    Ingredient.query.filter_by(recipe_id=recipe_id).delete()

    db.session.delete(recipe)
    db.session.commit()
    return redirect(url_for('get_recipes'))


"""
Entry point for running the Flask application.

This conditional block checks if the script is being executed directly, ensuring that the subsequent code runs only
when the script is executed as the main program.

- It pushes an application context to allow Flask extensions to function within the application.
- It creates all database tables defined in the models using SQLAlchemy's `create_all()` method.
- Finally, it starts the Flask development server with debugging enabled.

Note: This block typically appears at the end of the script, serving as the entry point for 
running the Flask application.

"""


if __name__ == "__main__":
    app.app_context().push()
    db.create_all()
    app.run(debug=True)
