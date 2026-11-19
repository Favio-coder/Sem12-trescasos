from datetime import date,time,timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User,Group
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from medicos.models import Especialidad,Medico,HorarioMedico
from pacientes.models import Paciente
from citas.models import Cita,ConsultaMedica
class Command(BaseCommand):
 help='Genera datos ficticios idempotentes para demostración.'
 def handle(self,*args,**kwargs):
  for name in ['Admins','Médicos','Recepcionistas','Pacientes']: Group.objects.get_or_create(name=name)
  permissions = {
   'Médicos': [('pacientes','paciente','ver_historial_clinico'),('citas','cita','view_cita'),('citas','cita','change_cita'),('citas','consultamedica','add_consultamedica'),('citas','notaconsulta','add_notaconsulta')],
   'Recepcionistas': [('pacientes','paciente','add_paciente'),('pacientes','paciente','view_paciente'),('citas','cita','add_cita'),('citas','cita','view_cita'),('citas','cita','change_cita'),('pacientes','paciente','agendar_cita'),('pacientes','paciente','cancelar_cita')],
   'Pacientes': [('pacientes','paciente','agendar_cita'),('pacientes','paciente','cancelar_cita'),('pacientes','paciente','ver_historial_clinico')],
  }
  for group_name, entries in permissions.items():
   group=Group.objects.get(name=group_name)
   for app,model,codename in entries:
    perm=Permission.objects.filter(content_type__app_label=app,content_type__model=model,codename=codename).first()
    if perm: group.permissions.add(perm)
  admin,_=User.objects.get_or_create(username='admin_demo',defaults={'email':'admin@demo.test','is_staff':True,'is_superuser':True}); admin.set_password('DemoAdmin2026!'); admin.is_staff=True; admin.is_superuser=True; admin.save(); admin.groups.add(Group.objects.get(name='Admins'))
  rec,_=User.objects.get_or_create(username='recepcion_demo'); rec.set_password('DemoRecep2026!'); rec.save(); rec.groups.add(Group.objects.get(name='Recepcionistas'))
  specs=[Especialidad.objects.get_or_create(nombre=n)[0] for n in ['Medicina General','Pediatría','Cardiología','Dermatología']]
  dias=[0,1,2,3,4,5]
  medicos=[]
  for i in range(8):
   u,_=User.objects.get_or_create(username=f'medico{i+1}_demo'); u.set_password('DemoMed2026!'); u.save(); u.groups.add(Group.objects.get(name='Médicos'))
   m,_=Medico.objects.get_or_create(cmp=f'{10000+i}',defaults={'nombres':f'Médico{i+1}','apellidos':'Demostración','especialidad':specs[i%4],'consultorio':f'C-{i+1}','usuario':u}); medicos.append(m)
   for day in dias: HorarioMedico.objects.get_or_create(medico=m,dia_semana=day,hora_inicio=time(8),defaults={'hora_fin':time(13) if day==5 else time(18),'consultorio':m.consultorio})
  patients=[]
  for i in range(15):
   u,_=User.objects.get_or_create(username=f'paciente{i+1}_demo'); u.set_password('DemoPac2026!'); u.save(); u.groups.add(Group.objects.get(name='Pacientes'))
   p,_=Paciente.objects.get_or_create(dni=f'{20000000+i:08d}',defaults={'nombres':f'Paciente{i+1}','apellidos':'Ficticio','fecha_nacimiento':date(1998,1,1),'tipo':'estudiante','email':f'p{i+1}@uncp.edu.pe','usuario':u}); patients.append(p)
  start=date.today()+timedelta(days=1)
  for i in range(30):
   day=start+timedelta(days=(i//5)*7); day+=timedelta(days=(7-day.weekday())%6)
   hour=time(8+(i%5)*2)
   state=['programada','completada','cancelada'][i%3]
   cita,_=Cita.objects.get_or_create(paciente=patients[i%15],medico=medicos[i%8],fecha=day,hora=hour,defaults={'especialidad':medicos[i%8].especialidad,'motivo':'Consulta de demostración para pruebas del sistema','estado':state,'registrada_por':admin})
   if cita.estado=='completada': ConsultaMedica.objects.get_or_create(cita=cita,defaults={'paciente':cita.paciente,'medico':cita.medico,'diagnostico':'Diagnóstico ficticio de demostración','tratamiento':'Seguimiento académico simulado','observaciones':'Datos ficticios.'})
  self.stdout.write(self.style.SUCCESS('Datos ficticios demo cargados. admin_demo / DemoAdmin2026!; medico1_demo / DemoMed2026!; paciente1_demo / DemoPac2026!'))
