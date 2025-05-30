from django import forms
from .models import Desafio

class DesafioForm(forms.ModelForm):
    class Meta:
        model = Desafio
        fields = ['nmdesafio', 'dsdesafio', 'tipo', 'dtinicio', 'dtfim', 'expdesafio', 'tipo_logica', 'parametro']
        widgets = {
            'dtinicio': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'dtfim': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
