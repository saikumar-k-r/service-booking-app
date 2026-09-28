from django.contrib import admin
from .models import Service, ServiceImage, Provider, ProviderProfile, Category

admin.site.register(Service)
admin.site.register(ServiceImage)
admin.site.register(Provider)
admin.site.register(ProviderProfile)
admin.site.register(Category)