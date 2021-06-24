"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data
db.drop_all()
db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        User.query.delete()

        self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work?"""

        u = User.signup(
                username="testuser1",
                password="HASHED_PASSWORD",
                email="test@test.com",
                image_url= User.image_url.default.arg,
            )
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_user_following(self):
        user1 = User(
            email="test1@test.com",
            username="testuser1",
            password="HASHED_PASSWORD")
        user2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD")
        
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()

        user1.following.append(user2)
        db.session.commit()

        self.assertEqual(user1.is_following(user2), True)

        db.session.delete(user2)
        db.session.commit()

        self.assertEqual(user1.is_following(user2), False)

    def test_user_followed(self):
        user1 = User(
            email="test1@test.com",
            username="testuser1",
            password="HASHED_PASSWORD")
        user2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD")
        
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()

        user2.following.append(user1)
        db.session.commit()

        self.assertEqual(user1.is_followed_by(user2), True)

        db.session.delete(user2)
        db.session.commit()

        self.assertEqual(user1.is_followed_by(user2), False)

    def test_user_authenticate_success(self):
        u = User.signup(
                username="testuser1",
                password="HASHED_PASSWORD",
                email="test@test.com",
                image_url= User.image_url.default.arg,
            )
        db.session.commit()

        self.assertEqual(u.authenticate('testuser1', "HASHED_PASSWORD"), u)

    
    def test_user_authenticate_failed(self):
        u = User.signup(
                username="testuser1",
                password="HASHED_PASSWORD",
                email="test@test.com",
                image_url= User.image_url.default.arg,
            )
        db.session.commit()
        self.assertEqual(u.authenticate('NOT_THE_testuser1', "HASHED_PASSWORD"), False)

        self.assertEqual(u.authenticate('testuser1', "NOT_THE_HASHED_PASSWORD"), False)

