from django.http import HttpResponse
from django.test import Client, TestCase


class TestAppViews(TestCase):
    def setUp(self) -> None:
        self.client: Client = Client()

    def test_get_home_page(self) -> None:
        response: HttpResponse = self.client.get('/')
        self.assertTemplateUsed(response, 'index.html')

    def test_get_legal_notices(self) -> None:
        response: HttpResponse = self.client.get('/legal')
        self.assertTemplateUsed(response, 'legal_notice.html')

    def test_i18n_lang_fr(self) -> None:
        response: HttpResponse = self.client.get(
            '/', HTTP_ACCEPT_LANGUAGE='fr'
        )
        self.assertIn(b'Accueil', response.content)

    def test_i18n_lang_en(self) -> None:
        response: HttpResponse = self.client.get(
            '/', HTTP_ACCEPT_LANGUAGE='en'
        )
        self.assertIn(b'Home', response.content)
