from django.urls import path

from . import views


urlpatterns = [
    path('<str:string>/', views.draw_menu, name='string')
]
