from django.db import models


class List(models.Model):
    objects = models.Manager()
    pass


class Item(models.Model):
    objects = models.Manager()
    text = models.TextField(default='')
    list = models.ForeignKey(List, default=None)
