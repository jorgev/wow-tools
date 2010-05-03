# Create your views here.
from django.shortcuts import render_to_response
from web.models import Event, UploadForm, LoginForm, RegisterForm, ContactForm
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
import parser

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

def contact(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/login?next=%s' % request.path)
	user = request.user
	if request.method == 'POST':
		form = ContactForm(request.POST)
		if form.is_valid():
			send_mail(request.POST['subject'], request.POST['body'], user.email, ['jorge@localhost'])
			return HttpResponseRedirect('./')
		else:
			return render_to_response('contact.html', { 'message': 'There was an error processing the form, please try again' })
	else:
		return render_to_response('contact.html', { 'user': user.username })

def raids(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/login?next=%s' % request.path)
	user = request.user
	raids = Event.objects.filter(user=user).order_by('-created')
	return render_to_response('raids.html', { 'user': user.username, 'raids': raids })

def raid_detail(request, raid_id):
	if request.method == 'GET':
		user = request.user
		try:
			raid = Event.objects.get(pk=raid_id) #, user=user)
		except:
			raid = None
		return render_to_response('raid_detail.html', { 'user': user.username, 'raid': raid })
	elif request.method == 'DELETE':
		# must be authenticated to do a delete
		if not request.user.is_authenticated():
			return HttpResponse(status=401)
		user = request.user
		try:
			raid = Event.objects.get(pk=raid_id, user=user)
			raid.delete()
		except Event.DoesNotExist:
			return HttpResponse(status=404)
		except:
			return HttpResponse(status=401)
		return HttpResponse()

def public_raid_detail(request, public_hash):
	try:
		raid = Event.objects.get(public_hash=public_hash)
	except Event.DoesNotExist:
		return HttpResponse(status=404)
	return render_to_response('raid_detail.html', { 'user': request.user.username, 'raid': raid, 'public': True })

def upload(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/login?next=%s' % request.path)
	if request.method == 'POST':
		form = UploadForm(request.POST, request.FILES)
		if form.is_valid():
			raid_id = parser.parse_data(request.user, request.POST['name'], request.POST['ignore_pets'], request.POST['ignore_guardians'], request.FILES['file'])
			return HttpResponseRedirect('./raids/%d' % raid_id)
		else:
			return render_to_response('upload.html', { 'message': 'There was an error processing the form, please try again' })
	else:
		username = request.user.username
		return render_to_response('upload.html', { 'user': username })

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
		if request.GET.has_key('next'):
			return render_to_response('login.html', { 'next': request.GET['next'] })
		else:
			return render_to_response('login.html', {})

def logout(request):
	auth.logout(request)
	return HttpResponseRedirect('./')

