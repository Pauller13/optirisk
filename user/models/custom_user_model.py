import secrets
import string
import uuid
import os

import pyotp
from django.contrib.auth.models import AbstractUser
from django.db import models
from base.services import MailService
from user.models.token_user_model import TokenUserModel
from dotenv import load_dotenv
from cloudinary_storage import storage

load_dotenv()
service = MailService()

class CustomUserModel(AbstractUser):
    email = models.CharField(max_length=150, unique=True)
    company_name = models.CharField(max_length=100)
    username = models.CharField(max_length=100)
    is_active = models.BooleanField(default=False)
    slug = models.SlugField(max_length=100, unique=True)
    otp_secret = models.CharField(max_length=32, blank=True, null=True)
    is_2fa_enabled = models.BooleanField(default=False)
    secret_key = models.CharField(max_length=32, blank=True, null=True)
    picture = models.ImageField(upload_to='user/', storage=storage.RawMediaCloudinaryStorage(), null=True, blank=True)
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [""]
    def save(self, *args, **kwargs):
        is_new = not self.pk
        token = self.generate_token()
        if is_new and not self.is_active:
            self.slug = f'user-{uuid.uuid4().hex}'
            
            self.set_password(self.password)
            service.send_email(
                subject="Activation de compte",
                template="mail_active_account.html",
                context={
                    'token': f'{os.getenv('FRONTLINK')}/activate-account?token={token}',
                    'app_name': os.getenv('APPNAME'),
                },
                recipient_mail=self.email,
            )
        super().save(*args, **kwargs)
        if is_new and not self.is_active:
            TokenUserModel.objects.create(user=self, token=token)

    def generate_otp_secret(self):
        self.otp_secret = pyotp.random_base32()
        self.save()

    def generate_secret_key(self):
        self.secret_key = pyotp.random_base32()
        self.save()
        
    def get_totp(self):
        return pyotp.TOTP(self.otp_secret)

    def generate_token(self):
        return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(64))

    def generate_opt(self):
        return ''.join(secrets.choice( string.digits) for _ in range(6))
