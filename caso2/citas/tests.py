from datetime import date,time,timedelta
from django.test import TestCase,Client,override_settings
from django.contrib.auth.models import User, Group, Permission
from django.core.exceptions import ValidationError
from pacientes.models import Paciente
from medicos.models import Especialidad,Medico,HorarioMedico
from .forms import CitaForm
from .models import Cita, ConsultaMedica, NotaConsulta
class CitaValidationTests(TestCase):
 def setUp(self):
  self.user=User.objects.create_user('p',password='testingpass123'); self.p=Paciente.objects.create(dni='12345678',nombres='Ana',apellidos='Demo',fecha_nacimiento=date(2000,1,1),tipo='estudiante',email='ana@uncp.edu.pe'); self.e=Especialidad.objects.create(nombre='General'); self.m=Medico.objects.create(nombres='Luis',apellidos='Demo',cmp='12345',especialidad=self.e,consultorio='A1'); HorarioMedico.objects.create(medico=self.m,dia_semana=0,hora_inicio=time(8),hora_fin=time(18),consultorio='A1')
 def data(self,**kw):
  d={'paciente':self.p.pk,'especialidad':self.e.pk,'medico':self.m.pk,'fecha':date.today()+timedelta(days=(7-date.today().weekday())%7 or 7),'hora':'10:00','motivo':'Consulta médica de control general'}; d.update(kw); return d
 def test_valid_dni_and_institutional_email(self):
  from pacientes.forms import PacienteForm
  d={'dni':'99999999','nombres':'Ana','apellidos':'Demo','fecha_nacimiento':'2000-01-01','tipo':'estudiante','email':'x@uncp.edu.pe'}; self.assertTrue(PacienteForm(d).is_valid()); d['dni']='12'; self.assertFalse(PacienteForm(d).is_valid()); d['dni']='99999999'; d['email']='x@gmail.com'; self.assertFalse(PacienteForm(d).is_valid())
 def test_booking_validates_motivo_and_time(self): self.assertTrue(CitaForm(self.data()).is_valid()); self.assertFalse(CitaForm(self.data(motivo='Muy corto')).is_valid())
 def test_duplicate_patient_day_rejected(self):
  Cita.objects.create(paciente=self.p,medico=self.m,especialidad=self.e,fecha=self.data()['fecha'],hora=time(10),motivo='Consulta médica de control general')
  self.assertFalse(CitaForm(self.data(hora='11:00')).is_valid())
 def test_session_timeout_configuration(self):
  from django.conf import settings
  self.assertEqual(settings.SESSION_COOKIE_AGE,1200)
 def test_login_and_csrf_token_available(self):
  c=Client(enforce_csrf_checks=True); response=c.get('/accounts/login/'); self.assertEqual(response.status_code,200); self.assertIn('csrftoken',c.cookies)

 def test_patient_future_birth_date_rejected(self):
  from pacientes.forms import PacienteForm
  data={'dni':'87654321','nombres':'Eva','apellidos':'Prueba','fecha_nacimiento':(date.today()+timedelta(days=1)).isoformat(),'tipo':'docente','email':'eva@example.test'}
  self.assertFalse(PacienteForm(data).is_valid())

 def test_valid_patient_registration_form(self):
  from pacientes.forms import PacienteForm
  data={'dni':'87654321','nombres':'Eva','apellidos':'Prueba','fecha_nacimiento':'2000-01-01','tipo':'estudiante','email':'eva@uncp.edu.pe'}
  form=PacienteForm(data)
  self.assertTrue(form.is_valid(),form.errors)
  self.assertEqual(form.save().dni,'87654321')

 def test_valid_medical_license_registration_form(self):
  from medicos.forms import MedicoForm
  data={'nombres':'Luis','apellidos':'Prueba','cmp':'54321','especialidad':self.e.pk,'consultorio':'A1','activo':'on'}
  form=MedicoForm(data)
  self.assertTrue(form.is_valid(),form.errors)
  self.assertEqual(form.save().cmp,'54321')

 def test_medical_license_must_have_five_digits(self):
  from medicos.forms import MedicoForm
  data={'nombres':'Luis','apellidos':'Prueba','cmp':'12A','especialidad':self.e.pk,'consultorio':'A1','activo':'on'}
  form=MedicoForm(data)
  self.assertFalse(form.is_valid())
  self.assertIn('cmp',form.errors)

 def test_past_appointment_date_rejected(self):
  yesterday=date.today()-timedelta(days=1)
  self.assertFalse(CitaForm(self.data(fecha=yesterday.isoformat())).is_valid())

 def test_doctor_must_match_selected_specialty(self):
  other=Especialidad.objects.create(nombre='Pediatría')
  self.assertFalse(CitaForm(self.data(especialidad=other.pk)).is_valid())

 def test_inactive_doctor_cannot_be_booked(self):
  self.m.activo=False
  self.m.save()
  self.assertFalse(CitaForm(self.data()).is_valid())

 def test_sunday_is_not_an_institutional_working_day(self):
  sunday=date.today()+timedelta(days=(6-date.today().weekday())%7 or 7)
  self.assertFalse(CitaForm(self.data(fecha=sunday.isoformat())).is_valid())

 def test_appointment_must_fit_doctors_individual_schedule(self):
  self.assertFalse(CitaForm(self.data(hora='17:45')).is_valid())

 def test_overlapping_doctor_appointment_is_rejected(self):
  fecha=self.data()['fecha']
  Cita.objects.create(paciente=self.p,medico=self.m,especialidad=self.e,fecha=fecha,hora=time(10),motivo='Consulta médica de control general')
  other=Paciente.objects.create(dni='87654321',nombres='Eva',apellidos='Demo',fecha_nacimiento=date(2000,1,1),tipo='docente',email='eva@example.test')
  self.assertFalse(CitaForm(self.data(paciente=other.pk,hora='10:15')).is_valid())

 def test_successful_booking_can_be_saved(self):
  form=CitaForm(self.data())
  self.assertTrue(form.is_valid(),form.errors)
  cita=form.save()
  self.assertEqual(cita.paciente,self.p)
  self.assertEqual(cita.estado,Cita.Estado.PROGRAMADA)

 def test_cancellation_endpoint_requires_post(self):
  cita=Cita.objects.create(paciente=self.p,medico=self.m,especialidad=self.e,fecha=self.data()['fecha'],hora=time(10),motivo='Consulta médica de control general')
  client=Client()
  client.force_login(self.user)
  response=client.get(f'/citas/{cita.pk}/cancelar/')
  self.assertEqual(response.status_code,405)

 def test_unrelated_user_cannot_cancel_appointment(self):
  cita=Cita.objects.create(paciente=self.p,medico=self.m,especialidad=self.e,fecha=self.data()['fecha'],hora=time(10),motivo='Consulta médica de control general')
  client=Client()
  client.force_login(self.user)
  response=client.post(f'/citas/{cita.pk}/cancelar/')
  self.assertEqual(response.status_code,403)
  cita.refresh_from_db()
  self.assertEqual(cita.estado,Cita.Estado.PROGRAMADA)

 def test_patient_cannot_open_another_patients_history(self):
  from django.urls import reverse
  self.p.usuario=self.user
  self.p.save()
  other=Paciente.objects.create(dni='87654321',nombres='Eva',apellidos='Demo',fecha_nacimiento=date(2000,1,1),tipo='docente',email='eva@example.test')
  client=Client()
  client.force_login(self.user)
  response=client.get(reverse('historial',args=[other.pk]))
  self.assertEqual(response.status_code,403)

 def test_patient_can_open_only_own_history(self):
  from django.urls import reverse
  self.p.usuario=self.user
  self.p.save()
  client=Client()
  client.force_login(self.user)
  response=client.get(reverse('historial',args=[self.p.pk]))
  self.assertEqual(response.status_code,200)

 def test_denied_history_access_is_audited(self):
  from auditoria.models import AuditoriaMedica
  from django.urls import reverse
  other=Paciente.objects.create(dni='87654321',nombres='Eva',apellidos='Demo',fecha_nacimiento=date(2000,1,1),tipo='docente',email='eva@example.test')
  client=Client()
  client.force_login(self.user)
  client.get(reverse('historial',args=[other.pk]))
  self.assertTrue(AuditoriaMedica.objects.filter(paciente=other,resultado='denegado',usuario=self.user).exists())

 def test_clinical_record_is_immutable(self):
  cita=Cita.objects.create(paciente=self.p,medico=self.m,especialidad=self.e,fecha=self.data()['fecha'],hora=time(10),motivo='Consulta médica de control general')
  consulta=ConsultaMedica.objects.create(cita=cita,paciente=self.p,medico=self.m,diagnostico='Dato ficticio',tratamiento='Seguimiento')
  consulta.diagnostico='Alterado'
  with self.assertRaises(ValidationError):
   consulta.save()

 def test_non_doctor_cannot_register_a_consultation(self):
  cita=Cita.objects.create(paciente=self.p,medico=self.m,especialidad=self.e,fecha=self.data()['fecha'],hora=time(10),motivo='Consulta médica de control general')
  client=Client()
  client.force_login(self.user)
  response=client.get(f'/citas/{cita.pk}/consulta/')
  self.assertEqual(response.status_code,403)

 def test_admin_bulk_completion_requires_change_permission(self):
  from citas.admin import completar
  from django.contrib.admin.sites import AdminSite
  cita=Cita.objects.create(paciente=self.p,medico=self.m,especialidad=self.e,fecha=self.data()['fecha'],hora=time(10),motivo='Consulta médica de control general')
  request=type('Request',(),{'user':self.user})()
  completar(None,request,Cita.objects.filter(pk=cita.pk))
  cita.refresh_from_db()
  self.assertEqual(cita.estado,Cita.Estado.PROGRAMADA)
  self.user.user_permissions.add(Permission.objects.get(codename='change_cita'))
  self.user=User.objects.get(pk=self.user.pk)
  request.user=self.user
  completar(None,request,Cita.objects.filter(pk=cita.pk))
  cita.refresh_from_db()
  self.assertEqual(cita.estado,Cita.Estado.COMPLETADA)
