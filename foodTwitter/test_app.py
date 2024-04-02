import unittest
from app import app, db


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


if __name__ == '__main__':
    unittest.main()
