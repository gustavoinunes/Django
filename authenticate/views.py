from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from .forms import SignUpForm, EditProfileForm, ChangePasswordForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from sohome.views import home


def login_user(request):
    if request.method == 'POST':
        usuario = request.POST.get('username')
        senha = request.POST.get('password')
        user = authenticate(request, username=usuario, password=senha)
        if user is not None:
            login(request, user)
            messages.success(request, 'You have been logged in successfully')
            return redirect(home)
        else:
            messages.warning(request, "Username or Password is incorrect !!")
            return redirect('login')
    else:
        return render(request, 'login.html') 

@login_required
def logout_user(request):
    logout(request)
    return redirect('login')


def register_user(request):
    if request.method == 'POST':
        nome = request.POST.get('first_name')
        sobrenome = request.POST.get('last_name')
        e_mail = request.POST.get('email')
        usuario = request.POST.get('username')
        senha = request.POST.get('password')
        user = User.objects.create_user(first_name=nome, last_name=sobrenome, email=e_mail, username=usuario, password=senha)
        login(request, user)
        return redirect('login')
    else:
        return render(request, 'register.html')


# @login_required()
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile Updated Successfully")
            return redirect(home)
    else:
        form = EditProfileForm(instance=request.user)
    context = {
        'form': form,
    }
    return render(request, 'edit_profile.html', context)


def change_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(data=request.POST, user=request.user)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, "Password Changed Successfully")
            return redirect(home)
    else:
        form = ChangePasswordForm(user=request.user)
        print(form)
    context = {
        'form': form,
    }
    return render(request, 'change_password.html', context)
