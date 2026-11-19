from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User,Group
from django.utils import timezone
from equipos.models import Laboratorio,Categoria,Equipo,Prestamo
class Command(BaseCommand):
    help='Carga datos de demostración idempotentes (password inicial: Demo-UNCP-2026).'
    def handle(self,*args,**opts):
        roles={n:Group.objects.get_or_create(name=n)[0] for n in ('Administrador','Docente','Asistente','Invitado')}
        users=[]
        for username,role in [('admin.uncp','Administrador'),('docente1.uncp','Docente'),('docente2.uncp','Docente'),('asistente.uncp','Asistente'),('invitado.uncp','Invitado')]:
            u,_=User.objects.get_or_create(username=username,defaults={'email':f'{username}@uncp.edu.pe','first_name':username.split('.')[0].title()}); u.set_password('Demo-UNCP-2026'); u.save(); u.groups.add(roles[role]); users.append(u)
        labs=[]
        for i in range(1,6): labs.append(Laboratorio.objects.get_or_create(codigo=f'LAB-{i:02}',defaults={'nombre':f'Laboratorio {i}','ubicacion':f'Pabellón {i}'} )[0])
        cats=[Categoria.objects.get_or_create(nombre=x)[0] for x in ('Computación','Redes','Electrónica')]
        equipos=[]
        for i in range(1,11): equipos.append(Equipo.objects.get_or_create(codigo_patrimonial=f'UNCP-EQ-{i:03}',defaults={'nombre':f'Equipo de laboratorio {i}','marca':'Genérica','modelo':f'M-{i}','categoria':cats[i%3],'laboratorio':labs[i%5],'stock_total':5,'estado':'mantenimiento' if i==10 else 'operativo'})[0])
        today=timezone.localdate()
        for i in range(15):
            Prestamo.objects.get_or_create(docente=users[1+i%2],equipo=equipos[i%9],fecha_prestamo=today-timedelta(days=i+1),defaults={'cantidad':1,'fecha_prevista_devolucion':today+timedelta(days=10) if i%3 else today-timedelta(days=1),'fecha_real_devolucion':today-timedelta(days=2) if i%4==0 else None,'estado':'devuelto' if i%4==0 else ('vencido' if i%3==0 else ('activo' if i%3==1 else 'solicitado')),'observaciones':'Registro de demostración'})
        self.stdout.write(self.style.SUCCESS('Datos demo listos. Usuarios demo usan la clave documentada.'))
