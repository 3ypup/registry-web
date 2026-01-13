from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

ROLE_EMPLOYEE = "employee"
ROLE_AN = "an"
ROLE_GIP = "gip"
ROLE_ADMIN = "admin"

class Command(BaseCommand):
    help = "Create default groups/roles"

    def handle(self, *args, **options):
        for name in [ROLE_EMPLOYEE, ROLE_AN, ROLE_GIP, ROLE_ADMIN]:
            Group.objects.get_or_create(name=name)
        self.stdout.write(self.style.SUCCESS("Roles ensured: employee, an, gip, admin"))

