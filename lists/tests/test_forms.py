#pylint: disable=missing-docstring, invalid-name, line-too-long
from django.test import TestCase
from lists.forms import EMPTY_ITEM_ERROR, ItemForm
from lists.models import Item, List

class ItemFormTest(TestCase):
    def test__item_form__when_created__renders_item_text_input(self):
        form = ItemForm()

        self.assertIn('placeholder="Enter a to-do item"', form.as_p())
        self.assertIn('class="form-control input-lg"', form.as_p())

    def test__item_form__with_passed_blank_item__renders_empty_item_error(self):
        form = ItemForm(data={'text': ''})

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['text'], [EMPTY_ITEM_ERROR])

    def test__item_form__with_passed_valid_item__saves_item_to_a_list(self):
        list_ = List.objects.create()
        form = ItemForm(data={'text': 'do me'})

        new_item = form.save(for_list=list_)

        self.assertEqual(new_item, Item.objects.first())
        self.assertEqual(new_item.text, 'do me')
        self.assertEqual(new_item.list, list_)
