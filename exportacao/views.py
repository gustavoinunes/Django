from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Dados_exportacao
from jinja2 import Environment, FileSystemLoader
import pdfkit


@login_required()
def documento(request):
    if request.method == 'POST':
        tipo_doc = request.POST.get('documento')
        cod_processo = request.POST.get('processo')
        acao = request.POST.get('acao')
        if cod_processo != '': 
            return redirect('gerar',tipo_doc=tipo_doc,cod_processo=cod_processo)
        else:
            return redirect('documento')
    else:
        return render(request, 'exportacao_documento.html')
    
   
def visualizar(request,tipo_doc,cod_processo,acao):
    processo, itens, frete = Dados_exportacao(cod_processo)
    return render(request, template_name='exportacao_documento.html', context={'processo':processo, 'itens':itens, 'frete':frete, 'acao':acao})


def gerar_documento(request,tipo_doc,cod_processo):

    processo, itens, frete = Dados_exportacao(tipo_doc,cod_processo)

    file_loader = FileSystemLoader('exportacao/templates/') 
    env = Environment(loader=file_loader)
    template = env.get_template(tipo_doc+'.html')

    html_content = template.render({'processo':processo, 'itens':itens, 'frete':frete})
    full_html_content = html_content 

    path_to_wkhtmltopdf = '../django/wkhtmltopdf.exe'
    config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)

    options = {
        'margin-top': '0mm',
        'margin-bottom': '4mm',
        'margin-right': '0mm',
        'margin-left': '0mm',
        'print-media-type': '',
    }
    pdf = pdfkit.from_string(full_html_content, False, configuration=config, options=options)

    # response = HttpResponse(pdf, content_type='application/pdf')
    # response.headers['Content-Disposition'] = 'attachment; filename='+tipo_doc+'_'+cod_processo+'.pdf'
    # return response

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename='+tipo_doc+'_'+cod_processo+'.pdf'
    return response