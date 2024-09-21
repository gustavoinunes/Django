from django.contrib.auth.decorators import login_required
from django.urls import path
from . import views


urlpatterns = [
    path('documento/',views.documento, name="documento"),
    path('documento/<str:tipo_doc>/<str:cod_processo>', views.gerar_documento, name="gerar"),
]