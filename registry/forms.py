from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import RegistryEntry

class RegisterForm(UserCreationForm):
    username = forms.CharField(label="Логин", max_length=150)
    email = forms.EmailField(label="Email", required=False)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

class RegistryEntryForm(forms.ModelForm):
    class Meta:
        model = RegistryEntry
        fields = [
            "building", "section", "mtr", "quantity", "works",
            "paid_date", "delivery_deadline", "done", "responsible"
        ]

class ANApprovalForm(forms.ModelForm):
    class Meta:
        model = RegistryEntry
        fields = []  # подтверждение кнопкой

class GIPApprovalForm(forms.ModelForm):
    class Meta:
        model = RegistryEntry
        fields = []

