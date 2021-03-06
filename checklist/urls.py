from django.urls import path

from . import views
from .views import (
    BookmarkChecklistListView,
    CategoryChecklistListView,
    ChecklistCreateView,
    ChecklistDeleteView,
    ChecklistDetailView,
    ChecklistListView,
    ChecklistUpdateView,
    ItemCreateView,
    ItemDetailView,
    ItemUpdateView,
    SearchChecklistListView,
    UpvoteChecklistListView,
    UserChecklistListView,
    UserDraftChecklistListView,
)

urlpatterns = [
    path("", ChecklistListView.as_view(), name="checklist-home"),
    path(
        "user/<str:username>/",
        UserChecklistListView.as_view(),
        name="user-checklists",
    ),
    path("user/<str:username>/follow", views.follow_user, name="user-follow"),
    path(
        "checklist/drafts",
        UserDraftChecklistListView.as_view(),
        name="user-drafts",
    ),
    path("bookmarks/", BookmarkChecklistListView.as_view(), name="bookmarks"),
    path("mybookmark/", views.mybookmark, name="checklist-mybookmark"),
    path("upvotes/", UpvoteChecklistListView.as_view(), name="upvotes"),
    path(
        "checklist/<int:pk>/",
        ChecklistDetailView.as_view(),
        name="checklist-detail",
    ),
    path(
        "checklist/<int:checklist_id>/publish",
        views.publish_checklist,
        name="checklist-publish",
    ),
    path(
        "checklist/<int:checklist_id>/save",
        views.save_and_edit,
        name="checklist-save",
    ),
    path(
        "checklist/new/",
        ChecklistCreateView.as_view(),
        name="checklist-create",
    ),
    path(
        "checklist/<int:pk>/update/",
        ChecklistUpdateView.as_view(),
        name="checklist-update",
    ),
    path(
        "checklist/<int:pk>/delete/",
        ChecklistDeleteView.as_view(),
        name="checklist-delete",
    ),
    path("about/", views.about, name="checklist-about"),
    # path('mychecklist/', views.mychecklist, name='checklist-mychecklist'),
    path(
        "checklist/<int:checklist_id>/upvote/",
        views.upvote_checklist,
        name="checklist-upvote",
    ),
    path(
        "checklist/<int:checklist_id>/bookmark/",
        views.bookmark_checklist,
        name="checklist-bookmark",
    ),
    path(
        "checklist/<int:checklist_id>/follow/",
        views.follow_checklist,
        name="checklist-follow",
    ),
    path("search/", SearchChecklistListView.as_view(), name="search"),
    path(
        "checklist/<str:category>/",
        CategoryChecklistListView.as_view(),
        name="category",
    ),
    path(
        "checklist/<int:checklist_id>/item/new/",
        ItemCreateView.as_view(),
        name="item-create",
    ),
    path(
        "checklist/item/<int:pk>/view/",
        ItemDetailView.as_view(),
        name="item-detail",
    ),
    path(
        "checklist/item/<int:pk>/update/",
        ItemUpdateView.as_view(),
        name="item-update",
    ),
    path(
        "checklist/item/<int:item_id>/<str:action_type>/",
        views.item_action,
        name="item-action",
    ),
    path("notif/<int:id>/dismiss/", views.dismiss_notif, name="dismiss-notif"),
    path(
        "checklist/<int:checklist_id>/comment/",
        views.submit_comment,
        name="comment-submit",
    ),
]
