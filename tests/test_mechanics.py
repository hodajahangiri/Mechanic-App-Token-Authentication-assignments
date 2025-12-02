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
        self.wrong_token = encode_token(1, "customer")
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

    def test_login(self):
        login_credentials = { 
            "email": "tester@email.com",
            "password": "1234"
        }
        response = self.client.post('/mechanics/login', json=login_credentials)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], "Successfully logged in. Welcome FirstTest")
        self.assertIn("token", response.json)
    
    # Negative check
    def test_invalid_email_or_pass_login(self):
        login_credentials = { 
            "email": "tester@email.com",
            "password": "12345"
        }
        response = self.client.post('/mechanics/login', json=login_credentials)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["error message"], "Invalid email or password.")

    def test_read_mechanics(self):
        response = self.client.get('/mechanics')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json[0]['email'], "tester@email.com")
        self.assertEqual(response.json[0]['first_name'], "FirstTest")
    
    def test_read_mechanic(self):
        headers = {
            "Authorization" : "Bearer " + self.token
        }
        response = self.client.get('/mechanics/profile', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['first_name'], "FirstTest")
        self.assertEqual(response.json['email'], "tester@email.com")
    
    def test_unauthorized_read_mechanic(self):
        response = self.client.get('/mechanics/profile')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json['error'], "token missing from authorization headers") 

    def test_delete_mechanic(self):
        headers = {
            "Authorization" : "Bearer " + self.token
        }
        response = self.client.delete('/mechanics', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], "Successfully deleted mechanic with id: 1") 

    def test_unauthorized_delete_mechanic(self):
        response = self.client.delete('/mechanics')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json['error'], "token missing from authorization headers") 

    def test_invalid_token_delete_mechanic(self):
        headers = {
            "Authorization" : "Bearer " + "123asdasd"
        }
        response = self.client.delete('/mechanics', headers=headers)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json['message'], "invalid token") 

    def test_update_mechanic(self):
        headers = {
            "Authorization" : "Bearer " + self.token
        }
        mechanic_payload = {
            "first_name": "FirstTester",
            "last_name": "LastTester",
            "email": "new_test@email.com",
            "password" : "12345",
            "phone": "+14082222222",
            "salary" : 4500.99
        }
        response = self.client.put('/mechanics', headers=headers, json=mechanic_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], "Successfully mechanic with id: 1 updated.")

    def test_wrong_token_update_mechanic(self):
        headers = {
            "Authorization" : "Bearer " + self.wrong_token
        }
        mechanic_payload = {
            "first_name": "FirstTest",
            "last_name": "LastTester",
            "email": "new_test@email.com",
            "password" : "12345",
            "phone": "+14082222222",
            "salary" : 4500.99
        }
        response = self.client.put('/mechanics', headers=headers, json=mechanic_payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['message'], "customer is not allowed.")
    
    def test_invalid_data_update_mechanic(self):
        headers = {
            "Authorization" : "Bearer " + self.token
        }
        mechanic_payload = {
            "last_name": "LastTester",
            "email": "new_test@email.com",
            "password" : "12345",
            "phone": "+14082222222",
            "salary" : 4500.99
        }
        response = self.client.put('/mechanics', headers=headers, json=mechanic_payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn('first_name', response.json['error message'])

    def test_read_mechanic_service_tickets(self):
        headers = {
            "Authorization" : "Bearer " + self.token
        }
        response = self.client.get('/mechanics/service_tickets',headers=headers)
        self.assertEqual(response.status_code, 200)
        
    def test_get_hard_work_mechanic(self):
        response = self.client.get('/mechanics/hard_work_mechanic')
        self.assertEqual(response.status_code, 200)
        self.assertIn('tickets_count',response.json)
        self.assertEqual(response.json['mechanic']['first_name'],'FirstTest')

    def test_get_sorted_mechanic_list_by_work(self):
        response = self.client.get('/mechanics/sort_by_work')
        self.assertEqual(response.status_code, 200)
        self.assertIn('tickets_count',response.json[0])
        self.assertEqual(response.json[0]['mechanic']['first_name'],'FirstTest')
    
