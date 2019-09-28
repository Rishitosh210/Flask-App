from django.db import models
from tenant_schemas.models import TenantMixin
from django.contrib.auth.models import User
from audtech_project import settings
from django.contrib.auth.models import AbstractUser


class Client(TenantMixin):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
