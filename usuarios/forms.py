from django import forms
from .models import Usuario

class ConfigUsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nmusuario', 'emailusuario', 'dtnascimento']