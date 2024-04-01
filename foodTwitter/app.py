from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///best_recipes.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)


class Recipe(db.Model):
    recipe_id = db.Column(db.Integer, primary_key=True)
    recipe_name = db.Column(db.String(100), nullable=False)
    ingredients = db.Column(db.Text, nullable=False)  # Update to db.Text
    instructions = db.Column(db.Text, nullable=False)  # Update to db.Text
    cooking_time = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False)

    def serialize(self):
        return {
            'recipe_id': self.recipe_id,
            'recipe_name': self.recipe_name,
            'ingredients': self.ingredients,
            'instructions': self.instructions,
            'cooking_time': self.cooking_time,
            'created_at': self.created_at.isoformat()  # Format timestamp as ISO-8601
        }


class Post(db.Model):
    post_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.recipe_id'), unique=True)
    post_content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False)
    user = db.relationship('User', backref=db.backref('posts', lazy=True))
    recipe = db.relationship('Recipe', backref=db.backref('post', lazy=True))


class Ingredient(db.Model):
    ingredient_id = db.Column(db.Integer, primary_key=True)
    food_id = db.Column(db.Integer, nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.recipe_id'), nullable=False)
    recipe = db.relationship('Recipe', backref='recipe_ingredients')  # Rename backref


class NutritionDetail(db.Model):
    detail_id = db.Column(db.Integer, primary_key=True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredient.ingredient_id'), nullable=False)
    carbs = db.Column(db.REAL)
    protein = db.Column(db.REAL)
    fat = db.Column(db.REAL)
    ingredient = db.relationship('Ingredient', backref=db.backref('nutrition_detail', lazy=True))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/recipes', methods=['POST'])
def create_recipe():
    data = request.form
    # Validate data (implement your validation logic here)
    new_recipe = Recipe(
        recipe_name=data['recipe_name'],
        ingredients=data['ingredients'],
        instructions=data['instructions'],
        cooking_time=data['cooking_time'],
    )
    db.session.add(new_recipe)
    db.session.commit()

    # Redirect to the 'get_recipes' route for all recipes
    return redirect(url_for('get_recipes'))


@app.route('/recipes', methods=['GET'])
def get_all_recipes():
    recipes = Recipe.query.order_by(Recipe.created_at.desc()).all()  # Order by descending creation date
    recipe_data = [recipe.serialize() for recipe in recipes]
    return jsonify(recipe_data)


@app.route('/all_recipes')
def get_recipes():
    recipes = Recipe.query.order_by(Recipe.created_at.desc()).all()  # Order by descending creation date
    recipe_data = [recipe.serialize() for recipe in recipes]
    return render_template('all_recipes.html', recipes=recipe_data)


if __name__ == "__main__":
    app.app_context().push()
    db.create_all()
    app.run(debug=True)
