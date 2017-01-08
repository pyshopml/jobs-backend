from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password
        """
        if not email:
            raise ValueError('Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        user.email_user(
            subject='PyJobs registration confirm',
            message='Go to http://jobs.pyshop.ru/activation/?token=',
            from_email='jobs_backend <noreply@jobs.pyshop.ru>'
        )
        return user

    def create_user(self, email, password=None, **extra_fields):
        """
        Creates regular User
        """
        extra_fields.setdefault('is_superuser', False)
        # todo: Can login right after registration?
        extra_fields.setdefault('is_active', True)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """
        Creates superuser with abilities to login at admin panel
        (django.contrib.admin)
        """
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField('email', unique=True)
    name = models.CharField('name', max_length=50, blank=True)
    is_active = models.BooleanField('active', default=False)
    is_staff = models.BooleanField('staff', default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def get_full_name(self):
        """
        Returns the full name of a User
        """
        return self.email

    def get_short_name(self):
        """
        Returns the short name of a User
        """
        return self.get_full_name()

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Sends an email to User
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)
