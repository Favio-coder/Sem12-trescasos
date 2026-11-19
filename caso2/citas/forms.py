from datetime import datetime, time, timedelta
from django import forms
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from .models import Cita, ConsultaMedica
from medicos.models import Medico
class CitaForm(forms.ModelForm):
    class Meta:
        model=Cita; fields=['paciente','especialidad','medico','fecha','hora','motivo']; widgets={'fecha':forms.DateInput(attrs={'type':'date'}),'hora':forms.TimeInput(attrs={'type':'time'}),'motivo':forms.Textarea(attrs={'rows':3})}
    def __init__(self,*args,**kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args,**kwargs)
        if self.user and hasattr(self.user, 'perfil_paciente') and not (self.user.is_staff or self.user.has_perm('citas.add_cita')):
            self.fields['paciente'].queryset = self.fields['paciente'].queryset.filter(pk=self.user.perfil_paciente.pk)
        if 'especialidad' in self.data:
            try: self.fields['medico'].queryset=self.fields['medico'].queryset.filter(especialidad_id=int(self.data.get('especialidad')),activo=True)
            except (ValueError,TypeError): pass
        else: self.fields['medico'].queryset=self.fields['medico'].queryset.filter(activo=True)
        if self.user and hasattr(self.user, 'perfil_paciente') and not (self.user.is_staff or self.user.has_perm('citas.add_cita')):
            self.fields['paciente'].initial = self.user.perfil_paciente
            self.fields['paciente'].widget = forms.HiddenInput()
    def clean(self):
        d=super().clean(); fecha=d.get('fecha'); hora=d.get('hora'); medico=d.get('medico'); esp=d.get('especialidad'); paciente=d.get('paciente'); motivo=d.get('motivo','')
        if len(motivo.strip())<20: self.add_error('motivo','El motivo debe tener al menos 20 caracteres.')
        if fecha and fecha<timezone.localdate(): self.add_error('fecha','No se permiten fechas pasadas.')
        if medico and esp and medico.especialidad_id!=esp.id: self.add_error('medico','El médico no pertenece a esta especialidad.')
        if medico and not medico.activo: self.add_error('medico','El médico no está activo.')
        if fecha and hora:
            weekday=fecha.weekday(); apertura, cierre=(time(8),time(13)) if weekday==5 else (time(8),time(18))
            if weekday==6 or not apertura<=hora<cierre: self.add_error('hora','Fuera del horario institucional (L-V 08-18; S 08-13).')
            if medico and not medico.horarios.filter(dia_semana=weekday,hora_inicio__lte=hora,hora_fin__gt=hora).exists(): self.add_error('hora','Fuera del horario individual del médico.')
            qs=Cita.objects.filter(fecha=fecha,estado=Cita.Estado.PROGRAMADA)
            if paciente and qs.filter(paciente=paciente).exists(): self.add_error('paciente','El paciente ya tiene una cita ese día.')
            if medico:
                inicio=datetime.combine(fecha,hora)
                fin=inicio+timedelta(minutes=30)
                solapadas=qs.filter(medico=medico).exclude(pk=self.instance.pk)
                for cita in solapadas:
                    otro_inicio=datetime.combine(cita.fecha,cita.hora)
                    otro_fin=otro_inicio+timedelta(minutes=cita.duracion_minutos)
                    if inicio < otro_fin and otro_inicio < fin:
                        self.add_error('hora','El médico ya tiene una cita superpuesta en ese horario.')
                        break
                if medico.horarios.filter(dia_semana=weekday,hora_inicio__lte=hora,hora_fin__gte=(fin.time())).exists() is False:
                    self.add_error('hora','La cita completa debe estar dentro del horario individual del médico.')
        return d
    @transaction.atomic
    def save(self,commit=True):
        obj=super().save(commit=False)
        if commit:
            candidates=Cita.objects.select_for_update().filter(fecha=obj.fecha,estado='programada').exclude(pk=obj.pk)
            if candidates.filter(paciente=obj.paciente).exists():
                raise ValidationError('El paciente ya tiene una cita programada ese día.')
            start=datetime.combine(obj.fecha,obj.hora)
            end=start+timedelta(minutes=30)
            for cita in candidates.filter(medico=obj.medico):
                other_start=datetime.combine(cita.fecha,cita.hora)
                other_end=other_start+timedelta(minutes=cita.duracion_minutos)
                if start < other_end and other_start < end:
                    raise ValidationError('La disponibilidad cambió; elija otra fecha u hora.')
            obj.registrada_por=self.user if hasattr(self,'user') else None; obj.save()
        return obj


class ConsultaForm(forms.ModelForm):
    class Meta:
        model = ConsultaMedica
        fields = ['diagnostico', 'tratamiento', 'medicamentos', 'proximo_control',
                  'referencias_recetas', 'referencias_examenes', 'observaciones']
        widgets = {'proximo_control': forms.DateInput(attrs={'type': 'date'})}
