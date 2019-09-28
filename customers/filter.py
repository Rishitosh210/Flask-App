from audtech_analytics.models import FinalTable
import django_filters

class FinalTableFilter(django_filters.FilterSet):
    class Meta:
        model = FinalTable
        fields= ['MainAccountCode','MainAccountName','SubAccountCode','SubAccountName','AccountCategory','JournalDate']