from django.urls import path
from django.shortcuts import redirect
from . import views

urlpatterns = [
    path('', views.index),
    path('catalog/<int:oid>', views.catalog),
    path('add-folder/<int:parent>', views.add_folder),
    path('add-material/<int:parent>', views.add_material),
    path('del-folder/<int:fid>', views.del_folder),
    path('del-material/<int:mid>', views.del_material),
    path('edit-folder/<int:fid>', views.edit_folder),
    path('edit-material/<int:mid>', views.edit_material),
    path('stock/<int:page>', views.stock),
    path('stock', lambda r: redirect('/stock/1')),
    path('add-task/<int:mid>/<str:count>/<str:price>/<str:for_order>', views.add_task, name='add-task'),
    path('create-order/', views.create_order),
    path('create-order/<int:additional>', views.create_order),
    path('stock/confirm/<int:mid>', views.confirm_stock_material),
    path('stock/edit/<int:mid>/<int:nid>', views.edit_stock_material),
    path('stock/delete/<int:mid>', views.delete_stock_material),
    path('api/get-all-materials', views.get_all_materials),
    path('test', views.test),
    path('api/get-units/<int:mid>', views.get_units),
    path('tasks', views.tasks),
    path('tasks/search/<str:text>', views.tasks_search),
    path('api/get-order-list', views.get_order_list),
    path('order/<str:oid>', views.order),
    path('order/<str:oid>/<int:additional>', views.order),
    path('edit-order/<str:oid>', views.edit_order),
    path('edit-order/<str:oid>/<int:additional>', views.edit_order),
    path('add-to-stock/<int:mid>', views.add_to_stock),
    path('catalog/search/<str:text>', views.catalog_search),
    path('stock/search/<str:text>/<int:page>', views.stock_search),
    path('mark-arrival/<int:mid>/<str:count>/<str:price>', views.mark_arrival),
    path('archive', views.archive),
    path('archive/<int:page>', views.archive),
    path('archive/<int:page>/<int:for_order>', views.archive),
    path('archive/search/<str:text>', views.archive_search),
    path('archive/search/<str:text>/<int:page>', views.archive_search),
    path('archive/search/<str:text>/<int:page>/<int:for_order>', views.archive_search),
    path('orders', views.orders),
    path('api/get-last-price/<int:mid>', views.get_last_price),
    path('api/order-to-work/<str:oid>', views.order_to_work),
    path('api/confirm-order/<str:oid>', views.confirm_order)
]
