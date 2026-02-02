from django.contrib.auth import get_user_model
from django.db.models.signals import post_migrate
from django.dispatch import receiver

UserModel = get_user_model()

@receiver(post_migrate)
def create_default_user(sender, **kwargs):
    username = 'admin'
    password = 'admin123'
    email = 'admin@example.com'

    if UserModel.objects.filter(username=username).exists():
        print('✅ Default user already exists')
        return

    try:
        user = UserModel.objects.create_user(
            username=username,
            password=password,
            email=email,
        )
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        if hasattr(user, 'role'):  
            user.role = 'admin'

        user.save()
        print('✅ Default user created')
    except Exception as e:
        print(f"❌ Default user creation failed: {e}")
