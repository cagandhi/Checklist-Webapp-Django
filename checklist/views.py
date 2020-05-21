from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
# mixins for checking if user is logged in and the checklist author is the same as logged in user
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (ListView, 
	DetailView, 
	CreateView,
	UpdateView,
	DeleteView
)
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.db.models import Q

from .models import Checklist, Upvote, Bookmark


# CHECKLIST HOME - display all checklists order by most recent - this class is used when user navigates to "localhost:8000/"
class ChecklistListView(ListView):
	model = Checklist
	template_name = 'checklist/home.html' # <app_name>/<model>_<viewtype>.html
	paginate_by = 5

	def get_context_data(self, **kwargs):
		context = super(ChecklistListView, self).get_context_data(**kwargs)

		upvotes_cnt_list = []
		checklists_var = Checklist.objects.all().order_by('-date_posted')
		
		for checklist in checklists_var:
			upvotes_cnt_list.append(Upvote.objects.filter(checklist=checklist).count())

		checklist_upvotes = zip(checklists_var, upvotes_cnt_list)

		paginator = Paginator(list(checklist_upvotes), self.paginate_by)
		page = self.request.GET.get('page')

		try:
			page_checklist_upvotes = paginator.page(page)
		except PageNotAnInteger:
			page_checklist_upvotes = paginator.page(1)
		except EmptyPage:
			page_checklist_upvotes = paginator.page(paginator.num_pages)

		context['checklist_upvotes'] = page_checklist_upvotes
		context['title'] = 'home'
		context['is_paginated'] = page_checklist_upvotes.has_other_pages

		return context


# DISPLAY CHECKLISTS BY LOGGED IN USER
class UserChecklistListView(ListView):
	model = Checklist
	template_name = 'checklist/user_checklists.html' # <app_name>/<model>_<viewtype>.html
	paginate_by = 5

	# https://stackoverflow.com/a/36950584/6543250 - when to use get_queryset() vs get_context_data()
	
	# how to paginate when get_context_data() implemented
	# 1. https://stackoverflow.com/a/33485595/6543250
	# 2. https://docs.djangoproject.com/en/1.8/topics/pagination/#using-paginator-in-a-view
	def get_context_data(self, **kwargs):
		context = super(UserChecklistListView, self).get_context_data(**kwargs)

		user = get_object_or_404(User, username=self.kwargs.get('username'))
		upvotes_cnt_list = []
		checklists_var = Checklist.objects.filter(author=user).order_by('-date_posted')
		
		for checklist in checklists_var:
			upvotes_cnt_list.append(Upvote.objects.filter(checklist=checklist).count())

		checklist_upvotes = zip(checklists_var, upvotes_cnt_list)

		paginator = Paginator(list(checklist_upvotes), self.paginate_by)
		page = self.request.GET.get('page')

		try:
			page_checklist_upvotes = paginator.page(page)
		except PageNotAnInteger:
			page_checklist_upvotes = paginator.page(1)
		except EmptyPage:
			page_checklist_upvotes = paginator.page(paginator.num_pages)

		context['checklist_upvotes'] = page_checklist_upvotes
		context['title'] = 'user'
		context['is_paginated'] = page_checklist_upvotes.has_other_pages

		return context
		

# DISPLAY A CHECKLIST IN FULL PAGE - WHEN USE CLICKS ON THE CHECKLIST
class ChecklistDetailView(DetailView):
	model = Checklist

	def get_context_data(self, **kwargs):
		context = super(ChecklistDetailView, self).get_context_data(**kwargs)
		# context['object'] = Checklist.objects.get(id=self.kwargs.get('pk'))

		uvote = Upvote.objects.filter(checklist_id=self.kwargs.get('pk')).count()
		context['uvote'] = uvote
		return context

# CREATE CHECKLIST
class ChecklistCreateView(LoginRequiredMixin, CreateView):
	model = Checklist
	fields = ['title', 'content']

	# to link logged in user as author to the checklist being created
	def form_valid(self, form):
		form.instance.author = self.request.user
		return super().form_valid(form)


# UPDATE CHECKLIST
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


