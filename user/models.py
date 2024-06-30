from django.db import models
from django.contrib.auth.models import  AbstractUser


class Profile(AbstractUser):
    address = models.TextField()
    email = models.EmailField(unique=True, null=True, blank=True)
    phone = models.CharField(unique=True, max_length=13, null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

