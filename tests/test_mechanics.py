import unittest
from app import create_app
from app.models import Mechanics, db
from werkzeug.security import generate_password_hash
from app.utils.auth import encode_token

class TestMechanics(unittest.TestCase):

    #Runs before each test_method
    def setUp(self):
        self.app = create_app('TestingConfig') #Create a testing version of my app for these testcases
        self.mechanic = Mechanics(first_name="Test", last_name="lastTest", email="tester@email.com", password=generate_password_hash('1234'), phone="+19999999", salary=00.00)
        with self.app.app_context():
            db.drop_all() #removing any lingering tables
            db.create_all() #creating fresh tables for another round of testing
            db.session.add(self.mechanic)
            db.session.commit()
        self.token = encode_token(1, "mechanic") #encoding a token for my starter designed mechanic 
        self.client = self.app.test_client() #creates a test client that will send requests to our API