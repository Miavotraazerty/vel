from django import forms
from django.contrib.auth.models import User

class ProfilForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']
