from django import forms
from .models import Paciente
class PacienteForm(forms.ModelForm):
    class Meta: model=Paciente; fields='__all__'
    def clean_dni(self):
        dni=self.cleaned_data['dni']
        if not dni.isdigit() or len(dni)!=8: raise forms.ValidationError('El DNI debe tener ocho dígitos.')
        return dni
    def clean(self):
        data=super().clean()
        if data.get('tipo')=='estudiante' and not data.get('email','').lower().endswith('@uncp.edu.pe'): self.add_error('email','Correo institucional @uncp.edu.pe obligatorio.')
        return data
