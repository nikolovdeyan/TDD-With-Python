#pylint: disable=missing-docstring, invalid-name, line-too-long
from django.test import TestCase
from unittest import skip
from django.utils.html import escape
from lists.models import Item, List
from lists.forms import ItemForm, EMPTY_ITEM_ERROR

class HomePageTest(TestCase):

    def test__home_page__when_called__uses_home_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')

    def test__home_page__when_called__uses_item_form(self):
        response = self.client.get('/')
        self.assertIsInstance(response.context['form'], ItemForm)


class ListViewTest(TestCase):

    def post_invalid_input(self):
        list_ = List.objects.create()
        return self.client.post('/lists/{}/'.format(list_.id), data={'text': ''})

    def test__list_view__with_valid_request__uses_list_template(self):
        list_ = List.objects.create()
        response = self.client.get('/lists/{}/'.format(list_.id))
        self.assertTemplateUsed(response, 'list.html')

    def test__list_view__with_valid_list__displays_only_items_for_that_list(self):
        correct_list = List.objects.create()
        Item.objects.create(text='itemey 1', list=correct_list)
        Item.objects.create(text='itemey 2', list=correct_list)
        other_list = List.objects.create()
        Item.objects.create(text='other list item 1', list=other_list)
        Item.objects.create(text='other list item 2', list=other_list)

        response = self.client.get('/lists/{}/'.format(correct_list.id))

        self.assertContains(response, 'itemey 1')
        self.assertContains(response, 'itemey 2')
        self.assertNotContains(response, 'other list item 1')
        self.assertNotContains(response, 'other list item 2')

    def test__list_view__passes_correct_list_to_template(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()

        response = self.client.get('/lists/{}/'.format(correct_list.id))
        self.assertEqual(response.context['list'], correct_list)

    def test__list_view__with_POST_request__can_save_to_an_existing_list(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()

        self.client.post(
            '/lists/{}/'.format(correct_list.id),
            data={'text': 'A new item for an existing list'})

        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, 'A new item for an existing list')
        self.assertEqual(new_item.list, correct_list)

    def test__list_view__with_POST_request__redirects_to_list_view(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()

        response = self.client.post(
            '/lists/{}/'.format(correct_list.id),
            data={'text': 'A new item for an existing list'})

        self.assertRedirects(response, '/lists/{}/'.format(correct_list.id))

    def test__list_view__with_blank_input__uses_list_view_template(self):
        list_ = List.objects.create()
        response = self.client.post(
            '/lists/{}/'.format(list_.id),
            data={'text': ''})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'list.html')
        expected_error = escape("You can't have an empty list item")
        self.assertContains(response, expected_error)

    def test__list_view__with_invalid_input__doesnt_save_to_db(self):
        self.post_invalid_input()

        self.assertEqual(Item.objects.count(), 0)

    def test__list_view__with_invalid_input__renders_list_template(self):
        response = self.post_invalid_input()

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'list.html')

    def test__list_view__with_invalid_input__passes_form_to_template(self):
        response = self.post_invalid_input()

        self.assertIsInstance(response.context['form'], ItemForm)

    def test__list_view__with_invalud_input__shows_error_on_page(self):
        response = self.post_invalid_input()

        self.assertContains(response, escape(EMPTY_ITEM_ERROR))

    @skip
    def test__list_view__with_duplicate_item__shows_item_validation_error(self):
        list1 = List.objects.create()
        item1 = Item.objects.create(list=list1, text='foo')
        expected_error = escape("You've already got this in you list")

        response = self.client.post('/lists/{}/'.format(list1.id), data={'text': 'foo'})

        self.assertContains(response, expected_error)
        self.assertTemplateUsed(response, 'list.html')
        self.assertEqual(Item.objects.all().count(), 1)


class NewListTest(TestCase):

    def test__home_page__can_save_a_POST_request(self):
        self.client.post('/lists/new', data={'text': 'A new list item'})

        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, 'A new list item')

    def test__home_page__redirects_after_a_POST_request(self):
        response = self.client.post('/lists/new', data={'text': 'A new list item'})
        new_list = List.objects.first()
        self.assertRedirects(response, '/lists/{}/'.format(new_list.id))

    def test__home_page__with_invalid_input__renders_home_template(self):
        response = self.client.post('/lists/new', data={'text': ''})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test__home_page__with_invalid_input__shows_validation_errors(self):
        response = self.client.post('/lists/new', data={'text': ''})

        self.assertContains(response, escape(EMPTY_ITEM_ERROR))

    def test__home_page__with_invalid_input__passes_form_to_template(self):
        response = self.client.post('/lists/new', data={'text': ''})

        self.assertIsInstance(response.context['form'], ItemForm)

    def test__list_item__when_invalid__are_not_saved(self):
        self.client.post('/lists/new', data={'text': ''})

        self.assertEqual(List.objects.count(), 0)
        self.assertEqual(Item.objects.count(), 0)

