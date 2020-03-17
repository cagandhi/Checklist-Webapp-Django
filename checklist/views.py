from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (ListView, 
	DetailView, 
	CreateView,
	UpdateView
)

from .models import Checklist
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


class ChecklistCreateView(LoginRequiredMixin, CreateView):
	model = Checklist
	fields = ['title', 'content']

	# to add link logged in user as author to the checklist
	def form_valid(self, form):
		form.instance.author = self.request.user
		return super().form_valid(form)


class ChecklistUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
	model = Checklist
	fields = ['title', 'content']

	# to add link logged in user as author to the checklist
	def form_valid(self, form):
		form.instance.author = self.request.user
		return super().form_valid(form)

	def test_func(self):
		checklist = self.get_object()
		return (self.request.user == checklist.author)


def about(request):
	return render(request, 'checklist/about.html')

# my checklist page - shows checklists written by the logged in user only
def mychecklist(request):
	context = {
		'checklists_var': request.user.checklist_set.all(),
		'title': 'My Checklists'
	}

	return render(request, 'checklist/mychecklist.html', context) # because render looks in templates subdirectory, by default