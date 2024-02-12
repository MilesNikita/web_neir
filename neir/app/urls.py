from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('neural_network/', views.neural_network, name='neural_network'),
]
