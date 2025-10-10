from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class MyAccountManager(BaseUserManager):
    def create_user(self, first_name, last_name, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Adicione um Email valido')
        if not username:
            raise ValueError('Adicione um nome valido')

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )
        user.set_password(password)
        # garante que o usuário seja ativo por padrão
        user.is_active = False
        user.save(using=self._db)
        return user

    def create_superuser(self, first_name, last_name, email, username, password, **extra_fields):
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superadmin', True)
        extra_fields.setdefault('is_active', True)

        user = self.create_user(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=self.normalize_email(email),
            password=password,
            **extra_fields
        )

        # atributos extras (apenas por segurança; já setados acima)
        user.is_admin = True
        user.is_staff = True
        user.is_active = True
        user.is_superadmin = True
        user.save(using=self._db)
        return user

class Account(AbstractBaseUser):
    first_name    = models.CharField(max_length=50)
    last_name     = models.CharField(max_length=50)
    username      = models.CharField(max_length=50, unique=True)
    email         = models.EmailField(max_length=100, unique=True)

    # Obrigatorios
    data_joined   = models.DateTimeField(auto_now_add=True)
    last_login    = models.DateTimeField(auto_now=True)
    is_admin      = models.BooleanField(default=False)
    is_staff      = models.BooleanField(default=False)
    is_active     = models.BooleanField(default=False)  
    is_superadmin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    objects = MyAccountManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True
