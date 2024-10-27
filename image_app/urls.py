from django.urls import path
from . import views

app_name = 'image_app'

urlpatterns = [
    path('', views.index, name='index'),
    path('process/<int:image_id>/', views.process_image, name='process_image'),
]
