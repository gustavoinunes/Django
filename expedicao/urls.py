from django.contrib.auth.decorators import login_required
from django.urls import path
from . import views


urlpatterns = [
    path('etiqueta/',views.etiqueta, name="etiqueta"),
    path('etiqueta/<str:idioma>/<str:tipo_ped>/<str:pedido>', views.gerar_etiqueta, name="gerar_etiqueta"),
    path('etiqueta/<str:tipo_ped>/<str:pedido>', views.gerar_etiqueta, {'idioma': ''}, name="gerar_etiqueta"),
]