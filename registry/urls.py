from django.urls import path
from . import views

app_name = "registry"

urlpatterns = [
    path("", views.entry_list, name="list"),
    path("new/", views.entry_create, name="create"),
    path("<int:pk>/edit/", views.entry_edit, name="edit"),
    path("<int:pk>/approve-an/", views.approve_an, name="approve_an"),
    path("<int:pk>/approve-gip/", views.approve_gip, name="approve_gip"),
    path("export/csv/", views.export_csv, name="export_csv"),
]

