from datetime import date,timedelta
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from .models import Area,Empleado

class EmployeeTests(TestCase):
    def setUp(self):
        self.area=Area.objects.create(nombre='Sistemas')
        self.user=User.objects.create_user('emp')
    def create_employee(self,**kwargs):
        data=dict(dni='12345678',nombres='Luis',apellidos='Prueba',cargo='Analista',area=self.area,fecha_ingreso=date(2020,1,1),correo='luis@tecnoandes.pe',usuario=self.user)
        data.update(kwargs);return Empleado(**data)
    def test_empleado_valido(self):
        e=self.create_employee();e.full_clean();e.save();self.assertIn('años',e.antiguedad)
    def test_correo_restringido(self):
        with self.assertRaises(ValidationError): self.create_employee(correo='luis@example.com').full_clean()
    def test_fecha_no_futura(self):
        with self.assertRaises(ValidationError): self.create_employee(fecha_ingreso=date.today()+timedelta(days=1)).full_clean()
    def test_dni_unico(self):
        self.create_employee().save()
        other=User.objects.create_user('other')
        with self.assertRaises(Exception):
            self.create_employee(usuario=other).save()
