from django.urls import path

from . import views

app_name = 'dataset'
urlpatterns = [
	path('', views.index, name='index'),
	path('<int:dataset_id>/', views.detail, name='detail'),
	path('create', views.create, name='create'),	
	path('<int:dataset_id>/run', views.run, name='run'),	
]
