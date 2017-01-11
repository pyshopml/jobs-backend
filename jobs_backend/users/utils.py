from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text


def encode_uid(pk):
    return urlsafe_base64_encode(force_bytes(pk)).decode()


def decode_uid(pk):
    return force_text(urlsafe_base64_decode(pk))


class UserEmailBase(object):
    mail_subject = None
    html_body_template = None
    plaintext_body_template = None
    url = None

    def __init__(self, request, user, from_email=None):
        self.from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', from_email)
        self.user = user or request.user
        self.protocol = 'https' if request.is_secure() else 'http'
        self.site = get_current_site(request)

    def __iter__(self):
        context = self.get_context()
        html_message = render_to_string(self.html_body_template, context)
        message = render_to_string(self.plaintext_body_template, context)

        envelope = {
            'subject': self.mail_subject,
            'message': message,
            'html_message': html_message,
            'from_email': self.from_email,
        }
        for item in envelope.items():
            yield item

    def get_context(self):
        return {
            'user': self.user,
            'protocol': self.protocol,
            'domain': self.site.domain,
            'site': self.site,
            'uid': encode_uid(self.user.pk),
            'token': default_token_generator.make_token(self.user),
        }


class UserActivationEmail(UserEmailBase):
    mail_subject = 'Account activation'
    plaintext_body_template = 'email_activation_body.txt'
    html_body_template = 'email_activation_body.html'
    url = 'account/activate/?uid={uid}&token={token}'

    def get_context(self):
        context = super(UserActivationEmail, self).get_context()
        context['url'] = self.url.format(**context)
        return context


class UserPasswordResetEmail(UserEmailBase):
    mail_subject = 'Password reset'
    plaintext_body_template = 'email_pass_reset_body.txt'
    html_body_template = 'email_pass_reset_body.html'
    url = 'account/password/reset/confirm/?uid={uid}&token={token}'

    def get_context(self):
        context = super(UserPasswordResetEmail, self).get_context()
        context['url'] = self.url.format(**context)
        return context
