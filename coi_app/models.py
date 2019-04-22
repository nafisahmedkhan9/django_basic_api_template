from django.db import models

from django.contrib.auth.models import (
	AbstractBaseUser, BaseUserManager, PermissionsMixin
)
from django.conf import settings
from datetime import datetime, timezone, timedelta
import jwt

# Create your models here.

# Create your models here.
class UserManager(BaseUserManager):
	def create_user(self, email, password):
		#create and return user with email, username and password
		if email is None:
			raise TypeError('User must have an email')
		if password is None:
			raise TypeError('User must have a password')

		user = self.model(email=email)
		user.set_password(password)
		user.save()
		return user

	def create_superuser(self, email, password):
		#create and return user with superuser (admin) permission 
		if password is None:
			raise TypeError('Superuser must have a password')
		user = self.create_user(email, password)
		user.is_superuser = True
		user.is_staff = True
		if password is not None:
			user.set_password(password)
		user.save()

		return user

USER_GENDER = (
	("MALE" , "MALE"),
	("FEMALE", "FEMALE"),
	("OTHER", "OTHER")
)

class User(AbstractBaseUser, PermissionsMixin):
	is_staff = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	name = models.CharField(max_length=100, null=True, blank=True)
	dob = models.DateField(null=True, blank=True)
	gender = models.CharField(max_length=10,choices=USER_GENDER, null=True, blank=True)
	email = models.EmailField(db_index=True, unique=True, max_length=100)
	mobile = models.CharField(max_length=10, null=True, blank=True)
	picture = models.ImageField(upload_to = 'image/', default = 'image/default_image.png')
	otp = models.CharField(max_length=15, null=True, blank=True)
	is_otp_verified = models.BooleanField(default=False)
	facebook_id = models.CharField(max_length=50, null=True, blank=True)
	google_id = models.CharField(max_length=50, null=True, blank=True)
	USERNAME_FIELD = 'email'
	objects = UserManager()
    
	def __str__(self):
		return self.email
        
	@property
	def token(self):
		return self._generate_jwt_token()
	
	def _generate_jwt_token(self):
		dt = datetime.now() + timedelta(days=60)
		token = jwt.encode({	
			'id': self.pk,
			'exp': dt.timestamp()
		}, settings.SECRET_KEY, algorithm='HS256')
		return token.decode('utf-8')
	
	def to_dict(self):
		return {
			"id" : self.id,
			"name": self.name,
			"email" : self.email,
		}