from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('tabriklar/', views.tabriklar_view, name='tabriklar'),
    path('bezaklar/', views.bezaklar_view, name='bezaklar'),
    path('xizmat/<int:pk>/', views.service_detail, name='service_detail'),
    path('kontaktlar/', views.contacts, name='contacts'),
    path('buyurtma/', views.create_order, name='create_order'),
    # API endpoints for bots
    path('api/xizmat/<int:pk>/', views.get_service_api, name='service_api'),
    path('api/xizmatlar/', views.get_services_api, name='services_api'),
    path('api/buyurtmalar/', views.admin_orders_api, name='orders_api'),
]
