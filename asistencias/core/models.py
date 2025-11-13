from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    foto = models.ImageField(upload_to='rostros/')
    encoding = models.BinaryField(null=True, blank=True)


class Asistencia(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    fecha = models.DateField(auto_now_add=True)
    hora = models.TimeField(auto_now_add=True)
    resultado = models.CharField(max_length=20)  # aceptado / rechazado

    def __str__(self):
        return f"{self.usuario.username} - {self.fecha} {self.hora} ({self.resultado})"


