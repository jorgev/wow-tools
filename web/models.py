from django.db import models
from django.contrib.auth.models import User
from django import forms

# Create your models here.
class Event(models.Model):
	user = models.ForeignKey(User)
	name = models.CharField(max_length=255)
	html = models.TextField()
	created = models.DateTimeField(auto_now_add=True)

	def __unicode__(self):
		return self.name

class UploadForm(forms.Form):
	name = forms.CharField(max_length=255)
	ignore_pets = forms.BooleanField()
	ignore_guardians = forms.BooleanField()
	file = forms.FileField()

class LoginForm(forms.Form):
	username = forms.CharField(max_length=255)
	password = forms.CharField(max_length=255)

class RegisterForm(forms.Form):
	username = forms.CharField(max_length=255)
	email = forms.CharField(max_length=255)
	password = forms.CharField(max_length=255)

class ContactForm(forms.Form):
	username = forms.CharField(max_length=255)
	email = forms.CharField(max_length=255)
	subject = forms.CharField(max_length=255)
	body = forms.TextField()

