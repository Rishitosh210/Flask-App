from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import Permission,Group

def is_analytics(user):
    return Group.objects.get()