import unittest
from app import create_app
from app.models import db, Customers, Mechanics, Parts, PartDescriptions, Service_tickets
from werkzeug.security import generate_password_hash
from app.utils.auth import encode_token

class TestServiceTickets(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TestingConfig')
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            # Create a customer
            self.customer = Customers(first_name="FirstTestCustomer", last_name="LastTestCustomer", email="custmer_test@email.com", password=generate_password_hash('1234'), phone="+1234567890")
            db.session.add(self.customer)
            db.session.commit()
            self.customer_id = self.customer.id
            # Create a mechanic
            self.mechanic = Mechanics(first_name="FirstTestMechanic", last_name="LastTestMechanic", email="mechanic_test@email.com", password=generate_password_hash('1234'), phone="+1234567890", salary=1000)
            db.session.add(self.mechanic)
            db.session.commit()
            self.mechanic_id = self.mechanic.id
            # Create a part description and part
            self.part_desc = PartDescriptions(name="TestPartDescription", price=10.0, made_in="TestLand")
            db.session.add(self.part_desc)
            db.session.commit()
            self.part = Parts(desc_id=self.part_desc.id, serial_number="P-001")
            db.session.add(self.part)
            db.session.commit()
            self.part_id = self.part.id
            #Create a service ticket 
            self.service_ticket = Service_tickets(service_desc="TestDesc", price=100.0, VIN="VIN000", customer_id=self.customer_id)
            db.session.add(self.service_ticket)
            db.session.commit()
            self.service_ticket_id = self.service_ticket.id
        self.customer_token = encode_token(self.customer_id, "customer")
        self.mechanic_token = encode_token(self.mechanic_id, "mechanic")
        self.client = self.app.test_client()

    def test_create_service_ticket(self):
        headers = {"Authorization": f"Bearer {self.customer_token}"}
        service_ticket_payload = {
            "service_desc": "Oil change", 
            "price": 50.0, 
            "VIN": "VIN123"
            }
        response = self.client.post("/service_tickets", json=service_ticket_payload, headers=headers)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["service_desc"], "Oil change")
        # Unauthorized
        response_unauth = self.client.post("/service_tickets", json=service_ticket_payload)
        self.assertEqual(response_unauth.status_code, 401)
        # Wrong role
        wrong_headers = {"Authorization": f"Bearer {self.mechanic_token}"}
        response_wrong = self.client.post("/service_tickets", json=service_ticket_payload, headers=wrong_headers)
        self.assertEqual(response_wrong.status_code, 400)
        self.assertIn("not allowed", response_wrong.get_json()["message"])

    def test_read_service_tickets(self):
        response = self.client.get("/service_tickets")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.get_json(), list)
        self.assertEqual(response.json[0]["service_desc"], "TestDesc")

    def test_read_service_ticket(self):
        response = self.client.get(f"/service_tickets/{self.service_ticket_id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["service_desc"], "TestDesc")
        # Not found
        response_nf = self.client.get("/service_tickets/9999")
        self.assertEqual(response_nf.status_code, 404)

    def test_update_service_ticket(self):
        update_payload = {"service_desc": "Updated", "price": 25.0, "VIN": "VIN789"}
        response = self.client.put(f"/service_tickets/{self.service_ticket_id}", json=update_payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Successfully service_ticket with id", response.get_json()["message"])
        # Not found
        response_nf = self.client.put("/service_tickets/9999", json=update_payload)
        self.assertEqual(response_nf.status_code, 404)

    def test_delete_service_ticket(self):
        response = self.client.delete(f"/service_tickets/{self.service_ticket_id}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Successfully deleted service_ticket", response.get_json()["message"])
        # Not found
        response_nf = self.client.delete("/service_tickets/9999")
        self.assertEqual(response_nf.status_code, 404)

    def test_read_service_ticket_mechanics(self):
        response = self.client.get(f"/service_tickets/mechanics/{self.service_ticket_id}")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.get_json(), list)
        # Not found
        response_nf = self.client.get("/service_tickets/mechanics/9999")
        self.assertEqual(response_nf.status_code, 404)

    def test_add_and_remove_mechanic_to_service_ticket(self):
        # Add mechanic
        response = self.client.put(f"/service_tickets/{self.service_ticket_id}/assign-mechanic/{self.mechanic_id}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("added to service_ticket", response.get_json()["message"])
        # Add again (should say already added)
        response_dup = self.client.put(f"/service_tickets/{self.service_ticket_id}/assign-mechanic/{self.mechanic_id}")
        self.assertEqual(response_dup.status_code, 200)
        self.assertIn("already added", response_dup.get_json()["message"])
        # Remove mechanic
        response_rm = self.client.put(f"/service_tickets/{self.service_ticket_id}/remove-mechanic/{self.mechanic_id}")
        self.assertEqual(response_rm.status_code, 200)
        self.assertIn("removed from service_ticket", response_rm.get_json()["message"])
        # Remove again (should say not in)
        response_rm2 = self.client.put(f"/service_tickets/{self.service_ticket_id}/remove-mechanic/{self.mechanic_id}")
        self.assertEqual(response_rm2.status_code, 200)
        self.assertIn("is not in service_ticket", response_rm2.get_json()["message"])

    def test_add_and_remove_part_to_service_ticket(self):
        # Add part
        response = self.client.put(f"/service_tickets/{self.service_ticket_id}/add_part/{self.part_id}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("added to service_ticket", response.get_json()["message"])
        # Add again (should say already added)
        response_dup = self.client.put(f"/service_tickets/{self.service_ticket_id}/add_part/{self.part_id}")
        self.assertEqual(response_dup.status_code, 200)
        self.assertIn("already added", response_dup.get_json()["message"])
        # Remove part
        response_rm = self.client.put(f"/service_tickets/{self.service_ticket_id}/remove_part/{self.part_id}")
        self.assertEqual(response_rm.status_code, 200)
        self.assertIn("removed from service_ticket", response_rm.get_json()["message"])
        # Remove again (should say not in)
        response_rm2 = self.client.put(f"/service_tickets/{self.service_ticket_id}/remove_part/{self.part_id}")
        self.assertEqual(response_rm2.status_code, 200)
        self.assertIn("is not in service_ticket", response_rm2.get_json()["message"])
