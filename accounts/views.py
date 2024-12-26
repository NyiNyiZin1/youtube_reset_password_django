from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import *
from django.contrib.auth import authenticate, login, logout
from .helpers import send_forget_password_mail


def Login(request):
    try:
        if request.method == "POST":
            username = request.POST.get("username")
            password = request.POST.get("password")

            if not username or not password:
                messages.success(request, "Both Username and Password are required.")
                return redirect("/login/")
            user_obj = User.objects.filter(username=username).first()
            if user_obj is None:
                messages.success(request, "User not found.")
                return redirect("/login/")

            user = authenticate(username=username, password=password)

            if user is None:
                messages.success(request, "Wrong password.")
                return redirect("/login/")

            login(request, user)
            return redirect("/")

    except Exception as e:
        print(e)
    return render(request, "login.html")


def Register(request):
    try:
        if request.method == "POST":
            username = request.POST.get("username")
            email = request.POST.get("email")
            password = request.POST.get("password")

        try:
            if User.objects.filter(username=username).first():
                messages.success(request, "Username is taken.")
                return redirect("/register/")

            if User.objects.filter(email=email).first():
                messages.success(request, "Email is taken.")
                return redirect("/register/")

            user_obj = User(username=username, email=email)
            user_obj.set_password(password)
            user_obj.save()

            profile_obj = Profile.objects.create(user=user_obj)
            profile_obj.save()
            return redirect("/login/")

        except Exception as e:
            print(e)

    except Exception as e:
        print(e)

    return render(request, "register.html")


def Logout(request):
    logout(request)
    return redirect("/")


@login_required(login_url="/login/")
def Home(request):
    return render(request, "home.html")


def ChangePassword(request, token):
    context = {}
    print("token", token)
    try:
        profile_obj = Profile.objects.filter(forget_password_token=token).first()
        # profile_obj = User.objects.filter(forget_password_token = token).first()
        print("profile_obj", profile_obj)
        context = {"user_id": profile_obj.user.id}
        print("context", context)
        if request.method == "POST":
            new_password = request.POST.get("new_password")
            confirm_password = request.POST.get("reconfirm_password")
            user_id = request.POST.get("user_id")
            print("user_id", user_id)
            if user_id is None:
                messages.success(request, "No user id found.")
                return redirect(f"/change-password/{token}/")

            if new_password != confirm_password:
                print("new_password", new_password)
                messages.success(request, "both should  be equal.")
                return redirect(f"/change-password/{token}/")

            user_obj = User.objects.get(id=user_id)
            user_obj.set_password(new_password)
            print("user_obj", user_obj)
            user_obj.save()
            return redirect("/login/")

    except Exception as e:
        print(e)
    return render(request, "change-password.html", context)


import uuid


def ForgetPassword(request):
    try:
        if request.method == "POST":
            print("Start An email is sent.>>>>>>>>")
            username = request.POST.get("username")
            print("username>>>>>>>>", username)
            if not User.objects.filter(username=username).first():
                messages.success(request, "Not user found with this username.")
                return redirect("/forget-password/")

            user_obj = User.objects.get(username=username)
            print("user_obj>>>>>>>>", user_obj)
            token = str(uuid.uuid4())
            print("user>>>>>>>>", username)
            # profile_obj, created = User.objects.get_or_create(username=user_obj)
            profile_obj, created = Profile.objects.get_or_create(user=user_obj)
            # player, created = UserProfile.objects.get_or_create(user=request.user)
            print("profile_obj1>>>>>>>>", profile_obj)
            profile_obj.forget_password_token = token
            print("profile_obj2>>>>>>>>", profile_obj)
            profile_obj.save()
            send_forget_password_mail(user_obj.email, token)
            print("End An email is sent.>>>>>>>>")
            messages.success(request, "An email is sent.")
            return redirect("/forget-password/")

    except Exception as e:
        print(e)
    return render(request, "forget-password.html")
