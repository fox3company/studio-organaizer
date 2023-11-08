from django.db import models

class VisitManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset().filter(type_of_tr=TypeOfTr.VISIT)
        return qs

class PaymentManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset().filter(type_of_tr=TypeOfTr.PAYMENT)
        return qs


