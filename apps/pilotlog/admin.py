from django.contrib import admin
from .models.dynamic_model import DynamicModel

class DynamicModelAdmin(admin.ModelAdmin):
    model = DynamicModel
    list_display = ['table', 'guid', 'user_id', '_modified']
    search_fields = ['user_id', 'table', 'guid']


admin.site.register(DynamicModel, DynamicModelAdmin)