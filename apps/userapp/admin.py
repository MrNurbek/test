from multiprocessing.resource_tracker import register
from django.contrib import admin
from apps.userapp.models import User

admin.site.register(User)
