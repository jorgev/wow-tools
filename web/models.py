from django.db import models
from django import forms

# Create your models here.
class Event(models.Model):
	name = models.CharField(max_length=255)
	html = models.TextField()
	created = models.DateTimeField(auto_now_add=True)

	def __unicode__(self):
		return self.name

class UploadForm(forms.Form):
	name = forms.CharField(max_length=255)
	file = forms.FileField()

