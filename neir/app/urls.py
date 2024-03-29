from django.urls import path
from . import views
from django.views.generic import RedirectView
from .views import login_view
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', RedirectView.as_view(url='/login/')),
    path('login/', login_view, name='login'),
    path('neural_network/', views.neural_network, name='neural_network'),
    path('run_neural_network/', views.run_neural_network, name='run_neural_network'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)