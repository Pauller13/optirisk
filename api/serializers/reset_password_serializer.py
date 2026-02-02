from datetime import timedelta, datetime, timezone
from rest_framework import serializers
from user.models.custom_user_model import CustomUserModel
from user.models.opt_model import OTPModel


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.IntegerField()
    password = serializers.CharField(min_length=8)  # Ajout de validation sur la longueur du mot de passe

    def validate(self, attrs):
        email = attrs.get('email')
        code = attrs.get('code')

        # Vérifier si l'utilisateur existe
        try:
            user = CustomUserModel.objects.get(email=email)
        except CustomUserModel.DoesNotExist:
            raise serializers.ValidationError("Aucun utilisateur trouvé avec cet email.")

        # Récupérer l'OTP associé à l'utilisateur
        user_opt = OTPModel.objects.filter(user=user).first()
        if not user_opt:
            raise serializers.ValidationError("Code OTP invalide ou expiré.")


        # Vérifier si le code OTP est valide et n'a pas expiré
        if user_opt.code != str(code):
            raise serializers.ValidationError("Le code OTP est incorrect.")

        if user_opt.created_at + timedelta(minutes=5) < datetime.now(timezone.utc):
            raise serializers.ValidationError("Le code OTP a expiré.")

        # Si tout est validé, on retourne les données pour mettre à jour le mot de passe
        return attrs
