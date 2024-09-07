from django.contrib import admin
from .models.aircraft import Aircraft
from .models.flight import Flight
from .models.image_pic import ImagePic
from .models.my_query_build import MyQueryBuild
from .models.my_query import MyQuery
from .models.limit_rules import LimitRules
from .models.pilot import Pilot
from .models.qualification import Qualification
from .models.setting_config import SettingConfig


class AircraftAdmin(admin.ModelAdmin):
    model = Aircraft
    list_display = ['guid', 'user_id', '_modified']
    search_fields = ['user_id', 'guid', 'meta']


class FlightAdmin(admin.ModelAdmin):
    model = Flight
    list_display = ['guid', 'aircraft__guid', 'user_id', '_modified']
    search_fields = ['user_id', 'aircraft__guid', 'guid', 'meta']
    readonly_fields = ['aircraft']


class ImagePicAdmin(admin.ModelAdmin):
    model = ImagePic
    list_display = ['guid', 'user_id', '_modified']
    search_fields = ['user_id', 'guid']


class LimitRulesAdmin(admin.ModelAdmin):
    model = LimitRules
    list_display = ['guid', 'user_id', '_modified']
    search_fields = ['user_id', 'guid']


class MyQueryAdmin(admin.ModelAdmin):
    model = MyQuery
    list_display = ['guid', 'user_id', '_modified']
    search_fields = ['user_id', 'guid']


class MyQueryBuildAdmin(admin.ModelAdmin):
    model = MyQueryBuild
    list_display = ['guid', 'user_id', '_modified']
    search_fields = ['user_id', 'guid']


class PilotAdmin(admin.ModelAdmin):
    model = Pilot
    list_display = ['guid', 'user_id', '_modified']
    search_fields = ['user_id', 'guid']


class QualificationAdmin(admin.ModelAdmin):
    model = Qualification
    list_display = ['guid', 'user_id', '_modified']
    search_fields = ['user_id', 'guid']


class SettingConfigAdmin(admin.ModelAdmin):
    model = SettingConfig
    list_display = ['guid', 'user_id', '_modified']
    search_fields = ['user_id', 'guid']


admin.site.register(Aircraft, AircraftAdmin)
admin.site.register(Flight, FlightAdmin)
admin.site.register(ImagePic, ImagePicAdmin)
admin.site.register(LimitRules, LimitRulesAdmin)
admin.site.register(MyQuery, MyQueryAdmin)
admin.site.register(MyQueryBuild, MyQueryBuildAdmin)
admin.site.register(Pilot, PilotAdmin)
admin.site.register(Qualification, QualificationAdmin)
admin.site.register(SettingConfig, SettingConfigAdmin)
