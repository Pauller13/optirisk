from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives, send_mail
from django.utils.html import strip_tags
from django.conf import settings
from typing import Any, Dict, List


class MailService:
    def __init__(self, default_from_email: str = settings.DEFAULT_FROM_EMAIL):
        self.default_from_email = default_from_email

    def send_simple_email(self, recipient_mail: str, subject: str, message: str) -> None:
        """Envoie un e-mail simple.

        Args :
            recipient_mail : L'adresse e-mail du destinataire,
            subject : Le sujet de l'e-mail,
            message : Le contenu de l'e-mail.
        """
        send_mail(subject, message, self.default_from_email, [recipient_mail], fail_silently=False)

    def send_email(self, context: Dict[str, Any], template: str, recipient_mail: str,
                   subject: str) -> None:
        """Envoie un e-mail avec un contenu HTML personnalisé.

        Args :
            context : Le contexte pour le rendu du template,
            template : Le nom du template à utiliser,
            recipient_mail : L'adresse e-mail du destinataire,
            subject : Le sujet de l'e-mail.
        """
        html_content = render_to_string(template, context)
        text_content = strip_tags(html_content)

        # Créer l'email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=self.default_from_email,
            to=[recipient_mail],
        )

        # Ajouter le contenu HTML
        email.attach_alternative(html_content, 'text/html')

        # Envoyer l'email
        try:
            email.send(fail_silently=False)
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'e-mail: {e}")

    def send_bulk_mail(self, context: Dict[str, Any], template: str, recipient_mails: List[str],
                       subject: str) -> None:
        # Méthode permettant d'envoyer un mail à plusieurs personnes
        for recipient in recipient_mails:
            self.send_mail(context, template, recipient, subject)

    def send_mail_with_attachment(self, context: Dict[str, Any], template: str, recipient_mail: str,
                                  attachments: List[str],
                                  subject: str) -> None:
        # Méthode permettant d'envoyer un mail avec des pièces jointe
        pass

