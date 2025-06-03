from django import forms
from .models import Conquista

class ConquistaForm(forms.ModelForm):
    class Meta:
        model = Conquista
        fields = ['nmconquista', 'dsconquista', 'nmimagem', 'expconquista']