from django.contrib import admin
from .models import ServiceItem, ServiceImage, Order, AgencySettings

@admin.register(ServiceItem)
class ServiceItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'service_type', 'price', 'sort_order', 'is_active')
    list_editable = ('price', 'sort_order', 'is_active')
    list_filter = ('service_type', 'is_active')
    search_fields = ('title', 'description')

@admin.register(ServiceImage)
class ServiceImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'service', 'sort_order')
    list_editable = ('sort_order',)
    search_fields = ('service__title',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'service_title', 'status', 'amount_paid', 'created_at')
    list_editable = ('status',)
    list_filter = ('status', 'payment_type')
    search_fields = ('customer_name', 'service_title')

@admin.register(AgencySettings)
class AgencySettingsAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone1', 'phone2', 'email')