import factory

from ..models import User


class BaseUserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User

    name = factory.Sequence(lambda n: 'name%s' % (n+1))
    email = factory.LazyAttribute(lambda obj: '%s@example.com' % obj.name)
    password = factory.PostGenerationMethodCall('set_password', 'secret')


class ActiveUserFactory(BaseUserFactory):
    is_active = True


class AdminFactory(BaseUserFactory):
    is_superuser = True
    is_staff = True
    is_active = True
