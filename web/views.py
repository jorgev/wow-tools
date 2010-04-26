# Create your views here.
from django.shortcuts import render_to_response
from web.models import Event, UploadForm
from django.http import HttpResponse, HttpResponseRedirect

def index(request):
    return render_to_response('wowparse/index.html', {})

def raids(request):
    return render_to_response('wowparse/raids.html', {})

def upload(request):
	if request.method == 'POST':
		form = UploadForm(request.POST, request.FILES)
		if form.is_valid():
			return HttpResponseRedirect('./raids')
		else:
			return HttpResponse('Form submission failed')
	else:
		return render_to_response('wowparse/upload.html', {})

