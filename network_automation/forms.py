from django import forms
from django.contrib.auth.models import User
from .models import Device

class DeviceFrom(forms.ModelForm):
    class Meta:
        model = Device
        fields = '__all__'

class CreateUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password')