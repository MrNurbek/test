from django_filters import rest_framework as filters

from apps.testbase.models import Topic


class TopicFilter(filters.FilterSet):
    category = filters.NumberFilter(field_name='category__id', lookup_expr='exact')

    class Meta:
        model = Topic
        fields = ['category']
