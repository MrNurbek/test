from django_filters import rest_framework as filters

from apps.exam.models import Exam


class ExamFilter(filters.FilterSet):
    id = filters.NumberFilter(field_name='id', lookup_expr='exact', help_text='Imtihon ID bo‘yicha filter')

    class Meta:
        model = Exam
        fields = ['id']
