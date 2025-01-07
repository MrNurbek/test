from django.contrib import admin
from datetime import timedelta
from apps.exam.models import Exam
from django.forms import DurationField, forms




@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('category', 'start_time', 'end_time', 'total_questions', 'time_limit')
    fields = ('category', 'topics', 'start_time', 'end_time', 'total_questions', 'time_limit')

    def save_model(self, request, obj, form, change):

        if isinstance(obj.time_limit, timedelta):
            obj.time_limit = obj.time_limit
        elif isinstance(obj.time_limit, str):
            h, m, s = map(int, obj.time_limit.split(':'))
            obj.time_limit = timedelta(hours=h, minutes=m, seconds=s)
        else:
            obj.time_limit = timedelta(minutes=30)
        super().save_model(request, obj, form, change)

