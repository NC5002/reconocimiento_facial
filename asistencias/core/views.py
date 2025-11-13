import face_recognition
import cv2
import numpy as np

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from .forms import RegistroForm
from .models import Usuario, Asistencia


# ==========================
# DASHBOARD
# ==========================
@login_required
def dashboard(request):
    return render(request, 'dashboard.html')


# ==========================
# REGISTRO DE USUARIO
# ==========================
def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST, request.FILES)
        if form.is_valid():

            usuario = form.save(commit=False)

            # Procesar la imagen
            imagen = face_recognition.load_image_file(request.FILES['foto'])
            encodings = face_recognition.face_encodings(imagen)

            if len(encodings) == 0:
                messages.error(request, "No se detectó ningún rostro en la imagen. Intente otra foto.")
                return render(request, 'registro.html', {'form': form})

            # Guardar encoding y contraseña
            usuario.encoding = encodings[0].tobytes()
            usuario.set_password(form.cleaned_data['password'])
            usuario.save()

            messages.success(request, "Usuario registrado correctamente. Ahora puedes iniciar sesión.")
            return redirect('login')

    else:
        form = RegistroForm()

    return render(request, 'registro.html', {'form': form})


# ==========================
# REGISTRO DE ASISTENCIA POR WEBCAM
# ==========================
@login_required
def registrar_asistencia(request):

    if request.method == 'POST':

        # Imagen enviada desde JavaScript
        frame = request.FILES['frame'].read()
        nparr = np.frombuffer(frame, np.uint8)
        imagen = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        encodings = face_recognition.face_encodings(imagen)

        # Si no detecta rostro
        if len(encodings) == 0:
            resultado = "rechazado"
        else:
            encoding_registrado = np.frombuffer(request.user.encoding, dtype=np.float64)
            match = face_recognition.compare_faces([encoding_registrado], encodings[0])

            resultado = "aceptado" if match[0] else "rechazado"

        # Guardar en tabla Asistencia
        Asistencia.objects.create(
            usuario=request.user,
            resultado=resultado
        )

        return JsonResponse({"resultado": resultado})

    return render(request, 'asistencia.html')
