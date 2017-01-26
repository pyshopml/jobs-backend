from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.template.exceptions import TemplateDoesNotExist
from django.test import TestCase, RequestFactory

from . import factories
from .. import utils


class UIDTest(TestCase):

    def test_ok_encode_uid(self):
        self.assertEqual(utils.encode_uid(1), 'MQ')
        self.assertEqual(utils.encode_uid(999), 'OTk5')
        self.assertEqual(
            utils.encode_uid('user@example.com'), 'dXNlckBleGFtcGxlLmNvbQ'
        )

    def test_ok_decode_uid(self):
        self.assertEqual(utils.decode_uid('MQ'), '1')
        self.assertEqual(utils.decode_uid('OTk5'), '999')
        self.assertEqual(
            utils.decode_uid('dXNlckBleGFtcGxlLmNvbQ'), 'user@example.com'
        )


class UserEmailBaseTest(TestCase):

    def setUp(self):
        self.rf = RequestFactory()
        self.req = self.rf.get('/')
        self.user = factories.ActiveUserFactory.create()

    def test_ok_init(self):
        email = utils.UserEmailBase(self.req, self.user)

        self.assertEqual(email.from_email, settings.DEFAULT_FROM_EMAIL)
        self.assertEqual(email.user.email, self.user.email)
        self.assertEqual(email.protocol, self.req.scheme)
        self.assertEqual(str(email.site), 'testserver')

    def test_ok_init_from_email(self):
        from_ = 'noreply <noreply@example.com>'
        email = utils.UserEmailBase(self.req, self.user, from_email=from_)
        self.assertEqual(email.from_email, from_)

    def test_ok_get_context(self):
        email = utils.UserEmailBase(self.req, self.user)
        pregenerated_token = default_token_generator.make_token(email.user)

        self.assertDictEqual(
            email.get_context(),
            {
                'user': self.user,
                'protocol': self.req.scheme,
                'domain': 'testserver',
                'site': email.site,
                'uid': utils.encode_uid(self.user.pk),
                'token': pregenerated_token,
            }
        )

    def test_fail_iter_render_templates(self):
        email = utils.UserEmailBase(self.req, self.user)
        with self.assertRaises(TemplateDoesNotExist):
            dict(email)
