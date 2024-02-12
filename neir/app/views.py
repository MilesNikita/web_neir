from django.shortcuts import render

def login(request):
    return render(request, 'login.html')

def neural_network(request):
    return render(request, 'neural_network.html')