# DELETE CHECKLIST 
class ChecklistDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
	model = Checklist
	success_url = '/'

	# checks if currently logged in user is the checklist author
	def test_func(self):
		checklist = self.get_object()
		return (self.request.user == checklist.author)


# VIEW BOOKMARKS PAGE
class BookmarkChecklistListView(ListView):
	model = Bookmark
	template_name = 'checklist/bookmark_checklists.html'
	# context_object_name = 'bookmarks_var'
	paginate_by = 5

	# def get_queryset(self):
	# 	return Bookmark.objects.filter(user=self.request.user)

	def get_context_data(self, **kwargs):
		context = super(BookmarkChecklistListView, self).get_context_data(**kwargs)

		upvotes_cnt_list = []
		bookmarks_var = Bookmark.objects.filter(user=self.request.user)

		for bookmark in bookmarks_var:
			upvotes_cnt_list.append(Upvote.objects.filter(checklist=bookmark.checklist).count())

		checklist_upvotes = zip(bookmarks_var, upvotes_cnt_list)

		paginator = Paginator(list(checklist_upvotes), self.paginate_by)
		page = self.request.GET.get('page')

		try:
			page_checklist_upvotes = paginator.page(page)
		except PageNotAnInteger:
			page_checklist_upvotes = paginator.page(1)
		except EmptyPage:
			page_checklist_upvotes = paginator.page(paginator.num_pages)

		context['checklist_upvotes'] = page_checklist_upvotes
		context['title'] = 'bookmarks'
		context['is_paginated'] = page_checklist_upvotes.has_other_pages

		return context


# VIEW UPVOTE PAGE
class UpvoteChecklistListView(ListView):
	model = Upvote
	template_name = 'checklist/upvote_checklists.html'
	paginate_by = 5

	def get_context_data(self, **kwargs):
		context = super(UpvoteChecklistListView, self).get_context_data(**kwargs)

		upvotes_cnt_list = []
		upvotes_var = Upvote.objects.filter(user=self.request.user)

		for upvote in upvotes_var:
			upvotes_cnt_list.append(Upvote.objects.filter(checklist=upvote.checklist).count())

		checklist_upvotes = zip(upvotes_var, upvotes_cnt_list)

		paginator = Paginator(list(checklist_upvotes), self.paginate_by)
		page = self.request.GET.get('page')

		try:
			page_checklist_upvotes = paginator.page(page)
		except PageNotAnInteger:
			page_checklist_upvotes = paginator.page(1)
		except EmptyPage:
			page_checklist_upvotes = paginator.page(paginator.num_pages)

		context['checklist_upvotes'] = page_checklist_upvotes
		context['title'] = 'bookmarks'
		context['is_paginated'] = page_checklist_upvotes.has_other_pages

		return context


# SEARCH RESULTS PAGE
class SearchChecklistListView(ListView):
	model = Checklist
	template_name = 'checklist/search_checklists.html'
	paginate_by = 5

	def get_context_data(self, **kwargs):
		context = super(SearchChecklistListView, self).get_context_data(**kwargs)

		query = ""
		if self.request.GET:
			checklists_var = None
			# if a query string is present in URL
			if ('q' in self.request.GET) and self.request.GET['q'].strip():
				query = self.request.GET['q']
				checklists_var = Checklist.objects.filter(Q(title__icontains=query) | Q(content__icontains=query))

		upvotes_cnt_list = []
		
		for checklist in checklists_var:
			upvotes_cnt_list.append(Upvote.objects.filter(checklist=checklist).count())

		checklist_upvotes = zip(checklists_var, upvotes_cnt_list)

		paginator = Paginator(list(checklist_upvotes), self.paginate_by)
		page = self.request.GET.get('page')

		try:
			page_checklist_upvotes = paginator.page(page)
		except PageNotAnInteger:
			page_checklist_upvotes = paginator.page(1)
		except EmptyPage:
			page_checklist_upvotes = paginator.page(paginator.num_pages)

		context['checklist_upvotes'] = page_checklist_upvotes
		context['title'] = 'search'
		context['is_paginated'] = page_checklist_upvotes.has_other_pages
		context['query_string'] = query

		return context


