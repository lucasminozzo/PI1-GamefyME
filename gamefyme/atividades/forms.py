from django import forms
from .models import Atividade

class AtividadeForm(forms.ModelForm):
    class Meta:
        model = Atividade
        fields = ['nmatividade', 'dsatividade', 'recorrencia', 'tpestimado', 'peso']
        widgets = {
            'dsatividade': forms.Textarea(attrs={'maxlength': 200}),
        }