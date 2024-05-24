from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    def create_user(self, matricula, password=None, **extra_fields):
        if not matricula:
            raise ValueError(_('The Matricula field must be set'))
        user = self.model(matricula=matricula, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, matricula, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(matricula, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    matricula = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    objects = CustomUserManager()

    USERNAME_FIELD = 'matricula'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.matricula