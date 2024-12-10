from django.contrib import admin
from apps.testbase.models import Test, Topic


class TopicAdmin(admin.ModelAdmin):
    list_display = ('name',)

class TestAdmin(admin.ModelAdmin):
    list_display = ('id','category', 'topic', 'question')


admin.site.register(Test, TestAdmin)
admin.site.register(Topic)
