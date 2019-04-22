from .models import *
import django_filters

class UserFilter(django_filters.FilterSet):
    class Meta:
        model = User
        fields = {
            "email" : ["exact"]
        }