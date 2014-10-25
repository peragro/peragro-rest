import django_filters

from damn_rest import models


from datetime import timedelta
from django.utils.timezone import now
from django_filters.filters import _truncate
from django_filters.filters import Filter


class FileReferenceFilter(django_filters.FilterSet):
    class Meta:
        model = models.FileReference
        order_by = ()
