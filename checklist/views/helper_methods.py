from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator


def paginate_content(checklist_upvotes, page, paginate_by=5):
    # add paginator object
    paginator = Paginator(list(checklist_upvotes), paginate_by)

    try:
        page_checklist_upvotes = paginator.page(page)
    except PageNotAnInteger:
        page_checklist_upvotes = paginator.page(1)
    except EmptyPage:
        page_checklist_upvotes = paginator.page(paginator.num_pages)

    return page_checklist_upvotes


def get_upvote_bookmark_list(checklists_var, is_anonymous, user):
    upvotes_cnt_list = []
    upvoted_bool_list = []
    bookmarked_bool_list = []

    for checklist in checklists_var:
        # for each checklist, fetch the count of upvotes
        # upvote_set - set of all upvotes who have foreign key checklist as the current checklist
        upvotes_cnt_list.append(checklist.upvote_set.count())

        # if user is not anonymous
        if not is_anonymous:

            # if any of the upvote objects have this checklist as foreign key and the user for that object is the current logged in user, then append True to the list
            if checklist.upvote_set.filter(user=user):
                upvoted_bool_list.append(True)
            else:
                upvoted_bool_list.append(False)

            if checklist.bookmark_set.filter(user=user):
                bookmarked_bool_list.append(True)
            else:
                bookmarked_bool_list.append(False)
        # need this else clause so that empty lists for upvoted and bookmarked are not passed in checklist_upvotes while zipping
        else:
            upvoted_bool_list.append(True)
            bookmarked_bool_list.append(True)

    return upvotes_cnt_list, upvoted_bool_list, bookmarked_bool_list
