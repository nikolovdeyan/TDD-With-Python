#pylint: disable=missing-docstring, invalid-name, line-too-long
from django.test import TestCase
from lists.forms import DUPLICATE_ITEM_ERROR, EMPTY_ITEM_ERROR, ItemForm, ExistingListItemForm
from lists.models import Item, List

class ItemFormTest(TestCase):

    def test__form_save(self):
        list_ = List.objects.create()
        form = ExistingListItemForm(for_list=list_, data={'text': 'hi'})
        new_item = form.save()

        self.assertEqual(new_item, Item.objects.all()[0])

    def test__new_list_form__when_created__renders_item_text_input(self):
        form = ItemForm()

        self.assertIn('placeholder="Enter a to-do item"', form.as_p())
        self.assertIn('class="form-control input-lg"', form.as_p())

    def test__new_list_form__with_passed_blank_item__renders_empty_item_error(self):
        form = ItemForm(data={'text': ''})

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['text'], [EMPTY_ITEM_ERROR])

    def test__new_list_form__with_passed_valid_item__saves_item_to_a_list(self):
        list_ = List.objects.create()
        form = ItemForm(data={'text': 'do me'})

        new_item = form.save(for_list=list_)

        self.assertEqual(new_item, Item.objects.first())
        self.assertEqual(new_item.text, 'do me')
        self.assertEqual(new_item.list, list_)


class ExistingListItemFormTest(TestCase):

    def test__existing_list_form__when_created__renders_item_text_input(self):
        list_ = List.objects.create()
        form = ExistingListItemForm(for_list=list_)

        self.assertIn('placeholder="Enter a to-do item"', form.as_p())

    def test__existing_list_form__with_passed_blank_item__renders_empty_item_error(self):
        list_ = List.objects.create()
        form = ExistingListItemForm(for_list=list_, data={'text': ''})

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['text'], [EMPTY_ITEM_ERROR])

    def test__existing_list_form__with_passed_valid_item__saves_item_to_a_list(self):
        list_ = List.objects.create()
        Item.objects.create(list=list_, text='no twins!')

        form = ExistingListItemForm(for_list=list_, data={'text': 'no twins!'})

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['text'], [DUPLICATE_ITEM_ERROR])
