from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save



class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)  # Usually good to enforce unique email
    name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    profile_pic = models.ImageField(upload_to='profile_pic', default='profile_pic/default.png')
    deletion_reason = models.TextField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Mark staff True for superusers or optionally for approved renter/seller if you want
        if self.is_superuser:
            self.is_staff = True
        else:
            # If you want renter/seller admins to access admin panel, uncomment below:
            # self.is_staff = self.is_approved and self.category in ['seller', 'renter']
            self.is_staff = False
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username
    
    def get_full_name(self):
        # Return the name field if set, else fallback to username
        return self.name or self.username






    








