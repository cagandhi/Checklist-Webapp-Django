from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

# create dummy data
posts = [
	{
		'title': 'checklist 1',
		'author': 'Chintan Gandhi',
		'content': 'This is checklist 1',
		'date': 'Today'
	},
	{
		'title': 'checklist 2',
		'author': 'Romil Gandhi',
		'content': 'This is checklist 2',
		'date': 'Yesterday'
	},
]

# home page - this function will be called when I navigate to "localhost:8000/admin"
def home(request):
	# return HttpResponse('<h1>This is your home page! Welcome</h1>')

	context = {
		'posts_var': posts,
		'title': 'HOME'
	}
	return render(request, 'checklist/home.html', context) # because render looks in templates subdirectory, by default

def about(request):
	return render(request, 'checklist/about.html')