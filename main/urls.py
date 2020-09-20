from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('catalog/<int:oid>', views.catalog),
    path('add-folder/<int:parent>', views.add_folder),
    path('add-material/<int:parent>', views.add_material),
]
