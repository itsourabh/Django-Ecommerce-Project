from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from core.models import *
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout


# Create your views here.
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        messages.info(request, "Login failed. Please try again.")

    return render(request, 'accounts/login.html')

def user_register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        phone = request.POST.get('phone')
        # print(username, email)
        if password == confirm_password:
            if User.objects.filter(username=username).exists():
                messages.info(request, "User Already Exists")
                return redirect('user_register')
            else:
                if User.objects.filter(email=email).exists():
                    messages.info(request, "Email Already Exists")
                    return redirect('user_register')
                else:
                    user = User.objects.create_user(username=username, email=email, password=password)
                    user.save()
                    data = Customer(user = user, phone_field = phone)
                    data.save()
                    
                    
                    
                    # Code for Login of user will come here
                    our_user = authenticate(username=username, password=password)
                    if our_user is not None:
                        login(request, our_user)
                        return redirect('/')
        else:
            messages.info(request, "Password and Confirm Password Mismatch")
            return redirect('user_register')
    return render(request, 'accounts/register.html')


def user_logout(request):
    logout(request)
    return redirect('/')