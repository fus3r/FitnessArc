from django.test import TestCase

# Create your tests here.
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Conversation, Message
from .views import _get_or_create_private_conversation


class ConversationModelTests(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user("alice", password="pwd12345")
        self.bob = User.objects.create_user("bob", password="pwd12345")

    def test_get_or_create_private_conversation_is_idempotent(self):
        """
        Creation d'une conversation entre deux utilisateurs.
        """
        conv1 = _get_or_create_private_conversation(self.alice, self.bob)
        conv2 = _get_or_create_private_conversation(self.alice, self.bob)

        self.assertEqual(Conversation.objects.count(), 1)
        self.assertEqual(conv1.id, conv2.id)
        self.assertEqual(
            set(conv1.participants.all()),
            {self.alice, self.bob}
        )


class MessagingViewsTests(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user("alice", password="pwd12345")
        self.bob = User.objects.create_user("bob", password="pwd12345")

    def test_send_message_creates_message(self):
        """
        Creation du message
        """
        self.client.login(username="alice", password="pwd12345")

        url = reverse("messaging:conversation_with", args=[self.bob.username])
        resp = self.client.post(url, {"text": "Hello Bob!"}, follow=True)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Message.objects.count(), 1)

        msg = Message.objects.first()
        self.assertEqual(msg.sender, self.alice)
        self.assertEqual(msg.text, "Hello Bob!")
        self.assertEqual(
            set(msg.conversation.participants.all()),
            {self.alice, self.bob}
        )

    def test_open_conversation_marks_other_messages_as_read(self):
        """
        Marque comme lu quand on ouvre le message.
        """
        conv = _get_or_create_private_conversation(self.alice, self.bob)
        msg = Message.objects.create(
            conversation=conv,
            sender=self.bob,
            text="Unseen message",
            is_read=False,
        )

        # Alice ouvre la conversation
        self.client.login(username="alice", password="pwd12345")
        url = reverse("messaging:conversation_with", args=[self.bob.username])
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 200)

        msg.refresh_from_db()
        self.assertTrue(msg.is_read)

    def test_inbox_lists_user_conversations(self):
        """
        Liste des conversations auquels le user participe
        """
        conv_ab = _get_or_create_private_conversation(self.alice, self.bob)
        eve = User.objects.create_user("eve", password="pwd12345")
        conv_be = _get_or_create_private_conversation(self.bob, eve)

        self.client.login(username="alice", password="pwd12345")
        resp = self.client.get(reverse("messaging:inbox"))

        self.assertEqual(resp.status_code, 200)
        conversations = list(resp.context["conversations"])

        # Alice ne voit que ses conversations
        self.assertEqual(conversations, [conv_ab])
