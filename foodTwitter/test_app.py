import unittest
from app import app, db, Recipe


class TestApp(unittest.TestCase):
    """
    Set up method executed before each test case.

    Configures the Flask application for testing by:
    - Setting the 'TESTING' configuration to True.
    - Using an in-memory SQLite database to isolate test data from the development or production databases.
    - Creating a test client to simulate HTTP requests to the application.
    - Pushing an application context to allow access to Flask's application and request contexts within the tests.
    - Creating all database tables defined in the SQLAlchemy models.

    This method ensures that each test case runs in a controlled environment with its own isolated database,
     preventing interference between tests and ensuring reproducibility.

    """

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        self.ctx = app.app_context()
        self.ctx.push()
        db.create_all()

    """
    Tear down method executed after each test case.

    Performs cleanup actions to reset the testing environment by:
    - Removing the current session from the database session registry to prevent session leakage and
     ensure data isolation between tests.
    - Dropping all database tables defined in the SQLAlchemy models to clean up any changes made during the test.
    - Popping the application context to clean up the application context stack and release associated resources.

    This method ensures that each test case leaves the testing environment in a clean and consistent state, 
    preventing side effects and ensuring the independence of subsequent tests.

    """

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    """
    Unit test for creating a recipe.

    Simulates the creation of a new recipe by sending a POST request to the '/recipes' endpoint with mock data.
    - Constructs a dictionary containing mock data for the recipe attributes.
    - Sends a POST request to the application with the mock data.
    - Asserts that the response status code is equal to 302, indicating a successful redirection 
    after creating the recipe.

    This test ensures that the creation of a recipe via the '/recipes' endpoint behaves as expected, 
    redirecting to the appropriate page upon successful creation.

    """

    def test_create_recipe(self):
        data = {
            'recipe_name': 'Test Recipe',
            'ingredients': 'Ingredient 1, Ingredient 2',
            'instructions': 'Test instructions',
            'cooking_time': 30
        }
        response = self.app.post('/recipes', data=data)
        self.assertEqual(response.status_code, 302)

    """
    Unit test for deleting a recipe.

    Simulates the deletion of a recipe by:
    - Creating a new recipe in the database.
    - Sending a POST request to the '/recipes/<recipe_id>/delete' endpoint to delete the created recipe.
    - Asserting that the response status code is equal to 302, indicating a successful redirection after deletion.
    - Checking if the response redirects to the '/all_recipes' page, as expected.
    - Verifying that the recipe is deleted from the database by querying for its absence.

    This test ensures that the deletion of a recipe via the '/recipes/<recipe_id>/delete' endpoint behaves correctly,
    redirecting to the appropriate page after deletion and removing the recipe from the database.

    """

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

    """
    Unit test for updating a recipe.

    Simulates the update of a recipe by:
    - Creating a new recipe in the database.
    - Sending a POST request to the '/recipes/<recipe_id>' endpoint with updated data.
    - Asserting that the response status code is equal to 302, indicating a successful redirection after update.
    - Checking if the response redirects to the '/all_recipes' page, as expected.
    - Verifying that the recipe is updated in the database by querying for the updated attributes.

    This test ensures that the update of a recipe via the '/recipes/<recipe_id>' endpoint behaves correctly,
    redirecting to the appropriate page after update and updating the recipe's attributes in the database.

    """

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
