from django.db import models
from django.urls import reverse


class Tag(models.Model):
    title = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.title


class Category(models.Model):
    title = models.CharField(max_length=128, unique=True)
    parent = models.ForeignKey('self', null=True, blank=True,
                               on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Vacancy(models.Model):
    title = models.CharField(max_length=128)
    description = models.TextField(max_length=1000)
    salary_min = models.PositiveIntegerField(null=True, blank=True)
    salary_max = models.PositiveIntegerField(null=True, blank=True)
    location_city = models.CharField(max_length=128, null=True, blank=True)
    location_country = models.CharField(max_length=128, null=True, blank=True)
    keywords = models.ManyToManyField(Tag)
    busyness = models.PositiveSmallIntegerField(null=True, blank=True)
    remote_work = models.BooleanField(default=False)
    category = models.ForeignKey(Category, null=True, blank=True,
                                 on_delete=models.PROTECT)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('api:vacancies:vacancy-detail', kwargs={'pk': self.pk})

    @property
    def location(self):
        return {'city': self.location_city, 'country': self.location_country}

    @location.setter
    def location(self, value):
        if type(value) is dict:
            try:
                self.location_city = value['city']
                self.location_country = value['country']
            except KeyError:
                pass
