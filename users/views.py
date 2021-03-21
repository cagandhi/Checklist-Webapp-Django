import os

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeDoneView  # noqa: F401
from django.shortcuts import redirect, render

from .forms import ProfileUpdateForm, UserRegisterForm, UserUpdateForm


# Create your views here.
def register(request):
    if request.method == "POST":
        # when POST request, fetch the form with the filled form data
        form = UserRegisterForm(request.POST)

        # if form is valid, save the form and display success message
        # Django builtin UserCreationForm checks whether the user already exists or not
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            messages.success(
                request,
                f"Your account with username {username} has been created successfully! You can now log in!",
            )

            # redirect to login page once account is created successfully
            return redirect("login")
    else:
        # when GET request, simply render a new form
        form = UserRegisterForm()

    # if form data is invalid or GET request, render the register page again with filled form data or new empty form
    return render(request, "users/register.html", {"form": form})


# "@" denotes a decorator - user must be logged in to access this page
@login_required
def profile(request):
    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=request.user)
        # additional data which is user uploaded image data which comes with the request
        p_form = ProfileUpdateForm(
            request.POST, request.FILES, instance=request.user.profile
        )
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    old_image_url = request.user.profile.image.url

    if u_form.is_valid() and p_form.is_valid():
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # save user and profile forms
        u_form.save()
        p_form.save()

        try:
            # if old image url is that of default image, we don't need to remove that file from the machine
            if old_image_url.split("/")[-1] != "default.jpg":

                # remove old image so that unused profile pics don't clutter space
                os.remove(BASE_DIR + old_image_url)
                # print("old image removed successfully!")

        # if image does not exist
        except OSError as err:
            # print("old image not removed")
            print(err)

        messages.success(
            request, f"Your profile has been updated successfully!"  # noqa: F541
        )

        # redirect to profile page after updating user profile

        # this sends a GET request so when we reload the form page, we don't get the message that form data will be submitted again and confirm that you want to reload the form
        return redirect("profile")

    context = {"u_form": u_form, "p_form": p_form}

    return render(request, "users/profile.html", context)
