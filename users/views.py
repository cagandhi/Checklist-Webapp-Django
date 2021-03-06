import os

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeDoneView  # noqa: F401
from django.shortcuts import redirect, render

from .forms import ProfileUpdateForm, UserRegisterForm, UserUpdateForm


# Create your views here.
def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")  # noqa: F841
            messages.success(
                request,
                f"Your account has been created successfully! You can now log in!",  # noqa: F541
            )
            return redirect("login")
    else:
        form = UserRegisterForm()

    return render(request, "users/register.html", {"form": form})


# "@" denotes a decorator - user must be logged in to access this page
@login_required
def profile(request):
    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(
            request.POST, request.FILES, instance=request.user.profile
        )
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    old_image_url = request.user.profile.image.url

    if u_form.is_valid() and p_form.is_valid():
        print("OLD IMAGE")
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        print(BASE_DIR)
        print(old_image_url)
        print("OLD IMAGE")

        """
        print('-----------------------------------------------------------------')
        print('NEW IMAGE')
        print(BASE_DIR)
        print(request.user.profile.image.url)
        print('NEW IMAGE')
        """

        u_form.save()
        p_form.save()

        try:
            # don't remove default image
            if old_image_url.split("/")[-1] != "default.jpg":

                # remove old image so that unused profile pics don't clutter space
                os.remove(BASE_DIR + old_image_url)
                print("OLD IMAGE REMOVED SUCCESSFULLY")

        # if image does not exist
        except OSError:
            print("OLD IMAGE NOT REMOVED")

        messages.success(
            request,
            f"Your profile has been updated successfully!",  # noqa: F541
        )
        return redirect("profile")

    context = {"u_form": u_form, "p_form": p_form}

    return render(request, "users/profile.html", context)
