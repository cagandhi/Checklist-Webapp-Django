# https://stackoverflow.com/a/34903331/6543250 - to pass data to "base.html"

from checklist.models import Category

def add_variable_to_context(request):
	return {
		'category_list': Category.objects.all()
	}