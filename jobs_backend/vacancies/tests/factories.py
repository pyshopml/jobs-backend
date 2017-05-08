from datetime import datetime, timedelta

import factory
from factory import fuzzy

from ..models import Vacancy


class VacancyFactory(factory.DjangoModelFactory):
    class Meta:
        model = Vacancy

    title = factory.Sequence(lambda n: 'title%s' % (n + 1))
    description = factory.Sequence(lambda n: 'description%s' % (n + 1))


class VacancyRandomDateFactory(factory.DjangoModelFactory):
    class Meta:
        model = Vacancy

    title = factory.Sequence(lambda n: 'title%s' % (n + 1))
    description = factory.Sequence(lambda n: 'description%s' % (n + 1))
    created_on = fuzzy.FuzzyNaiveDateTime(datetime.now() - timedelta(2))
    modified_on = fuzzy.FuzzyNaiveDateTime(datetime.now(), datetime.now() + timedelta(2))
