from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):

    CUSTOMER = "CU"
    TRAINER = "TR"
    ADMIN = "AD"

    ROLES_CHOICES = [
        (CUSTOMER, "Customer"),
        (TRAINER, "Trainer"),
        (ADMIN, "Admin"),
    ]


    phone = models.CharField(max_length=15)
    age = models.CharField(max_length=3,null=True)
    height = models.CharField(max_length=5,null=True)
    weight = models.CharField(max_length=5,null=True)
    
    profile_image = models.ImageField(upload_to='profile_image',default='profile_image/default-avatar.jpg',null=True)
    role = models.CharField(
        max_length=2, choices=ROLES_CHOICES, null=False)
    gender = models.CharField(max_length=10)
    own_plan = models.BooleanField(null=True, blank=True, default=False)
    assigned_trainer = models.BooleanField(null=True, blank=True, default=False)
    assigned_user = models.BooleanField(null=True, blank=True, default=False)
    trainer= models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True)
    plan= models.ForeignKey(
        "api.Plan", on_delete=models.CASCADE, null=True)


class Plan(models.Model):
    type = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

class Feature(models.Model):
    entry = models.ForeignKey(Plan, related_name='features', on_delete=models.CASCADE)
    feature_text = models.CharField(max_length=200)

# class Notification(models.Model):

class Category(models.Model):
    category_name=models.CharField(max_length=30)

class video(models.Model):
    title=models.CharField(max_length=15)
    url=models.URLField()
    category=models.ForeignKey(Category,on_delete=models.CASCADE,null=True)