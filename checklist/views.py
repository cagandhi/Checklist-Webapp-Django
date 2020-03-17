from django.shortcuts import render
from django.http import HttpResponse
from .models import Checklist
from django.views.generic import ListView, DetailView

# Create your views here.

# home page - this function will be called when I navigate to "localhost:8000/admin"
def home(request):
	# return HttpResponse('<h1>This is your home page! Welcome</h1>')

	context = {
		'checklists_var': Checklist.objects.all().order_by('-date_posted'), # order by to order posts in descending order of date posted
		'title': 'HOME'
	}
	return render(request, 'checklist/home.html', context) # because render looks in templates subdirectory, by default

class ChecklistListView(ListView):
	model = Checklist
	template_name = 'checklist/home.html' # <app_name>/<model>_<viewtype>.html
	context_object_name = 'checklists_var'
	ordering = ['-date_posted']

class ChecklistDetailView(DetailView):
	model = Checklist

def about(request):
	return render(request, 'checklist/about.html')

# my checklist page - shows checklists written by the logged in user only
def mychecklist(request):
	context = {
		'checklists_var': request.user.checklist_set.all(),
		'title': 'My Checklists'
	}

	return render(request, 'checklist/mychecklist.html', context) # because render looks in templates subdirectory, by default