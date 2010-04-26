# Create your views here.
from django.shortcuts import render_to_response
from web.models import Event, UploadForm, LoginForm, RegisterForm
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

def index(request):
	username = None
	if request.user.is_authenticated():
		username = request.user.username
	return render_to_response('index.html', { 'user': username })

def register(request):
	if request.method == 'POST':
		form = RegisterForm(request.POST)
		if form.is_valid():
			user = User.objects.create_user(request.POST['username'], request.POST['email'], request.POST['password'])
			return HttpResponseRedirect('./')
		else:
			return render_to_response('register.html', { 'message': 'There was an error processing the form, please try again' })
	else:
		return render_to_response('register.html', {})

def raids(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/login?next=%s' % request.path)
	return render_to_response('raids.html', {})

def raid_detail(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/login?next=%s' % request.path)
	return render_to_response('raid_detail.html', {})

def upload(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/login?next=%s' % request.path)
	if request.method == 'POST':
		form = UploadForm(request.POST, request.FILES)
		if form.is_valid():
			request.FILES['file']
			return HttpResponseRedirect('./raids')
		else:
			return render_to_response('upload.html', { 'message': 'There was an error processing the form, please try again' })
	else:
		return render_to_response('upload.html', {})

def login(request):
	if request.method == 'POST':
		form = LoginForm(request.POST)
		if form.is_valid():
			username = request.POST['username']
			password = request.POST['password']
			next = request.POST['next']
			user = auth.authenticate(username=username, password=password)
			if user is not None:
				if user.is_active:
					auth.login(request, user)
					if next:
						return HttpResponseRedirect(next)
					else:
						return HttpResponseRedirect('./')
				else:
					return render_to_response('login.html', { 'message': 'Account has been disabled, please contact the site administrator' })
			else:
				return render_to_response('login.html', { 'message': 'Incorrect username or password, please try again' })
		else:
			return render_to_response('login.html', { 'message': 'There was an error processing the form, please try again' })
	else:
		next = request.GET['next']
		return render_to_response('login.html', { 'next': next })

def logout(request):
	auth.logout(request)
	return HttpResponseRedirect('./')

