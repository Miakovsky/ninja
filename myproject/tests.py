from django.test import Client, TestCase
from ninja.testing import TestClient
from .api import api, router, UserLogin
from .models import *
from django.contrib.auth.models import User
from django.urls import reverse
import json


class ProductTest(TestCase):
    fixtures = ['db.json']
    def setUp(self):
        self.client = Client()

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
        self.assertEqual(str(product), 'rat slayer')

    def test_get_products(self):
        response = self.client.get("/api/products")
        self.assertEqual(response.status_code, 200)

    def test_get_product(self):
        response = self.client.get("/api/product/2")
        print(response.json())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'id': 2, 'title': 'ratew', 'slug': 'rat', 'category_id': 1, 'description': 'very rat', 'price': 24.0})
    
    def test_get_products_filter(self):
        response = self.client.get("/api/products?min_price=30&max_price=40")
        print(response.json())
        self.assertEqual(response.status_code, 200)
    
    

class CategoryTest(TestCase):
    fixtures = ['db.json']
    def setUp(self):
        self.client = Client()

    def test_str(self):
        category = Category(
            title = "slay",
            slug = "slay",
        )
        self.assertEqual(str(category), 'slay')

    def test_get_cat(self):
        response = self.client.get("/api/categories")
        self.assertEqual(response.status_code, 200)


    def test_get_slay_cat(self):
        response = self.client.get("/api/category/slay")
        print(response.json())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'id': 5, 'title': 'slay', 'slug': 'slay'})


class RegisterTest(TestCase):
    fixtures = ['db.json']
    def setUp(self):
        self.client = Client()

    def test_register(self):
        payload = {
                    "username": "testtest",
                    "email": "testing@verytesting.com",
                    "password1": "123",
                    "password2": "123"
                    }

        json_object = json.dumps(payload, indent = 4) 
        response = self.client.post("/api/registration", content_type = 'application/json',  data=payload)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'success':True})


class LoginTest(TestCase):
    fixtures = ['db.json']
    def setUp(self):
        self.client = Client()

    def test_login(self):
        response = self.client.post("/api/login", content_type = 'application/json', data={"username": "admin","password": "admin"},follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'success':True})

    def test_get_user(self):
        response = self.client.post("/api/login", content_type = 'application/json', data={"username": "admin", "password": "admin"})
        response = self.client.get("/api/user")
        self.assertEqual(response.status_code, 200)

    def test_logout(self):
        response = self.client.post("/api/login", content_type = 'application/json', data={"username": "admin", "password": "admin"})
        response = self.client.post("/api/logout")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'success':True})

    def test_get_users(self):
        self.client.post("/api/login", content_type = 'application/json', data={"username": "admin", "password": "admin"})
        response = self.client.get("/api/users")
        self.assertEqual(response.status_code, 200)
    
    def test_get_users_no_auth(self):
        response = self.client.post("/api/login", content_type = 'application/json', data={"username": "test", "password": "test"})
        response = self.client.get("/api/users")
        self.assertEqual(response.status_code, 403)

    
class WishlistTest(TestCase):
    fixtures = ['db.json']
    def setUp(self):
        self.client = Client()

    def test_get_wl(self):
        self.client.post("/api/login", content_type = 'application/json', data={"username": "admin", "password": "admin"})
        response = self.client.get("/api/get_wishlist/1", follow=True)
        self.assertEqual(response.status_code, 200)

    def test_create_wl(self):
        self.client.post("/api/login", content_type = 'application/json', data={"username": "admin", "password": "admin"})
        response = self.client.post("/api/create_wishlist", content_type = 'application/json', data={"user": 1,"product": 2, "quantity":1})
        self.assertEqual(response.status_code, 200)

    def test_add_wl(self):
        self.client.post("/api/login", content_type = 'application/json', data={"username": "admin", "password": "admin"})
        response = self.client.put("/api/wishlist/add?wishlist_id=1")
        self.assertEqual(response.status_code, 200)

class OrderTest(TestCase):
    fixtures = ['db.json']
    def setUp(self):
        self.client = Client()

    def test_get_orders(self):
        self.client.post("/api/login", content_type = 'application/json', data={"username": "admin", "password": "admin"})
        response = self.client.get("/api/get_orders")
        self.assertEqual(response.status_code, 200)

    def test_get_order(self):
        self.client.post("/api/login", content_type = 'application/json', data={"username": "admin", "password": "admin"})
        response = self.client.get("/api/order/1", follow=True)
        self.assertEqual(response.status_code, 200)

    def test_get_order_items(self):
        self.client.post("/api/login", content_type = 'application/json', data={"username": "admin", "password": "admin"})
        response = self.client.get("/api/order/items/3", follow=True)
        self.assertEqual(response.status_code, 200)
        

    def test_change_status(self):
        self.client.post("/api/login", content_type = 'application/json', data={"username": "admin", "password": "admin"})
        response = self.client.put("/api/change_status?order_id=3&status_id=2")
        self.assertEqual(response.status_code, 200)