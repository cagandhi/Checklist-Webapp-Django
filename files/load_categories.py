from checklist.models import Category

with open('categories.txt', 'r') as fp:
	for line in fp.readlines():
		obj=Category(name=line.strip())
		obj.save()

# Run this python file in django shell to load categories into "Category" model
# ./manage.py shell < load_categories.py