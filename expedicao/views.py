from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Dados_etiqueta, Dados_etiqueta_2
from jinja2 import Environment, FileSystemLoader
import pdfkit


@login_required()
def etiqueta(request):
    if request.method == 'POST':
        pedido = request.POST.get('pedido')
        tipo_ped = request.POST.get('tipo_ped')
        acao = request.POST.get('acao')
        if pedido != '': 
            return redirect('gerar_etiqueta',pedido=pedido,tipo_ped=tipo_ped)
        else:
            return redirect('etiqueta')
    else:
        return render(request, 'expedicao_etiqueta.html')
    


def gerar_etiqueta(request, idioma, tipo_ped, pedido):

    tipo_ped = tipo_ped.upper()
    idioma = idioma.upper()

    # Obtém os dados do pedido usando a função Dados_etiqueta
    dados = Dados_etiqueta(idioma,tipo_ped,pedido)
    # Obtém dados adicionais do pedido
    dados_2 = Dados_etiqueta_2(idioma,tipo_ped,pedido)

    # Verifica o idioma e define a variável 'idioma'
    if dados[0]['idioma'] == 'ESPANHOL':
        idioma = 'es'
    elif dados[0]['idioma'] == 'INGLES':
        idioma = 'en'
    else: idioma = 'pt'  # Define como PORTUGUES por padrão

    pedido = str(dados[0]['num_ped'])  # Obtém o número do pedido

    estilo_etiqueta_css = open('expedicao/static/css/estilo_etiqueta.css').read()
    dicionario_tradutor_js = open('expedicao/static/js/dicionario_tradutor.js').read()

    # Configura o carregador de templates para a pasta 'embalagem/templates/'
    file_loader = FileSystemLoader('expedicao/templates/') 
    env = Environment(loader=file_loader)  # Cria um ambiente Jinja2
    template = env.get_template('etiqueta.html')  # Obtém o template para cada dado

    html_content = template.render({
        'dados': dados,
        'dados_2': dados_2,
        'pedido': pedido,
        'tipo_ped': tipo_ped,
        'estilo_etiqueta_css': estilo_etiqueta_css,
        'dicionario_tradutor_js': dicionario_tradutor_js,
        'idioma': idioma
    })

    path_to_wkhtmltopdf = '../django/wkhtmltopdf.exe'  # Caminho para o executável do wkhtmltopdf
    config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)  # Configura o pdfkit com o executável

    # Define as opções para o PDF
    options = {
        'orientation': 'Landscape',  # Orientação do PDF
        'margin-top': '0mm',  # Margem superior
        'margin-bottom': '0mm',  # Margem inferior
        'margin-right': '0mm',  # Margem direita
        'margin-left': '0mm',  # Margem esquerda
    }
    
    # Gera o PDF a partir do conteúdo HTML
    pdf = pdfkit.from_string(html_content, False, configuration=config, options=options)

    # Cria a resposta HTTP com o conteúdo do PDF
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename=' + tipo_ped + '_' + pedido + '.pdf'  # Define o cabeçalho para visualização no navegador

    return response  # Retorna a resposta com o PDF