from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import default

# Create your models here.


class UserProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(blank=True, null=True, upload_to='userprofile',default='userprofile/default_image.png')
    phone_number = models.BigIntegerField(null=True)

    def __str__(self):
        return self.user.first_name