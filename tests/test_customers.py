import unittest
from app import create_app
from app.models import Customers, db
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.auth import encode_token

class TestMechanics(unittest.TestCase):

    #Runs before each test_method
    def setUp(self):
        self.app = create_app('TestingConfig') #Create a testing version of my app for these testcases
        self.customer = Customers(first_name="FirstTest", last_name="LastTest", email="tester@email.com", password=generate_password_hash('1234'), phone="+19999999", address="Test Street")
        with self.app.app_context():
            db.drop_all() #removing any lingering tables
            db.create_all() #creating fresh tables for another round of testing
            db.session.add(self.customer)
            db.session.commit()
        self.token = encode_token(1, "customer") #encoding a token for my starter designed mechanic 
        self.wrong_token = encode_token(1, "mechanic")
        self.client = self.app.test_client()

    def test_create_customer(self):
            # Valid customer creation
            customer_payload = {
                "first_name": "FirstTest",
                "last_name": "LastTest",
                "email": "test@email.com",
                "password": "12345",
                "phone": "+1234567890",
                "address": "123 Test St"
            }
            response = self.client.post("/customers", json=customer_payload)
            self.assertEqual(response.status_code, 201)
            data = response.get_json()
            self.assertIn("customer_data", data)
            self.assertIn("token", data)
            self.assertEqual(data["customer_data"]["email"], customer_payload["email"])

            # Duplicate email
            response_dup = self.client.post("/customers", json=customer_payload)
            self.assertEqual(response_dup.status_code, 400)
            data_dup = response_dup.get_json()
            self.assertIn("error", data_dup)
            self.assertIn(customer_payload["email"], data_dup["error"])

            # Validation error (missing required field)
            invalid_payload = {
                "first_name": "NoEmail",
                "last_name": "LastTest",
                "password": "12345",
                "phone": "+1234567890",
                "address": "123 Test St"
            }
            response_invalid = self.client.post("/customers", json=invalid_payload)
            self.assertEqual(response_invalid.status_code, 400)
            data_invalid = response_invalid.get_json()
            self.assertIn("error message", data_invalid)