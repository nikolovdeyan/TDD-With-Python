#pylint: disable=missing-docstring, invalid-name, line-too-long
from django.test import TestCase
from lists.forms import EMPTY_ITEM_ERROR, ItemForm

class ItemFormTest(TestCase):

    def test__item_form__when_created__renders_item_text_input(self):
        form = ItemForm()

        self.assertIn('placeholder="Enter a to-do item"', form.as_p())
        self.assertIn('class="form-control input-lg"', form.as_p())

    def test__item_form__when_passed_blank_items__validates(self):
        form = ItemForm(data={'text': ''})

        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['text'],
            [EMPTY_ITEM_ERROR])
