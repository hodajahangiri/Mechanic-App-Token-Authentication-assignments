import unittest
from app import create_app
from app.models import db, PartDescriptions, Parts

class TestPartDescriptions(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TestingConfig')
        self.part_description1 = PartDescriptions(name="TestPartDesc", price=100.0, made_in="TestLand")
        self.part_description2 = PartDescriptions(name="RelatedPartDesc", price=150.0, made_in="RelatedLand")
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.part_description1)
            db.session.add(self.part_description2)
            db.session.commit()
            part_desc_id_1 = db.session.query(PartDescriptions.id).where(PartDescriptions.name=="TestPartDesc").first()[0]
            part_desc_id_2 = db.session.query(PartDescriptions.id).where(PartDescriptions.name=="RelatedPartDesc").first()[0]
            new_part_2 = Parts(desc_id=part_desc_id_2, serial_number="BP-001")
            db.session.add(new_part_2)
            db.session.commit()
            part_id = db.session.query(Parts.id).first()[0]
        self.part_desc_id_without_part = part_desc_id_1
        self.part_desc_id_with_part = part_desc_id_2
        self.client = self.app.test_client()

    def test_create_part_description(self):
        part_desc_payload = {"name": "Rotor", "price": 100.0, "made_in": "USA"}
        response = self.client.post("/part_descriptions", json=part_desc_payload)
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data["name"], part_desc_payload["name"])
        # Duplicate
        response_dup = self.client.post("/part_descriptions", json=part_desc_payload)
        self.assertEqual(response_dup.status_code, 400)
        self.assertIn("already exist", response_dup.get_json()["message"])
        # Validation error
        invalid_payload = {"price": 100.0, "made_in": "USA"}
        response_invalid = self.client.post("/part_descriptions", json=invalid_payload)
        self.assertEqual(response_invalid.status_code, 400)
        self.assertIn("error", response_invalid.get_json())

    def test_get_all_part_descriptions(self):
        response = self.client.get("/part_descriptions")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsInstance(data, list)
        self.assertEqual(data[0]["name"], "TestPartDesc")

    def test_get_all_descriptions_by_name(self):
        response = self.client.get("/part_descriptions/search_by_name?name=Test")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsInstance(data, list)
        self.assertEqual(data[0]["name"], "TestPartDesc")
        # No name param
        response_none_name = self.client.get("/part_descriptions/search_by_name")
        self.assertEqual(response_none_name.status_code, 200)
        self.assertIn("have to send the name", response_none_name.get_json()["message"])
        # Not found
        response_notfound = self.client.get("/part_descriptions/search_by_name?name=NotExist")
        self.assertEqual(response_notfound.status_code, 200)
        self.assertIn("no part description", response_notfound.get_json()["message"])

    def test_update_part_description(self):
        update_payload = {"name": "SpringUpdated", "price": 6.0, "made_in": "Italy"}
        response = self.client.put(f"/part_descriptions/{self.part_desc_id_without_part}", json=update_payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Successfully description with id", response.get_json()["message"])
        # Not found
        response_notfound = self.client.put("/part_descriptions/9999", json=update_payload)
        self.assertEqual(response_notfound.status_code, 404)
        self.assertIn("not found", response_notfound.get_json()["message"])

    def test_delete_part_description(self):
        response = self.client.delete(f"/part_descriptions/{self.part_desc_id_without_part}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Successfully deleted description", response.get_json()["message"])
        # Not found
        response_notfound = self.client.delete("/part_descriptions/9999")
        self.assertEqual(response_notfound.status_code, 404)
        self.assertIn("not found", response_notfound.get_json()["message"])
        # Not allowed to delete if related part exists
        response_related = self.client.delete(f"/part_descriptions/{self.part_desc_id_with_part}")
        self.assertEqual(response_related.status_code, 200)
        self.assertIn("can not delete", response_related.get_json()["message"])
