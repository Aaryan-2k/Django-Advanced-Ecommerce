from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager


class MyAccountManager(BaseUserManager):
    def create_user(self,first_name,last_name,username,email,password=None):
        if not email:
            raise ValueError("user must have an email address")

        if not username:
            raise ValueError("username is also required")
        user=self.model(
            email=self.normalize_email(email),  #make all char small
            username=username,
            first_name=first_name,
            last_name=last_name,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self,first_name,last_name,username,email,password):
        user=self.create_user(first_name,last_name,username,email,password)
        user.is_admin=True
        user.is_active=True
        user.is_staff=True
        user.is_superadmin=True
        user.save(using=self._db)
    
class Account(AbstractBaseUser):
    first_name=models.CharField(max_length=100)
    last_name=models.CharField(max_length=100)
    username=models.CharField(max_length=100,unique=True)
    email=models.EmailField(max_length=100,unique=True)
    phone_number=models.CharField(max_length=100, blank=True)

    # we need to mention some required fields
    date_joined=models.DateTimeField(auto_now_add=True)
    last_login=models.DateTimeField(auto_now_add=True)
    is_admin=models.BooleanField(default=False)
    is_staff=models.BooleanField(default=False)
    is_active=models.BooleanField(default=False)
    is_superadmin=models.BooleanField(default=False)
    # These above 6 fields are mandatory when we are creating custom user model

    #Now we have to set a user login field currently usename is used for login purpose we want to use email instead so
    USERNAME_FIELD='email'
    REQUIRED_FIELDS=['username','first_name','last_name']

    objects=MyAccountManager()

    def __str__(self):
        return self.email

    #Following are some mandatory methods that are to be created
    def has_perm(self,perm,obj=None):
        return self.is_admin
    
    def has_module_perms(self,add_label):
        return True
    
class UserProfile(models.Model):
    user=models.OneToOneField(Account, on_delete=models.CASCADE)
    address_line_1=models.CharField(max_length=100, blank=True)
    address_line_2=models.CharField(max_length=100, blank=True)
    profile_picture=models.ImageField(blank=True, upload_to='userprofile')
    city=models.CharField(max_length=100, blank=True)
    state=models.CharField(max_length=100, blank=True)
    country=models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.user.first_name
