import factory

from ..models import Tag, Category, Vacancy


class TagFactory(factory.DjangoModelFactory):
    class Meta:
        model = Tag

    title = factory.Sequence(lambda n: 'tag%s' % (n + 1))


class CategoryFactory(factory.DjangoModelFactory):
    class Meta:
        model = Category

    title = factory.Sequence(lambda n: 'category%s' % (n + 1))


class VacancyFactory(factory.DjangoModelFactory):
    class Meta:
        model = Vacancy

    title = factory.Sequence(lambda n: 'title%s' % (n + 1))
    description = factory.Sequence(lambda n: 'description%s' % (n + 1))
