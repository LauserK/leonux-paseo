from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib.auth import authenticate, login, logout
from usuarios.models import User, TipoUsuario
from django.db import connection, connections

class LoginView(View):
    def get(self, request):
        ctx = {}
        template   = "login.html"
        return render(request, template, ctx)

    def post(self, request):
        mensaje       = ""

        usuario       = request.POST.get("usuario")
        contrasena    = request.POST.get("clave")

        if not usuario and not contrasena:
            mensaje = "No se deben dejar campos vacios"
        else:
            user = authenticate(username=usuario, password=contrasena)
            if user is not None:
                login(request, user)
                return redirect('/')
            else:
                # registrar con datos de leonux
                with connections['leonux'].cursor() as cursor:
                    cursor.execute("SELECT nombre, codigo, clave, auto_grupo FROM usuarios WHERE codigo = %s AND clave = %s", [usuario, contrasena])
                    usuario_leonux     = cursor.fetchone()
                    cursor.close()

                    if usuario_leonux is not None:
                        # Crear usuario
                        new_user            = User.objects.create_user(usuario_leonux[1], 'it@grupopaseo.com', usuario_leonux[2])
                        new_user.first_name = usuario_leonux[0]
                        tipo_usuario = TipoUsuario.objects.get(codigo=usuario_leonux[3])
                        new_user.tipo_usuario = tipo_usuario
                        new_user.save()

                        login(request, new_user)
                        return redirect('/')

        ctx = {
            "mensaje": mensaje
        }
        template   = "login.html"
        return render(request, template, ctx)
