from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone

User = settings.AUTH_USER_MODEL

class RegistryEntry(models.Model):
    building = models.CharField("Здание", max_length=200)
    section = models.CharField("Раздел", max_length=200)
    mtr = models.CharField("МТР", max_length=300)
    quantity = models.PositiveIntegerField("Кол-во", validators=[MinValueValidator(1)])
    works = models.TextField("Работы", blank=True)

    an_approved = models.BooleanField("Согласовано АН", default=False)
    an_approved_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name="an_approvals"
    )
    an_approved_at = models.DateTimeField(null=True, blank=True)

    gip_approved = models.BooleanField("Согласовано ГИП", default=False)
    gip_approved_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name="gip_approvals"
    )
    gip_approved_at = models.DateTimeField(null=True, blank=True)

    paid_date = models.DateField("Оплачено (дата)", null=True, blank=True)
    delivery_deadline = models.DateField("Сроки поставки/завершения", null=True, blank=True)

    done = models.BooleanField("Выполнено", default=False)
    responsible = models.CharField("Ответственный", max_length=200)

    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="created_entries")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def clean(self):
        # Валидация "звёздочных" согласований + логические правила
        if self.paid_date and not (self.an_approved and self.gip_approved):
            raise ValidationError("Нельзя поставить 'Оплачено', пока не согласовано АН и ГИП.")

        if self.done and not (self.an_approved and self.gip_approved):
            raise ValidationError("Нельзя отметить 'Выполнено' без согласования АН и ГИП.")

        if self.done and not self.works.strip():
            raise ValidationError("Для 'Выполнено' заполните поле 'Работы'.")

    def set_approval(self, kind: str, user):
        now = timezone.now()
        if kind == "an":
            self.an_approved = True
            self.an_approved_by = user
            self.an_approved_at = now
        elif kind == "gip":
            self.gip_approved = True
            self.gip_approved_by = user
            self.gip_approved_at = now
        else:
            raise ValueError("Unknown approval kind")

