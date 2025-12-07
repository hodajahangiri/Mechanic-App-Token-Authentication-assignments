import unittest
from app import create_app
from app.models import db, Parts, PartDescriptions

class TestParts(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TestingConfig')
        # Create a part description for use in part creation
        new_part_desc = PartDescriptions(name="TestName", price=50.0, made_in="TestLand")
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(new_part_desc)
            db.session.commit()
            part_desc_id = db.session.query(PartDescriptions.id).first()[0]
            new_part = Parts(desc_id=part_desc_id, serial_number="BP-001")
            db.session.add(new_part)
            db.session.commit()
            part_id = db.session.query(Parts.id).first()[0]
        self.part_desc_id = part_desc_id
        self.part_id = part_id
        self.client = self.app.test_client()

    def test_create_part(self):
        part_payload = {
            "desc_id": self.part_desc_id,
            "serial_number": "BP-002"
        }
        response = self.client.post("/parts", json=part_payload)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("Successfully created", data["message"])

        # Test quantity > 1
        response_qty = self.client.post("/parts?qty=2", json=part_payload)
        self.assertEqual(response_qty.status_code, 200)
        data_qty = response_qty.get_json()
        self.assertIn("Successfully created 2 part(s)", data_qty["message"])

        # Test invalid quantity
        response_invalid_qty = self.client.post("/parts?qty=0", json=part_payload)
        self.assertEqual(response_invalid_qty.status_code, 400)
        data_invalid_qty = response_invalid_qty.get_json()
        self.assertIn("qty can not be 0 or negative", data_invalid_qty["error"])

    def test_create_part_duplicate_serial(self):
        Duplicate_part_payload = {
            "desc_id": self.part_desc_id,
            "serial_number": "BP-001"
        }
        # Try to create again with same serial
        response_dup = self.client.post("/parts", json=Duplicate_part_payload)
        self.assertEqual(response_dup.status_code, 200)
        data_dup = response_dup.get_json()
        self.assertIn("Successfully created", data_dup["message"])

    def test_get_all_parts(self):
        response = self.client.get("/parts")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsInstance(data, list)
        self.assertIn("part", data[0])
        self.assertIn("part_name", data[0])
        self.assertIn("part_price", data[0])

    def test_get_specific_part(self):
        response = self.client.get(f"/parts/{self.part_id}")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["serial_number"], "BP-001")
        # Test not found
        response_not_found = self.client.get("/parts/9999")
        self.assertEqual(response_not_found.status_code, 200)
        self.assertIn("part with part_id", response_not_found.get_json()["message"])

    def test_update_part(self):
        update_payload = {
            "desc_id": self.part_desc_id,
            "serial_number": "BP-001-NEW"
        }
        response = self.client.put(f"/parts/{self.part_id}", json=update_payload)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("Successfully part with id", data["message"])
        # Test duplicate serial number
        payload2 = {
            "desc_id": self.part_desc_id,
            "serial_number": "BP-006"
        }
        self.client.post("/parts", json=payload2)
        response_dup_serial = self.client.put(f"/parts/{self.part_id}", json=payload2)
        self.assertEqual(response_dup_serial.status_code, 400)
        self.assertIn("belongs to another product", response_dup_serial.get_json()["message"])
        # Test not found
        response_not_found = self.client.put("/parts/9999", json=update_payload)
        self.assertEqual(response_not_found.status_code, 404)
        self.assertIn("Part with id: 9999 not found", response_not_found.get_json()["message"])

    def test_delete_part(self):
        response = self.client.delete(f"/parts/{self.part_id}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Successfully deleted part", response.get_json()["message"])
        # Test not found
        response_not_found = self.client.delete("/parts/9999")
        self.assertEqual(response_not_found.status_code, 404)
        self.assertIn("Part with id: 9999 not found", response_not_found.get_json()["message"])
