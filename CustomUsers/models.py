from django.db import models  
from django.utils.timezone import now


class User(models.Model):
    id= models.AutoField(primary_key=True, unique=True)
    username = models.CharField(max_length=100, unique=True)
    name= models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=100, unique=True)
    profile_image = models.ImageField(upload_to='static/profile_image/', null=True, blank=True)
    last_login = models.DateTimeField(default=now)


    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.username + ',' + self.email
    
#override the default authentication
    @property
    def is_authenticated(self):
        return True