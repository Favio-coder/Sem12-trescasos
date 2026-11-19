from datetime import date, time, datetime
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from empleados.models import Area, Empleado
from .models import Asistencia
from .services import marcar_entrada, marcar_salida

class AttendanceTests(TestCase):
    def setUp(self):
        self.user=User.objects.create_user('ana',password='Demo12345')
        self.area=Area.objects.create(nombre='Sistemas')
        self.emp=Empleado.objects.create(dni='12345678',nombres='Ana',apellidos='Pérez',cargo='Analista',area=self.area,fecha_ingreso=date(2023,1,1),correo='ana@tecnoandes.pe',usuario=self.user)

    def test_calculo_horas_y_extras(self):
        item=Asistencia(empleado=self.emp,fecha=date.today(),hora_entrada=time(9),hora_salida=time(18,30))
        item.save()
        self.assertEqual(str(item.horas_trabajadas),'9.50')
        self.assertEqual(str(item.horas_extras),'1.50')

    def test_entrada_rechaza_duplicado(self):
        now=timezone.make_aware(datetime.combine(date.today(),time(10)))
        marcar_entrada(self.emp,now)
        with self.assertRaises(ValidationError): marcar_entrada(self.emp,now)

    def test_salida_sin_entrada(self):
        now=timezone.make_aware(datetime.combine(date.today(),time(10)))
        with self.assertRaises(ValidationError): marcar_salida(self.emp,now)

    def test_registro_entrada_y_salida(self):
        start=timezone.make_aware(datetime.combine(date.today(),time(9)))
        end=timezone.make_aware(datetime.combine(date.today(),time(18)))
        item=marcar_entrada(self.emp,start)
        item=marcar_salida(self.emp,end)
        self.assertEqual(item.horas_trabajadas,9)
