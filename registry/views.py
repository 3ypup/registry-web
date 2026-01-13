import csv
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.db.models import Q

from .models import RegistryEntry
from .forms import RegisterForm, RegistryEntryForm

ROLE_EMPLOYEE = "employee"
ROLE_AN = "an"
ROLE_GIP = "gip"
ROLE_ADMIN = "admin"

def user_in(group_name: str, user) -> bool:
    return user.is_superuser or user.groups.filter(name=group_name).exists()

class RegisterView(CreateView):
    template_name = "registration/register.html"
    form_class = RegisterForm
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        resp = super().form_valid(form)
        # по умолчанию все новые — сотрудники
        employee, _ = Group.objects.get_or_create(name=ROLE_EMPLOYEE)
        self.object.groups.add(employee)
        return resp

@login_required
def entry_list(request):
    q = request.GET.get("q", "").strip()
    qs = RegistryEntry.objects.all()

    if q:
        qs = qs.filter(
            Q(building__icontains=q) |
            Q(section__icontains=q) |
            Q(mtr__icontains=q) |
            Q(works__icontains=q) |
            Q(responsible__icontains=q)
        )

    # сотрудники видят всё (обычно так в реестре), но можно легко ограничить до created_by=request.user
    can_approve_an = user_in(ROLE_AN, request.user)
    can_approve_gip = user_in(ROLE_GIP, request.user)
    can_export = user_in(ROLE_ADMIN, request.user)

    return render(request, "registry/list.html", {
        "entries": qs[:500],  # простое ограничение
        "q": q,
        "can_approve_an": can_approve_an,
        "can_approve_gip": can_approve_gip,
        "can_export": can_export,
    })

@login_required
def entry_create(request):
    if request.method == "POST":
        form = RegistryEntryForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.created_by = request.user
            obj.full_clean()
            obj.save()
            return redirect("registry:list")
    else:
        form = RegistryEntryForm()
    return render(request, "registry/form.html", {"form": form, "title": "Новая запись"})

@login_required
def entry_edit(request, pk: int):
    obj = get_object_or_404(RegistryEntry, pk=pk)

    # простая политика: править может создатель, админ; после оплат/выполнено — только админ
    if (obj.created_by != request.user) and not user_in(ROLE_ADMIN, request.user):
        return HttpResponseForbidden("Нет прав на редактирование.")

    if (obj.paid_date or obj.done) and not user_in(ROLE_ADMIN, request.user):
        return HttpResponseForbidden("После оплаты/выполнения редактирование доступно только админу.")

    if request.method == "POST":
        form = RegistryEntryForm(request.POST, instance=obj)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.full_clean()
            obj.save()
            return redirect("registry:list")
    else:
        form = RegistryEntryForm(instance=obj)

    return render(request, "registry/form.html", {"form": form, "title": f"Редактирование #{obj.id}"})

@login_required
def approve_an(request, pk: int):
    if not user_in(ROLE_AN, request.user):
        return HttpResponseForbidden("Нужна роль АН.")
    obj = get_object_or_404(RegistryEntry, pk=pk)
    obj.set_approval("an", request.user)
    obj.full_clean()
    obj.save()
    return redirect("registry:list")

@login_required
def approve_gip(request, pk: int):
    if not user_in(ROLE_GIP, request.user):
        return HttpResponseForbidden("Нужна роль ГИП.")
    obj = get_object_or_404(RegistryEntry, pk=pk)
    obj.set_approval("gip", request.user)
    obj.full_clean()
    obj.save()
    return redirect("registry:list")

@login_required
def export_csv(request):
    if not user_in(ROLE_ADMIN, request.user):
        return HttpResponseForbidden("Экспорт доступен только админу.")

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="registry.csv"'

    writer = csv.writer(response)
    writer.writerow([
        "Здание","Раздел","МТР","Кол-во","Работы",
        "Согласовано АН","Согласовано ГИП","Оплачено(дата)",
        "Сроки поставки/завершения","Выполнено","Ответственный"
    ])

    for e in RegistryEntry.objects.all().order_by("-created_at"):
        writer.writerow([
            e.building, e.section, e.mtr, e.quantity, e.works,
            "Да" if e.an_approved else "Нет",
            "Да" if e.gip_approved else "Нет",
            e.paid_date.isoformat() if e.paid_date else "",
            e.delivery_deadline.isoformat() if e.delivery_deadline else "",
            "Да" if e.done else "Нет",
            e.responsible
        ])
    return response

