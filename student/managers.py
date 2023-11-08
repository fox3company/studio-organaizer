from django.contrib.auth.base_user import BaseUserManager
from django.db import models





class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, password, **extra_fields):
        if not phone_number:
            raise ValueError('The phone number must be set')   
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, phone_number, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(phone_number, password, **extra_fields)

class CustomTeacherManager(CustomUserManager):
    def get_queryset(self):
        qs = super().get_queryset().filter(is_staff=True)
        return qs

class CustomStudentManager(CustomUserManager):
    def get_queryset(self):
        qs = super().get_queryset().filter(is_staff=False)
        return qs

class CustomClientManager(CustomUserManager):
    def get_queryset(self):
        qs = super().get_queryset().filter(is_staff=False).filter(is_client=True)
        return qs
    def tr_count(self,client_id):
        client = self.get_queryset().filter(id=client_id)[0]
        return client.transactions.all().count()


class TypeOfTr(models.TextChoices):
        PAYMENT     = "+", "Payment"
        VISIT       = "-", "Visit"


class TransactionsManager(models.Manager):
    def smth(self):
        self

class VisitManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset().filter(type_of_tr=TypeOfTr.VISIT)
        return qs

class PaymentManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset().filter(type_of_tr=TypeOfTr.PAYMENT)
        return qs







