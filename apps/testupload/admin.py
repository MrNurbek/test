from django.contrib import admin

from apps.testupload.models import NewTestUpload


class NewTestUploadAdmin(admin.ModelAdmin):
    list_display = ('category', 'topic_name', 'created_at')

admin.site.register(NewTestUpload, NewTestUploadAdmin)

