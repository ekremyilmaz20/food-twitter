import unittest
from app import app, db, Recipe


class TestApp(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        self.ctx = app.app_context()
        self.ctx.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_create_recipe(self):
        data = {
            'recipe_name': 'Test Recipe',
            'ingredients': 'Ingredient 1, Ingredient 2',
            'instructions': 'Test instructions',
            'cooking_time': 30
        }
        response = self.app.post('/recipes', data=data)
        self.assertEqual(response.status_code, 302)

    def test_get_all_recipes(self):
        response = self.app.get('/recipes')
        self.assertEqual(response.status_code, 200)

    def test_delete_recipe(self):
        # Create a recipe to be deleted
        new_recipe = Recipe(
            recipe_name='Test Recipe',
            ingredients='Ingredient 1, Ingredient 2',
            instructions='Test instructions',
            cooking_time=30,
        )
        db.session.add(new_recipe)
        db.session.commit()

        # Get the ID of the created recipe
        recipe_id = new_recipe.recipe_id

        # Send a POST request to delete the recipe
        response = self.app.post(f'/recipes/{recipe_id}/delete')

        # Check if the response redirects to the recipes page after deletion
        self.assertEqual(response.status_code, 302)
        self.assertIn('/all_recipes', response.headers['Location'])

        # Check if the recipe is deleted from the database
        deleted_recipe = db.session.query(Recipe).get(recipe_id)
        self.assertIsNone(deleted_recipe)

    def test_update_recipe(self):
        # Create a recipe to be updated
        new_recipe = Recipe(
            recipe_name='Test Recipe',
            ingredients='Ingredient 1, Ingredient 2',
            instructions='Test instructions',
            cooking_time=30,
        )
        db.session.add(new_recipe)
        db.session.commit()

        # Get the ID of the created recipe
        recipe_id = new_recipe.recipe_id

        # Data for updating the recipe
        updated_data = {
            'recipe_name': 'Updated Test Recipe',
            'ingredients': 'Updated Ingredient 1, Updated Ingredient 2',
            'instructions': 'Updated instructions',
            'cooking_time': 45
        }

        # Send a POST request to update the recipe
        response = self.app.post(f'/recipes/{recipe_id}', data=updated_data)

        # Check if the response redirects to the recipes page after update
        self.assertEqual(response.status_code, 302)
        self.assertIn('/all_recipes', response.headers['Location'])

        # Check if the recipe is updated in the database
        updated_recipe = db.session.query(Recipe).get(recipe_id)
        self.assertIsNotNone(updated_recipe)
        self.assertEqual(updated_recipe.recipe_name, updated_data['recipe_name'])
        self.assertEqual(updated_recipe.ingredients, updated_data['ingredients'])
        self.assertEqual(updated_recipe.instructions, updated_data['instructions'])
        self.assertEqual(updated_recipe.cooking_time, updated_data['cooking_time'])


if __name__ == '__main__':
    unittest.main()
