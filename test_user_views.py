"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py


import os
from typing import Text
from unittest import TestCase

from werkzeug import test

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for user pages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        User.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

    def test_view_user(self):
        """Can we see the user detail page?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id


            resp = c.get(f"/users/{self.testuser.id}")

            self.assertEqual(resp.status_code, 200)

            self.assertIn(b"testuser", resp.data)

    def test_view_others_followers_logged_in(self):
        """When you’re logged in, can you see the follower pages for any user?"""

        testuser2 = User.signup(username= 'testuser2', email='testuser2@gmail.com', password="1234567", image_url=None)
        testuser2.id = 222222

        db.session.add(testuser2)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get(f"/users/{testuser2.id}/followers", follow_redirects = True)
            self.assertEqual(resp.status_code, 200)
    
    def test_view_others_following_logged_in(self):
        """When you’re logged in, can you see the following pages for any user?"""

        testuser2 = User.signup(username= 'testuser2', email='testuser2@gmail.com', password="1234567", image_url=None)
        testuser2.id = 222222

        db.session.add(testuser2)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 222222

            resp = c.get(f"/users/{self.testuser.id}/following", follow_redirects = True)
            self.assertEqual(resp.status_code, 200)


    def test_view_others_followers_logged_out(self):
        """When you’re logged out, are you disallowed from visiting a user’s follower pages?"""
         
        testuser2 = User.signup(username= 'testuser2', email='testuser2@gmail.com', password="1234567", image_url=None)
        testuser2.id = 222222

        db.session.add(testuser2)
        db.session.commit()

        with self.client as c:

            resp = c.get(f"/users/{testuser2.id}/followers", follow_redirects = True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b"Access unauthorized.", resp.data)
    
    def test_view_others_following_logged_out(self):
        """When you’re logged out, are you disallowed from visiting a user’s following pages?"""

        testuser2 = User.signup(username= 'testuser2', email='testuser2@gmail.com', password="1234567", image_url=None)
        testuser2.id = 222222

        db.session.add(testuser2)
        db.session.commit()

        with self.client as c:

            resp = c.get(f"/users/{testuser2.id}/following", follow_redirects = True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b"Access unauthorized.", resp.data)


    def test_home_logged_in(self):
        """When you’re logged out, are you prohibited from deleting messages?"""
        
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
    
            resp = c.get("/", follow_redirects = True)

            self.assertEqual(resp.status_code, 200) 

            self.assertIn(b"Messages", resp.data)
            self.assertIn(b"Followers", resp.data)
            self.assertIn(b"Following", resp.data)
    