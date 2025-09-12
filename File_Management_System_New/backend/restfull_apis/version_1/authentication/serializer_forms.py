from django.utils.translation import gettext as _
from django.contrib.auth.forms import PasswordResetForm
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from django.conf import settings


class CustomPasswordResetForm(PasswordResetForm):

    def send_mail(self, subject_template_name, email_template_name, context, from_email, to_email, html_email_template_name=None):

        """
        Send a django.core.mail.EmailMultiAlternatives to `to_email`.
        """

        subject = _('Reset Your Password: Society First')
        context.update({'CLIENT_PWA_URL': "https://front-societyfirst.progfeel.co.in/session/confirm-password"})
       
        body = loader.render_to_string('registration/password_reset_email.html', context)


        email_message = EmailMultiAlternatives(subject, body, _('ProtoType'), [to_email])

        html_email_template_name = 'registration/password_reset_email.html'

        if html_email_template_name is not None:
            html_email = loader.render_to_string(html_email_template_name, context)
            email_message.attach_alternative(html_email, 'text/html')

        email_message.send()

'''
# context.update({'CLIENT_PWA_URL': "http://localhost:3000/session/confirm-password"})
# body = loader.render_to_string(email_template_name, context)
'''