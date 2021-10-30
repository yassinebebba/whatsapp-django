from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.contrib.auth.models import _user_has_perm
from django.contrib.auth.models import _user_has_module_perms
# typing
from typing import Union


class CustomUserManager(BaseUserManager):
    def create_user(self, username, phone_number):
        if not username:
            return ValueError('User must have a username.')
        if not phone_number:
            return ValueError('User must have a phone number.')

        user = self.model(
            username=username,
            phone_number=phone_number
        )
        user.save(using=self._db)

        return user

    def create_superuser(self, username, phone_number):
        user = self.create_user(username, phone_number)

        user.is_staff = True
        user.is_admin = True

        user.save(using=self._db)

        return user


class CustomUser(AbstractBaseUser):
    class Meta:
        db_table = 'custom_user'

    username = models.CharField(max_length=30, null=False)
    phone_number = models.CharField(max_length=15, unique=True, null=False)
    password = None
    last_login = None
    creation_date = models.DateTimeField(default=timezone.now, null=False)
    is_active = models.BooleanField(default=False, null=False)
    is_staff = models.BooleanField(default=False, null=False)
    is_admin = models.BooleanField(default=False, null=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['username']

    @staticmethod
    def exists(phone_number: str) -> Union[tuple['CustomUser', bool], tuple[None, bool]]:
        try:
            return (CustomUser.objects.get(phone_number=phone_number), True)
        except ObjectDoesNotExist:
            return (None, False)

    def activate(self) -> None:
        self.is_active = True
        self.save()
        return None

    def has_perm(self, perm: str, obj=None) -> bool:
        if self.is_active and self.is_admin:
            return True
        return _user_has_perm(self, perm, obj)

    def has_perms(self, perms: list[str], obj=None) -> bool:
        if self.is_active and self.is_admin:
            return True
        return all(self.has_perm(perm, obj) for perm in perms)

    def has_module_perms(self, app_label: str) -> bool:
        if self.is_active and self.is_admin:
            return True
        return _user_has_module_perms(self, app_label)

    def __repr__(self):
        return f'CustomUser(username=\'{self.username}\', phone_number=\'{self.phone_number}\')'

    def __str__(self):
        return f'{self.username} - {self.phone_number}'