from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods


@require_http_methods(["GET"])
def home_view(request):
    return render(request, "home.html")


@require_http_methods(["POST"])
@csrf_protect
def login_view(request):
    username = request.POST.get("username", "").strip()
    password = request.POST.get("password", "")

    user = authenticate(request, username=username, password=password)
    if user is not None and user.is_active:
        login(request, user)
        return redirect("home")

    return render(
        request,
        "home.html",
        {"login_error": "Usuario o contraseña inválidos."},
        status=401,
    )


@require_http_methods(["POST"])
@csrf_protect
def logout_view(request):
    logout(request)
    return redirect("home")
