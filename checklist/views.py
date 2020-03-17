from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (ListView, 
	DetailView, 
	CreateView,
	UpdateView,
	DeleteView
)
from django.contrib.auth.models import User

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
	paginate_by = 5


class UserChecklistListView(ListView):
	model = Checklist
	template_name = 'checklist/user_checklists.html' # <app_name>/<model>_<viewtype>.html
	context_object_name = 'checklists_var'
	paginate_by = 5

	def get_queryset(self):
		user = get_object_or_404(User, username=self.kwargs.get('username'))
		return Checklist.objects.filter(author=user).order_by('-date_posted')


class ChecklistDetailView(DetailView):
	model = Checklist


class ChecklistCreateView(LoginRequiredMixin, CreateView):
	model = Checklist
	fields = ['title', 'content']

	# to link logged in user as author to the checklist being created
	def form_valid(self, form):
		form.instance.author = self.request.user
		return super().form_valid(form)

# mixins for checking if user is logged in and the checklist author is the same as logged in user
class ChecklistUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
	model = Checklist
	fields = ['title', 'content']

	# to link logged in user as author to the checklist being updated
	def form_valid(self, form):
		form.instance.author = self.request.user
		return super().form_valid(form)

	# checks if currently logged in user is the checklist author
	def test_func(self):
		checklist = self.get_object()
		return (self.request.user == checklist.author)


class ChecklistDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
	model = Checklist
	success_url = '/'

	# checks if currently logged in user is the checklist author
	def test_func(self):
		checklist = self.get_object()
		return (self.request.user == checklist.author)


def about(request):
	return render(request, 'checklist/about.html')

# my checklist page - shows checklists written by the logged in user only
def mychecklist(request):
	context = {
		'checklists_var': request.user.checklist_set.all().order_by('-date_posted'),
		'title': 'My Checklists'
	}

	return render(request, 'checklist/mychecklist.html', context) # because render looks in templates subdirectory, by default