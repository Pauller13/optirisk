import os
from datetime import timedelta, timezone, datetime
from api.serializers import CreateUserSerializer, UpdateUserSerializer, UserSerializer, PasswordSerializer
from api.serializers.reset_password_serializer import ResetPasswordSerializer
from base.services import MailService
from base.services.status_service import StatusService
from user.models.custom_user_model import CustomUserModel
from user.models.opt_model import OTPModel
from user.models.token_user_model import TokenUserModel
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.hashers import check_password


status_service = StatusService()
mail_service = MailService()

class CustomUserViewSet(ModelViewSet):
    serializer_class = CreateUserSerializer
    queryset = CustomUserModel.objects.all()
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateUserSerializer
        if self.action == 'update_my_profile':
            return UpdateUserSerializer
        if self.action == 'update_password':
            return PasswordSerializer
        if self.action == 'reset_password':
            return ResetPasswordSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action in ['create', 'activate_account','demand_opt_to_reset_password','reset_password']:
            return []
        return [IsAuthenticated()]


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return status_service.status400(data=serializer.errors, message="Invalid data")

        self.perform_create(serializer)
        return status_service.status201(
            data=serializer.data,
            message="Inscription réussi, Vous allez recevoir un mail pour activer votre compte"
        )

    def demand_opt_to_reset_password(self, request, *args, **kwargs):
        try:
            email = request.data.get('email')
            user = CustomUserModel.objects.filter(email=email).first()
            OTPModel.objects.filter(user=user, type='PASSWORD').delete()
            if not user:
                return status_service.status400(data={}, message="L'utilisateur n'existe pas")
            opt = user.generate_opt()
            OTPModel.objects.create(
                user=user,
                code=opt,
                type='PASSWORD'
            )
            mail_service.send_email(
                subject="Réinitilisation de mot de passe",
                template="mail_opt_reinitialize_password.html",
                context={
                    'code': opt,
                    'app_name': os.getenv('APPNAME'),
                },
                recipient_mail=user.email,
            )
            return status_service.status201(
                data={},
                message="Demande de réinitialisation",
            )
        except Exception as e:
            return status_service.status500(data=str(e))

    def reset_password(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                return status_service.status400(data=serializer.errors, message="Invalid data")
            customer = CustomUserModel.objects.filter(email=serializer.validated_data.get('email')).first()
            customer.set_password(serializer.validated_data.get('password'))
            customer.save()
            OTPModel.objects.filter(user=customer).delete()
            return status_service.status200(data={})
        except Exception as e:
            return status_service.status500(data=str(e))

    def update_my_profile(self, request, *args, **kwargs):
        try:
            instance = CustomUserModel.objects.filter(id=request.user.id).first()
            serializer = self.get_serializer(instance, data=request.data)
            if not serializer.is_valid():
                return status_service.status400(data=serializer.errors, message="Invalid data")

            self.perform_update(instance)
            return status_service.status200(
                data=serializer.data,
                message="Inscription réussi, Vous allez recevoir un mail pour activer votre compte"
            )
        except Exception as e:
            return status_service.status500(data=str(e))

    def update_password(self, request, *args, **kwargs):
        try:
            instance = CustomUserModel.objects.filter(id=request.user.id).first()
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                return status_service.status400(data=serializer.errors)
            password = serializer.validated_data.get('password')
            is_correct_password = check_password(password, instance.password)
            print(is_correct_password)
            if not is_correct_password:
                return status_service.status400(data={},message="Mot de passe incorrect")
            new_password = serializer.validated_data.get('new_password')
            instance.set_password(new_password)
            instance.save()
            return status_service.status200(data={}, message="Mot de passe modifié ")
        except Exception as e:
            return status_service.status500(data=str(e))


    def profil(self,request,*args,**kwargs):
        try:
            instance = CustomUserModel.objects.filter(id=request.user.id).first()
            serializer = self.get_serializer(instance)
            return status_service.status200(
                data=serializer.data,
                message="Success"
            )
        except Exception as e:
            return status_service.status500(data=str(e))

    def delete_account(self,request,*args,**kwargs):
        try:
            instance = CustomUserModel.objects.filter(id=request.user.id).first()
            instance.is_active = False
            return status_service.status204(data={})
        except Exception as e:
            return status_service.status500(data=str(e))

    def activate_account(self, request, *args, **kwargs):
        token = request.data.get('token')
        if not token:
            return status_service.status400(
                data={'token': ''},
                message="Pas de token"
            )
        try:
            t = TokenUserModel.objects.filter(token=token).first()
            if token == t.token and t.created_at + timedelta(days=1) > datetime.now(timezone.utc):
                t.user.is_active = True
                t.user.save()
                t.delete()
                return status_service.status200(
                    data={},
                    message="Activation du compte"
                )
            t.delete()
            t.user.delete()
            return status_service.status400(
                data={'token': token},
                message="Expiration du délai veuillez recréer votre compte"
            )
        except Exception as e:
            return status_service.status500(data=str(e))


