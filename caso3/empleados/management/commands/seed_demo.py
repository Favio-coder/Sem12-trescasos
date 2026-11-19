from datetime import date,timedelta,time
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User,Group
from empleados.models import Area,Empleado
from asistencias.models import Asistencia
from permisos.models import Permiso
class Command(BaseCommand):
 help='Crea datos ficticios idempotentes para demostración (contraseña Demo2026!).'
 def handle(self,*args,**opts):
  groups={n:Group.objects.get_or_create(name=n)[0] for n in ['Administrador RRHH','Jefe de Área','Empleado','Contador']}
  admin,_=User.objects.get_or_create(username='rrhh',defaults={'email':'rrhh@tecnoandes.pe','first_name':'Rocío','last_name':'Recursos Humanos','is_staff':True})
  admin.is_staff=True;admin.set_password('Demo2026!');admin.save();admin.groups.add(groups['Administrador RRHH'])
  names=['Sistemas','Contabilidad','Ventas','Logística','Recursos Humanos']
  areas=[]
  for i,n in enumerate(names):
   jefe,_=User.objects.get_or_create(username=f'jefe{i+1}',defaults={'email':f'jefe{i+1}@tecnoandes.pe','first_name':'Jefe','last_name':n})
   jefe.set_password('Demo2026!');jefe.save();jefe.groups.add(groups['Jefe de Área'])
   a,_=Area.objects.get_or_create(nombre=n,defaults={'jefe':jefe});a.jefe=jefe;a.save();areas.append(a)
  counter,_=User.objects.get_or_create(username='contador',defaults={'email':'contador@tecnoandes.pe','first_name':'César','last_name':'Contador'});counter.set_password('Demo2026!');counter.save();counter.groups.add(groups['Contador'])
  for i in range(10):
   a=areas[i%len(areas)];username=f'empleado{i+1:02}'
   u,_=User.objects.get_or_create(username=username,defaults={'email':f'{username}@tecnoandes.pe','first_name':f'Persona{i+1}','last_name':f'Demo{i+1}'})
   u.set_password('Demo2026!');u.save();u.groups.add(groups['Empleado'])
   e,_=Empleado.objects.get_or_create(usuario=u,defaults={'dni':f'{70000000+i:08d}','nombres':u.first_name,'apellidos':u.last_name,'cargo':'Analista','area':a,'fecha_ingreso':date.today()-timedelta(days=400+i*50),'correo':u.email})
   for j in range(5):
    day=date.today()-timedelta(days=j+1)
    Asistencia.objects.get_or_create(empleado=e,fecha=day,defaults={'hora_entrada':time(9),'hora_salida':time(18,30) if j==0 else time(17,30)})
   if i<10:
    estado=['pendiente','aprobado','rechazado'][i%3]
    p,_=Permiso.objects.get_or_create(empleado=e,tipo='personal',fecha_inicio=date.today()+timedelta(days=10+i),defaults={'fecha_fin':date.today()+timedelta(days=10+i),'motivo':'Solicitud ficticia para atender asuntos personales y familiares.'+(' Adjunto documento sustentatorio.'),'estado':estado,'aprobador':admin if estado!='pendiente' else None})
  self.stdout.write(self.style.SUCCESS('Datos demo listos. Usuarios de ejemplo usan password Demo2026!.'))
