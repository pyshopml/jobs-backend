from django.db import models
from django.urls import reverse


class Vacancy(models.Model):
    title = models.CharField(max_length=128)
    description = models.TextField(max_length=1000)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('api:vacancies:vacancy-detail', kwargs={'pk': self.pk})
