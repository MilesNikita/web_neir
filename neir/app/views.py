from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages

def login_page(request):
    return render(request, 'login.html')

def neural_network(request):
    return render(request, 'neural_network.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('neural_network') 
        else:
            messages.error(request, 'Неверное имя пользователя или пароль.')
    return render(request, 'login.html')