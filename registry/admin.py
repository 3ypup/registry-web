from django.contrib import admin
from .models import RegistryEntry

@admin.register(RegistryEntry)
class RegistryEntryAdmin(admin.ModelAdmin):
    list_display = (
        "id","building","section","mtr","quantity",
        "an_approved","gip_approved","paid_date","delivery_deadline","done","responsible",
        "created_by","created_at"
    )
    list_filter = ("an_approved","gip_approved","done","paid_date","delivery_deadline","created_at")
    search_fields = ("building","section","mtr","works","responsible","created_by__username")
    readonly_fields = ("created_at","updated_at","an_approved_by","an_approved_at","gip_approved_by","gip_approved_at","created_by")

