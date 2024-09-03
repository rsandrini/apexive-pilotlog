from django.contrib import admin
from .models.dynamic_table import DynamicTable

class DynamicTableAdmin(admin.ModelAdmin):
    model = DynamicTable
    list_display = ['table', 'guid', 'user_id', '_modified']
    search_fields = ['user_id', 'table', 'guid']


admin.site.register(DynamicTable, DynamicTableAdmin)