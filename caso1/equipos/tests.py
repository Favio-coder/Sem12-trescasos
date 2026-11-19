from datetime import timedelta
from django.test import TestCase, Client
from django.contrib.auth.models import User,Group
from django.utils import timezone
from .models import Laboratorio,Categoria,Equipo,Prestamo,Auditoria
from .forms import PrestamoForm
class AppTests(TestCase):
 def setUp(self):
  self.lab=Laboratorio.objects.create(nombre='Lab',codigo='L1',ubicacion='Pabellón'); self.cat=Categoria.objects.create(nombre='PC'); self.e=Equipo.objects.create(codigo_patrimonial='EQ1',nombre='PC',categoria=self.cat,laboratorio=self.lab,stock_total=2); self.u=User.objects.create_user('docente',password='Pass-12345'); self.grp=Group.objects.create(name='Docente'); self.u.groups.add(self.grp)
 def test_codigo_unico(self):
  from django.db import IntegrityError,transaction
  with self.assertRaises(IntegrityError):
   with transaction.atomic(): Equipo.objects.create(codigo_patrimonial='EQ1',nombre='otro',categoria=self.cat,laboratorio=self.lab)
 def test_form_fecha_y_stock(self):
  data={'equipo':self.e.pk,'cantidad':1,'fecha_prestamo':timezone.localdate(),'fecha_prevista_devolucion':timezone.localdate(),'observaciones':''}; f=PrestamoForm(data,usuario=self.u); self.assertFalse(f.is_valid()); self.assertIn('fecha_prevista_devolucion',f.errors)
 def test_equipo_mantenimiento(self):
  self.e.estado='mantenimiento'; self.e.save(); d={'equipo':self.e.pk,'cantidad':1,'fecha_prestamo':timezone.localdate(),'fecha_prevista_devolucion':timezone.localdate()+timedelta(days=1)}; self.assertFalse(PrestamoForm(d,usuario=self.u).is_valid())
 def test_limite_prestamos(self):
  for i in range(3): Prestamo.objects.create(docente=self.u,equipo=self.e,cantidad=1,fecha_prevista_devolucion=timezone.localdate()+timedelta(days=2),estado='activo')
  d={'equipo':self.e.pk,'cantidad':1,'fecha_prestamo':timezone.localdate(),'fecha_prevista_devolucion':timezone.localdate()+timedelta(days=1)}; self.assertFalse(PrestamoForm(d,usuario=self.u).is_valid())
 def test_catalogo_publico_y_solicitud_protegida(self):
  c=Client(); self.assertEqual(c.get('/').status_code,200); self.assertEqual(c.get('/prestamos/nuevo/').status_code,302)
 def test_middleware_alerta_docente(self):
  Prestamo.objects.create(docente=self.u,equipo=self.e,cantidad=1,fecha_prevista_devolucion=timezone.localdate()-timedelta(days=1),estado='vencido'); c=Client(); c.force_login(self.u); r=c.get('/dashboard/'); self.assertEqual(r.status_code,200); self.assertContains(r,'Vencido')
 def test_solicitud_auditoria(self):
  c=Client(); c.force_login(self.u); c.post('/prestamos/nuevo/',{}); self.assertTrue(Auditoria.objects.filter(usuario=self.u).exists())
