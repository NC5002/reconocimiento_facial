import face_recognition
import cv2
import numpy as np

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from .forms import RegistroForm
from .models import Usuario, Asistencia

from django.contrib.auth import authenticate, login

# ==========================
# HOME
def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    else:
        return redirect('login')

# =========================

# LANDING PAGE
def landing(request):
    return render(request, 'landing.html')

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

        form = RegistroForm(request.POST)
        frame = request.FILES.get('frame', None)
        print("DEBUG FRAME:", frame)


        if frame is None:
            messages.error(request, "Debes capturar tu rostro antes de registrarte.")
            return render(request, 'registro.html', {'form': form})

        print("ERRORES DE FORMULARIO:", form.errors)

        if form.is_valid():

            usuario = form.save(commit=False)
            usuario.set_password(form.cleaned_data['password'])

            # Convertir la imagen capturada a un array
            file_bytes = np.frombuffer(frame.read(), np.uint8)
            imagen = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

            encodings = face_recognition.face_encodings(imagen)

            if len(encodings) == 0:
                messages.error(request, "No se detectó ningún rostro. Intenta nuevamente.")
                return render(request, 'registro.html', {'form': form})

            # Guardar encoding facial
            usuario.encoding = encodings[0].tobytes()
            usuario.save()

            messages.success(request, "Registro completado correctamente. Ahora puedes iniciar sesión.")

            # 👇 ESTA ES LA REDIRECCIÓN FINAL
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
