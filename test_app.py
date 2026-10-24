import os
import tempfile
import unittest

os.environ["ADMIN_PASSWORD"] = "test-admin-password"
os.environ["FLASK_SECRET_KEY"] = "test-secret-key"
fd, dbpath = tempfile.mkstemp(suffix=".db")
os.close(fd)
os.environ["DATABASE_PATH"] = dbpath

import server

class BookReviewTests(unittest.TestCase):
    def setUp(self):
        self.client = server.app.test_client()

    def test_homepage(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_books_endpoint(self):
        response = self.client.get("/api/books")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.get_json()["books"]) >= 1)
        self.assertIn("desc", response.get_json()["books"][0])

    def test_review_validation(self):
        response = self.client.post("/api/reviews", json={"name":"Test","bookId":1,"rating":5,"text":"Too short"})
        self.assertEqual(response.status_code, 400)

    def test_admin_requires_login(self):
        response = self.client.get("/api/admin/summary")
        self.assertEqual(response.status_code, 401)

    def test_admin_login(self):
        response = self.client.post("/admin/login", json={"password":"test-admin-password"})
        self.assertEqual(response.status_code, 200)
        response = self.client.get("/api/admin/summary")
        self.assertEqual(response.status_code, 200)
        self.assertIn("subscribers", response.get_json())

    def test_newsletter_subscription_and_duplicate(self):
        response = self.client.post("/api/newsletter", json={"email":"Reader@example.com"})
        self.assertEqual(response.status_code, 201)
        response = self.client.post("/api/newsletter", json={"email":"reader@example.com"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("already subscribed", response.get_json()["message"])

    def test_newsletter_validation(self):
        response = self.client.post("/api/newsletter", json={"email":"not-an-email"})
        self.assertEqual(response.status_code, 400)

if __name__ == "__main__":
    unittest.main()
