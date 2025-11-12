from django.urls import resolve
from django.test import TestCase
from store.views import index
from django.http import HttpResponse, HttpRequest

# Create your tests here.


class WelcomePageTest(TestCase):

    def test_root_url_resolves_to_welcome_page_view(self):
        found = resolve('/')
        self.assertEqual(found.func, index)

    def test_welcome_page_returns_correct_html(self):
        request = HttpRequest()
        response = index(request)
        html = response.content.decode('utf8')
        message = "Bienvenue sur le comptoir local de Paris Saclay!"
        self.assertTrue(html==message)
