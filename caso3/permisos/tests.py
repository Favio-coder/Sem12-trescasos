from datetime import date,timedelta
from django.contrib.auth.models import User,Group
from django.core.exceptions import ValidationError
from django.test import TestCase
from empleados.models import Area,Empleado
from .models import Permiso

class PermisoTests(TestCase):
    def setUp(self):
        self.jefe=User.objects.create_user('jefe',password='Demo12345')
        self.jefe.groups.add(Group.objects.create(name='Jefe de Área'))
        self.area=Area.objects.create(nombre='Sistemas',jefe=self.jefe)
        self.user=User.objects.create_user('emp',password='Demo12345')
        self.emp=Empleado.objects.create(dni='12345678',nombres='Eva',apellidos='Demo',cargo='Analista',area=self.area,fecha_ingreso=date(2022,1,1),correo='eva@tecnoandes.pe',usuario=self.user)
    def make_request(self,**kwargs):
        data=dict(empleado=self.emp,tipo='personal',fecha_inicio=date.today()+timedelta(days=5),fecha_fin=date.today()+timedelta(days=5),motivo='Necesito realizar una diligencia familiar previamente programada.')
        data.update(kwargs);return Permiso(**data)
    def test_motivo_minimo_y_rango(self):
        p=self.make_request(motivo='corto')
        with self.assertRaises(ValidationError): p.full_clean()
        p=self.make_request(fecha_fin=date.today()-timedelta(days=1))
        with self.assertRaises(ValidationError): p.full_clean()
    def test_aprobacion_jefe_area(self):
        p=self.make_request();p.full_clean();p.save()
        p.resolver(self.jefe,'aprobado')
        p.refresh_from_db()
        self.assertEqual(p.estado,'aprobado')
    def test_jefe_otra_area_no_aprueba(self):
        other=User.objects.create_user('otro');other.groups.add(self.jefe.groups.first())
        p=self.make_request();p.full_clean();p.save()
        with self.assertRaises(ValidationError): p.resolver(other,'aprobado')
    def test_superposicion_bloqueada(self):
        p=self.make_request();p.full_clean();p.save()
        p2=self.make_request()
        with self.assertRaises(ValidationError): p2.full_clean()
