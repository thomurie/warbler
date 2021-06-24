"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_message_model.py


import os
from unittest import TestCase

from models import Likes, db, User, Message, Follows

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app

# Create our tables 
db.drop_all()
db.create_all()


class MessageModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        Message.query.delete()
        User.query.delete()

        self.client = app.test_client()

    def test_new_message(self):
        """Does basic model work?"""
        user1 = User(
            email="test1@test.com",
            username="testuser1",
            password="HASHED_PASSWORD")
        db.session.add(user1)
        db.session.commit()

        msg = Message(text = 'testing testing', user_id = user1.id)
        user1.messages.append(msg)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(msg.text, 'testing testing')
        self.assertEqual(msg.user_id, user1.id)

    def test_correct_message_details(self):
        """Verify removal of message removes it from user profile"""
        user1 = User(
            email="test1@test.com",
            username="testuser1",
            password="HASHED_PASSWORD")
        db.session.add(user1)
        db.session.commit()

        msg = Message(text = 'testing testing', user_id = user1.id)
        user1.messages.append(msg)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(msg.text, 'testing testing')

        db.session.delete(msg)
        db.session.commit()
        self.assertEqual(user1.messages, [])

    def test_likes_add(self):
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

        msg = Message(text = 'testing testing', user_id = user1.id)
        user1.messages.append(msg)
        db.session.commit()

        liked_message = Likes(user_id = user2.id, message_id = msg.id)
        db.session.add(liked_message)
        user2.likes.append(msg)
        db.session.commit()

        self.assertEqual(len(user2.likes), 1)

    def test_likes_remove(self):
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

        msg = Message(text = 'testing testing', user_id = user1.id)
        user1.messages.append(msg)
        db.session.commit()

        liked_message = Likes(user_id = user2.id, message_id = msg.id)
        db.session.add(liked_message)
        user2.likes.append(msg)
        db.session.commit()

        db.session.delete(liked_message)
        db.session.commit()

        self.assertEqual(len(user2.likes), 0)

    



