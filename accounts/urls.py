from django.urls import path
from .views import *

urlpatterns = [
    path('reg',register_view,name='reg'),
    path('log',LoginView.as_view(),name='log'),
    path('logout',LogoutView.as_view(),name='logout'),
    path('sociallog',social_registration_view,name='sociallog'),
]
