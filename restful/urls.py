from django.urls import path, include
from rest_framework import routers

from . import views

app_name = 'restful'

router = routers.DefaultRouter(trailing_slash=False)

router.register('games', views.GameViewSet)
router.register('users', views.UserViewSet)
router.register('login', views.LoginViewSet, basename='login')
urlpatterns = [
    path('', include(router.urls))
]
