import factory

from jobs_backend.vacancies.models import Vacancy


class VacancyFactory(factory.DjangoModelFactory):
    class Meta:
        model = Vacancy

    title = factory.Sequence(lambda n: 'title%s' % (n+1))
    description = factory.Sequence(lambda n: 'description%s' % (n+1))
