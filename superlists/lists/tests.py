from django.test import TestCase

class HomePageTest(TestCase):

    def test__uses_home_template(self):
        response = self.client.get('/')

        self.assertTemplateUsed(response, 'home.html')