# ABOUT PAGE
def about(request):
	return render(request, 'checklist/about.html', {'title_new': 'about'})


# UPVOTE POST FUNCTIONALITY
def upvote_checklist(request, checklist_id):
	# for "messages", refer https://stackoverflow.com/a/61603003/6543250
	
	""" if user cannot retract upvote, then this code be uncommented
	if Upvote.objects.filter(user=User.objects.filter(username=username).first(), checklist=Checklist.objects.get(id=checklist_id)):
		msg = 'You have already upvoted the checklist once!'
		messages.info(request, msg)
	"""
	if Checklist.objects.get(id=checklist_id).author == request.user:
		msg = 'Action Denied! You cannot upvote your own checklist!'
		messages.info(request, msg)
	else:
		# remove user's upvote if he has already upvoted
		obj = Upvote.objects.filter(user=request.user, checklist=Checklist.objects.get(id=checklist_id))
		if obj:
			obj.delete()
			msg = 'Upvote retracted!'
			messages.info(request, msg)
		else:
			# if fetching by id, use "get()", else "filter()" 
			# User.objects.filter(username=username).first()
			upvote_obj = Upvote(user=request.user, checklist=Checklist.objects.get(id=checklist_id))
			upvote_obj.save()

			msg = 'Checklist upvoted!'
			messages.info(request, msg)

	# redirect to home url; simply reload the page
	# return redirect('checklist-home')
	return redirect(request.META.get('HTTP_REFERER', 'checklist-home'))


# BOOKMARK FUNCTIONALITY
def bookmark_checklist(request, checklist_id):
	# remove user's bookmark if he has already bookmarked
	if Checklist.objects.get(id=checklist_id).author == request.user:
		msg = 'Action Denied! You cannot bookmark your own checklist!'
		messages.info(request, msg)
	else:

		obj = Bookmark.objects.filter(user=request.user, checklist=Checklist.objects.get(id=checklist_id))
		if obj:
			obj.delete()
			msg = 'Bookmark removed!'
			messages.info(request, msg)
		else:
			bookmark_obj = Bookmark(user=request.user, checklist=Checklist.objects.get(id=checklist_id))
			bookmark_obj.save()

			msg = 'Checklist bookmarked!'
			messages.info(request, msg)

	return redirect(request.META.get('HTTP_REFERER', 'checklist-home'))


# @DEPRECATED
# HOME - show all checklists - this function will be called when user navigates to "localhost:8000/"
def home(request):
	# count upvotes for each post
	upvotes_cnt_list = []
	checklists_var = Checklist.objects.all().order_by('-date_posted')
	for checklist in checklists_var:
		upvotes_cnt_list.append(Upvote.objects.filter(checklist=checklist).count())

	checklist_upvotes = zip(checklists_var, upvotes_cnt_list)

	paginate_by = 5
	paginator = Paginator(list(checklist_upvotes), paginate_by)
	page = request.GET.get('page')

	try:
		page_checklist_upvotes = paginator.page(page)
	except PageNotAnInteger:
		page_checklist_upvotes = paginator.page(1)
	except EmptyPage:
		page_checklist_upvotes = paginator.page(paginator.num_pages)

	context = {
		'checklist_upvotes': page_checklist_upvotes,
		'title': 'home',
		'is_paginated': True
	}

	return render(request, 'checklist/home.html', context) # because render looks in templates subdirectory, by default


# @DEPRECATED
# SHOW CHECKLISTS POSTED BY LOGGED IN USER
def mychecklist(request):
	context = {
		'checklists_var': request.user.checklist_set.all().order_by('-date_posted'),
		'title': 'My Checklists'
	}

	return render(request, 'checklist/mychecklist.html', context) # because render looks in templates subdirectory, by default


# @DEPRECATED
# VIWE BOOKMARKS PAGE | ALTERNATE - can be used if "BookmarkChecklistListView" does not work
def mybookmark(request):
	context = {
		'bookmarks_var': Bookmark.objects.filter(user=request.user),
		'title': 'My Bookmarks'
	}

	return render(request, 'checklist/mybookmark.html', context) # because render looks in templates subdirectory, by default
