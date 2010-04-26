# Create your views here.
from django.shortcuts import render_to_response
from web.models import Event, UploadForm, LoginForm, RegisterForm
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User

def index(request):
    return render_to_response('index.html', {})

def register(request):
	if request.method == 'POST':
		form = RegisterForm(request.POST)
		if form.is_valid():
			return HttpResponseRedirect('./')
		else:
			return HttpResponse('Form submission failed')
	else:
		return render_to_response('register.html', {})

def raids(request):
    return render_to_response('raids.html', {})

def raid_detail(request):
	return render_to_response('raid_detail.html', {})

def upload(request):
	if request.method == 'POST':
		form = UploadForm(request.POST, request.FILES)
		if form.is_valid():
			return HttpResponseRedirect('./raids')
		else:
			return HttpResponse('Form submission failed')
	else:
		return render_to_response('upload.html', {})

def login(request):
	if request.method == 'POST':
		form = LoginForm(request.POST)
		if form.is_valid():
			return HttpResponseRedirect('./')
		else:
			return HttpResponse('Form submission failed')
	else:
		return render_to_response('login.html', {})


