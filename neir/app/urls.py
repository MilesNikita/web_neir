from django.urls import path
from . import views
from django.views.generic import RedirectView
from .views import login_view

urlpatterns = [
    path('', RedirectView.as_view(url='/login/')),
    path('login/', login_view, name='login'),
    path('neural_network/', views.neural_network, name='neural_network'),
]
