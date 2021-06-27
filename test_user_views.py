"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from flask import g, dologin, 
from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        
        self.testuser2 = User.signup(username="testuser2",
                                    email="test2@test.com",
                                    password="testuser2",
                                    image_url=None)

        db.session.commit()

    def test_loggedin_see_follow(self):
        """Can we see followers and following of other users while logged in"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

                resp = c.get(f"/users/{self.testuser2.id}/following", follow_redirects=True)
            
                self.assertEqual(resp.status_code, 200)

                self.assertIn(b"testuser2",resp.data)

     def test_add_message_logged_ou(self):
        """Can use add a message logged out?"""

        with self.client as c:

            resp = c.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)
            print(resp)

            # Make sure it redirects
            self.assertEqual(resp.status_code, 200)

            self.assertIn(b'Sign up now to get your own personalized timeline!',resp.data)