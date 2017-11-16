#pylint: disable=missing-docstring
from django.db import models
from django.core.urlresolvers import reverse


class List(models.Model):
    objects = models.Manager()

    def get_absolute_url(self):
        return reverse('view_list', args=[self.id])


class Item(models.Model):
    objects = models.Manager()
    text = models.TextField(default='')
    list = models.ForeignKey(List, default=None)

    class Meta:
        ordering = ('id',)
        unique_together = ('list', 'text')

    def __str__(self):
        return self.text
