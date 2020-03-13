from django.shortcuts import render
from django.http import HttpResponse
from .models import Checklist

# Create your views here.

# create dummy data - no need after we fetch the checklists from the database
# checklists = [
# 	{
# 		'title': 'checklist 1',
# 		'author': 'Chintan Gandhi',
# 		'content': 'This is checklist 1',
# 		'date_posted': 'Today'
# 	},
# 	{
# 		'title': 'checklist 2',
# 		'author': 'Romil Gandhi',
# 		'content': 'This is checklist 2',
# 		'date_posted': 'Yesterday'
# 	},
# ]

# home page - this function will be called when I navigate to "localhost:8000/admin"
def home(request):
	# return HttpResponse('<h1>This is your home page! Welcome</h1>')

	context = {
		'checklists_var': Checklist.objects.all(),
		'title': 'HOME'
	}
	return render(request, 'checklist/home.html', context) # because render looks in templates subdirectory, by default

def about(request):
	return render(request, 'checklist/about.html')