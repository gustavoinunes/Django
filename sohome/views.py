from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required


@login_required(login_url='')
def home(request):
        return render(request, 'home.html')