#pylint: disable=missing-docstring, invalid-name, line-too-long
from django.test import TestCase
from django.core.exceptions import ValidationError
from lists.models import Item, List


class ItemModelTest(TestCase):

    def test__item_model__when_item_created__item_has_default_text(self):
        item = Item()

        self.assertEqual(item.text, '')

    def test__item_model__when_item_created__item_is_related_to_list(self):
        list_ = List.objects.create()
        item = Item()
        item.list = list_

        item.save()

        self.assertIn(item, list_.item_set.all())

    def test__item_model__when_passed_empty_list_item__raises_ValidationError(self):
        list_ = List.objects.create()
        item = Item(list=list_, text='')

        with self.assertRaises(ValidationError):
            item.save()
            item.full_clean()

    def test__item_model__when_duplicate_item_same_list__raises_ValidationError(self):
        list_ = List.objects.create()
        Item.objects.create(list=list_, text='foo')

        with self.assertRaises(ValidationError):
            item = Item(list=list_, text='foo')
            item.full_clean()

    def test__item_model__when_duplicate_item_differrent_list__items_are_valid(self):
        list1 = List.objects.create()
        list2 = List.objects.create()
        Item.objects.create(list=list1, text='foo')
        item = Item(list=list2, text='foo')
        item.full_clean()  # should not raise

    def test__item_model__when_items_in_list__items_are_correctly_ordered(self):
        list1 = List.objects.create()
        item1 = Item.objects.create(list=list1, text='item1')
        item2 = Item.objects.create(list=list1, text='item2')
        item3 = Item.objects.create(list=list1, text='item3')

        self.assertEqual(list(Item.objects.all()), [item1, item2, item3])

    def test__item_model__when_item_string_called__correct_string_returned(self):
        item = Item(text='some text')

        self.assertEqual(str(item), 'some text')


class ListModelTest(TestCase):

    def test__list_model__when_called__get_abosulte_url_returns_correct_url(self):
        list_ = List.objects.create()

        self.assertEqual(list_.get_absolute_url(), '/lists/{}/'.format(list_.id))
