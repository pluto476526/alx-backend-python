import django_filters
from .models import Message
from django.utils import timezone

class MessageFilter(django_filters.FilterSet):
    start_date = django_filters.DateTimeFilter(field_name='sent_at', lookup_expr='gte')
    end_date = django_filters.DateTimeFilter(field_name='sent_at', lookup_expr='lte')
    sender = django_filters.CharFilter(field_name='sender__username', lookup_expr='iexact')
    conversation = django_filters.NumberFilter(field_name='conversation__id')

    class Meta:
        model = Message
        fields = ['sender', 'conversation', 'start_date', 'end_date']

