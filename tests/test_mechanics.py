import unittest
from app import create_app
from app.models import Mechanics, db
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.auth import encode_token

class TestMechanics(unittest.TestCase):

    #Runs before each test_method
    def setUp(self):
        self.app = create_app('TestingConfig') #Create a testing version of my app for these testcases
        self.mechanic = Mechanics(first_name="FirstTest", last_name="LastTest", email="tester@email.com", password=generate_password_hash('1234'), phone="+19999999", salary=00.00)
        with self.app.app_context():
            db.drop_all() #removing any lingering tables
            db.create_all() #creating fresh tables for another round of testing
            db.session.add(self.mechanic)
            db.session.commit()
        self.token = encode_token(1, "mechanic") #encoding a token for my starter designed mechanic 
        self.client = self.app.test_client() #creates a test client that will send requests to our API
    
    def test_create_mechanic(self):
        mechanic_payload = {
            "first_name": "FirstTest",
            "last_name": "LastTest",
            "email": "test@email.com",
            "password" : "12345",
            "phone": "+14082222222",
            "salary" : 4000.99
        }

        response = self.client.post('/mechanics', json=mechanic_payload) #sending a test POST request using our test_client and including a JSON body
        self.assertEqual(response.status_code, 201) 
        self.assertEqual(response.json['mechanic_data']['first_name'], "FirstTest")
        self.assertTrue(check_password_hash(response.json['mechanic_data']['password'], '12345'))
        self.assertEqual(response.json['mechanic_data']['last_name'], "LastTest")
        self.assertEqual(response.json['mechanic_data']['email'], "test@email.com")
        self.assertEqual(response.json['mechanic_data']['phone'], "+14082222222")
        self.assertEqual(response.json['mechanic_data']['salary'], 4000.99)
        self.assertIsNone(response.json['mechanic_data']['address'])

    # Negative check
    def test_invalid_create_mechanic(self):
        mechanic_payload = {
            "last_name": "LastTest",
            "email": "test@email.com",
            "password" : "12345",
            "phone": "+14082222222",
            "salary" : 4000.99
        }
        response = self.client.post('/mechanics', json=mechanic_payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn('first_name', response.json['error message'])

    def test_non_unique_email_create_mechanic(self):
        mechanic_payload = {
            "first_name": "FirstTest",
            "last_name": "LastTest",
            "email": "tester@email.com",
            "password" : "12345",
            "phone": "+14082222222",
            "salary" : 4000.99
        }
        response = self.client.post('/mechanics', json=mechanic_payload)
        self.assertEqual(response.status_code, 400)