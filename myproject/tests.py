from django.test import TestCase
from ninja.testing import TestClient
from .api import api, router, UserLogin
from .models import *
from django.contrib.auth.models import User

class ProductTest(TestCase):
    def test_str(self):
        category = Category(title='slay', slug='slay')
        product = Product(
            id = 6,
            title = "rat slayer",
            slug = "rat-slayer",
            category_id = category,
            description = "this rat slayyyyyyyys frfr",
            price = 100,
        )
        print(str(product))
        self.assertEqual(str(product), 'rat slayer')

class CategoryTest(TestCase):
    def test_str(self):
        category = Category(
            title = "slay",
            slug = "slay",
        )
        print(str(category))
        self.assertEqual(str(category), 'slay')

    def test_get_cat(self):
        client = TestClient(router)
        response = self.client.get("/categories")
        self.assertEqual(response.status_code, 200)

        
'''
class LoginTest(TestCase):
    def test_login(self):
        client = TestClient(router)
        response = client.post("/login", data={
                                                "username": "admin",
                                                "password": "string"
                                                })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'success':True})
'''