import unittest
from app import create_app
from app.models import Customers, db
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.auth import encode_token

class TestCustomers(unittest.TestCase):
    #Runs before each test_method
    def setUp(self):
        self.app = create_app('TestingConfig') #Create a testing version of my app for these testcases
        self.customer = Customers(first_name="FirstTest", last_name="LastTest", email="tester@email.com", password=generate_password_hash('1234'), phone="+19999999", address="Test Street")
        with self.app.app_context():
            db.drop_all() #removing any lingering tables
            db.create_all() #creating fresh tables for another round of testing
            db.session.add(self.customer)
            db.session.commit()
        self.token = encode_token(1, "customer") #encoding a token for my starter designed customer 
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
        self.assertTrue(check_password_hash(data["customer_data"]["password"], customer_payload["password"]))

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

    def test_login_customer(self):
        login_credentials = { 
        "email": "tester@email.com",
        "password": "1234"
        }
        # Successful login
        response = self.client.post("/customers/login", json=login_credentials)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("token", data)
        self.assertIn("Successfully logged in", data["message"])
        # Invalid password
        response_invalid = self.client.post("/customers/login", json={"email": login_credentials["email"], "password": "wrongpass"})
        self.assertEqual(response_invalid.status_code, 400)
        data_invalid = response_invalid.get_json()
        self.assertIn("Invalid email or password.", data_invalid["error message"])
        # Nonexistent email
        response_nonexistent = self.client.post("/customers/login", json={"email": "notfound@email.com", "password": "any"})
        self.assertEqual(response_nonexistent.status_code, 400)
        data_nonexistent = response_nonexistent.get_json()
        self.assertIn("Invalid email or password.", data_nonexistent["error message"])

    def test_read_customers(self):
        response = self.client.get("/customers")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsInstance(data, list)
        self.assertEqual(response.json[0]['email'], "tester@email.com")
        self.assertEqual(response.json[0]['first_name'], "FirstTest")

    def test_read_customer_profile(self):
        headers = {
        "Authorization" : "Bearer " + self.token
        }
        response = self.client.get("/customers/profile", headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("email", data)
        self.assertEqual(data["email"], "tester@email.com")
        #Test unauthorized access to customer profile
        unauthorized_response = self.client.get('/customers/profile')
        self.assertEqual(unauthorized_response.status_code, 401)
        self.assertEqual(unauthorized_response.json['error'], "token missing from authorization headers")
        
    def test_update_customer(self):
        headers = {
            "Authorization" : "Bearer " + self.token
        }
        # Create and login customer
        update_payload = {
            "first_name": "FirstTester",
            "last_name": "LastTester",
            "email": "new_test@email.com",
            "password" : "12345",
            "phone": "+14082222222",
            "address": "123 Test St"
        }
        response = self.client.put("/customers", json=update_payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("Successfully customer with id", data["message"])

        # Test token with wrong role
        wrong_role_headers = {
            "Authorization" : "Bearer " + self.wrong_token
        }
        wrong_role_response = self.client.put("/customers", json=update_payload, headers=wrong_role_headers)
        self.assertEqual(wrong_role_response.status_code, 400)
        self.assertEqual(wrong_role_response.json['message'], "mechanic is not allowed.")
        
    def test_delete_customer(self):
        headers = {
            "Authorization" : "Bearer " + self.token
        }
            
        response = self.client.delete("/customers", headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("Successfully deleted customer", data["message"])

        #Test unauthorized delete attempt
        unauthorized_response = self.client.delete('/customers')
        self.assertEqual(unauthorized_response.status_code, 401)
        self.assertEqual(unauthorized_response.json['error'], "token missing from authorization headers")

        # Test invalid token delete attempt
        invalid_headers = {
            "Authorization" : "Bearer " + "123asdasd"
        }
        invalid_token_response = self.client.delete('/customers', headers=invalid_headers)
        self.assertEqual(invalid_token_response.status_code, 401)
        self.assertEqual(invalid_token_response.json['message'], "invalid token")

    def test_read_customer_service_tickets(self):
        headers = {
            "Authorization" : "Bearer " + self.token
        }
        response = self.client.get("/customers/service_tickets", headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsInstance(data, list)

    def test_search_by_email(self):
        response = self.client.get("/customers/search_by_email?email=test")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsInstance(data, list)