"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


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

        db.session.commit()

    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

    def test_delete_message(self):
        """Can we delete a message?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp1 = c.post("/messages/new", data={"text": "Hello"})

            self.assertEqual(resp1.status_code, 302)

            msg = Message.query.first()
            
            self.assertEqual(msg.text, "Hello")

            resp2 = c.post(f"/messages/{msg.id}/delete", follow_redirects = True)

            self.assertIn(b"testuser", resp2.data)
    
    def test_logged_out_add_message(self):
        """When you’re logged out, are you prohibited from adding messages?"""
        with self.client as c:

            resp = c.post("/messages/new", data={"text": "Hello"}, follow_redirects = True)

            self.assertIn(b"Access unauthorized.", resp.data)


    def test_logged_out_delete_message(self):
        """When you’re logged out, are you prohibited from deleting messages?"""
        with self.client as c:
    
            resp = c.post("/messages/32/delete", follow_redirects = True)

            self.assertIn(b"Access unauthorized.", resp.data)
    
    def test_logged_in_add_as_other_user(self):
        """When you’re logged in, are you prohibiting from adding a message as another user?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 987659999

            resp = c.post("/messages/new", data={"text": "Hello"}, follow_redirects = True)

            self.assertIn(b"Access unauthorized.", resp.data)
    

    def test_logged_out_delete_other_users_msg(self):
        """When you’re logged in, are you prohibiting from deleting a message as another user?"""

        usr = User.signup(username= 'bad-user', email='baduser@gmail.com', password="Iambad!", image_url=None)
        usr.id = 987654

        db.session.add(usr)

        msg = Message(id=1234, text= 'test', user_id =self.testuser.id)

        db.session.add(msg)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 987654

            resp = c.post("/messages/1234/delete", follow_redirects = True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b"Access unauthorized.", resp.data)


    


