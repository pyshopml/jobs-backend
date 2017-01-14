from django.db import models


class Vacancy(models.Model):
    title = models.CharField(max_length=128)
    description = models.TextField(max_length=1000)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)
