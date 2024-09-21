from django.contrib.auth.decorators import login_required
from django.urls import path
from . import views


urlpatterns = [
    path('tab_preco_venda/', views.tab_preco_venda, name='tab_preco_venda'),
    path('exporta_excel/<str:cod_produto>', login_required(views.exporta_excel.as_view()), name="exporta_excel"),
]