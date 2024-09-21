import requests
import base64
from datetime import datetime
import locale
import cx_Oracle
import base64
from io import BytesIO
from PIL import Image
import numpy as np
import cv2

token = 'CfDJ8PhfB8i7Kx1KkLkxk_yYZ7OuHQUNRC9s73wJYl6zG55YmwVbrofRPOt9eoGt8oofhrAydXyuKi6-OYwk0TtKEk0-ZNmvjbqrACrwn91pkOVM0E0B56DY0BN2w6ww0tLfyoaEyV0J-0__dHgUcyL5cU7PsFUjLELQ992frNIwEoYHy0nl504Z0nhEqT032KFFKGJamfuG0KdhWo3Kx16XGn4-fuMz1rkr4CiL2ehx7aU5DqypnASY8KGf2y8XtHUhYBjZh7aVU_t377-5UBBqP8BQlTFYwgw8MCqNbRSGpuW9PjplPw6fk9yOvG97Kqd6KkGwzf8BjVSgp1u80vHf2gsHeTVR5EGwjfUxgtXuIbbstzd-6bqvpSu-gMgzoy7c3W1kjGjcKUucgJQZcSG3yhyGml60fTJDteEQBWnmJY4IaeBFQkoJ_nPHN-AU49cFt5LhPc1_22EWtn954aZFatIlpwDWdja4lSDj0fdUOD0B6fC5DCXi0nK95-W39i-vkCZ-Xj3X_FujR4tIXLFAECc'

def API_exportacao(cod_processo):
    url = 'https://sistema.meucentury.com/PROWeb/FoccoIntegrador/api/v1/Exportacao/py_processo_export?Chave=5459905092&COD_PROCESSO='+cod_processo
    dados = requests.get(url, headers={'Authorization':'Bearer ' + token})
    dados = dados.json()
    dados = dados['value']
    return dados

def API_exportacao_itens(cod_processo):
    url = 'https://sistema.meucentury.com/PROWeb/FoccoIntegrador/api/v1/Exportacao/py_ite_proc_export?Chave=5459905092&COD_PROCESSO='+cod_processo
    dados = requests.get(url, headers={'Authorization':'Bearer ' + token})
    dados = dados.json()    
    dados = dados['value']
    return dados

def API_exportacao_frete(cod_processo):
    url = 'https://sistema.meucentury.com/PROWeb/FoccoIntegrador/api/v1/Exportacao/py_frete_proc_export?Chave=5459905092&COD_PROCESSO='+cod_processo
    dados = requests.get(url, headers={'Authorization':'Bearer ' + token})
    dados = dados.json()    
    dados = dados['value']
    return dados


def exportacao_itens(tipo_doc,cod_processo):
    # Definir a string de conexão
    # oracledb.init_oracle_client(lib_dir='C:\oracle\instantclient_23_5')
    dsn_tns = cx_Oracle.makedsn('10.1.57.181', '1521', service_name='f3ipro')
    connection = cx_Oracle.connect(user='otimiza', password='otimiza#century', dsn=dsn_tns)

    try:
        # Iniciar uma transação
        cursor = connection.cursor()

        cursor.execute('CALL OTIMIZA.SH_EXPORTACAO_PR(V_SESSAO => 0,V_PROCESSO => :cod_processo)', {'cod_processo': cod_processo})

        # Definir uma consulta SQL
        if tipo_doc=='packing':
            query = 'SELECT * FROM SH_EXPORTACAO_WK WHERE COD_PROCESSO = :cod_processo ORDER BY SEQ'
        else:
            query = 'SELECT * FROM SH_EXPORTACAO_WK WHERE ID_ITEM_PROCESSO IS NOT NULL AND COD_PROCESSO = :cod_processo ORDER BY SEQ'

        # Executar a consulta
        cursor.execute(query, {'cod_processo': cod_processo})

        # Recuperar os resultados
        columns = [col[0] for col in cursor.description]  # Obter nomes das colunas
        rows = cursor.fetchall()

        # Converter resultados em uma lista de dicionários
        dados = []
        for row in rows:
            item = {}
            for col_name, value in zip(columns, row):
                # Verificar o tipo de dado baseado na descrição do cursor
                col_index = columns.index(col_name)
                col_type = cursor.description[col_index][1]  # Índice 1 para tipo de dado

                if col_type == cx_Oracle.BLOB:
                    if value is not None:
                        # Converter BLOB para Base64
                        blob_data = value.read()
                        base64_data = base64.b64encode(blob_data).decode('utf-8')
                        item[col_name] = base64_data
                    else:
                        item[col_name] = None
                else:
                    item[col_name] = value
            dados.append(item)

        # Retornar os resultados
        return dados

    finally:
        # Fechar o cursor e a conexão
        cursor.close()
        connection.close()


def Dados_exportacao(tipo_doc,cod_processo):
    processo_lista = API_exportacao (cod_processo)
    frete_lista = API_exportacao_frete(cod_processo)
    itens_lista = exportacao_itens(tipo_doc,cod_processo)
    
    processo_lista[0]['data'] = format_date()
    processo_lista[0]['logo'] = remove_background_from_base64("exportacao/static/img/logo.png")
    processo_lista[0]['letreiro'] = remove_background_from_base64("exportacao/static/img/letreiro.png")
    processo_lista[0]['marcas'] = remove_background_from_base64("exportacao/static/img/marcas.png")
    processo_lista[0]['soma_qtde'] = 0
    processo_lista[0]['soma_volume'] = 0
    processo_lista[0]['soma_frete'] = 0
    processo_lista[0]['soma_valor'] = 0
    processo_lista[0]['soma_total'] = 0
    processo_lista[0]['soma_peso_brt'] = 0
    processo_lista[0]['soma_peso_liq'] = 0
    processo_lista[0]['soma_cubagem'] = 0
    
    itens = []
    frete = []
    produto = ''
    id_masc = ''
    cor_back = '255,255,255'
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')  #'en_US.UTF-8' or 'pt_BR.UTF-8'

    k = 0;
    for k in range(len(frete_lista)):
        if frete_lista[k]['operacao'] == '+':
            processo_lista[0]['soma_frete']  = processo_lista[0]['soma_frete'] + frete_lista[k]['valor']
        else:
            processo_lista[0]['soma_frete']  = processo_lista[0]['soma_frete'] - frete_lista[k]['valor']
        frete_lista[k]['valor'] = locale.format_string('%.2f', frete_lista[k]['valor'], grouping=True)
        frete.append(frete_lista[k])

    k = 0;
    for k in range(len(itens_lista)):

        processo_lista[0]['soma_qtde'] = int(processo_lista[0]['soma_qtde'] + itens_lista[k]['QTDE'])
        processo_lista[0]['soma_volume'] = int(processo_lista[0]['soma_volume'] + itens_lista[k]['VOLUME'])
        processo_lista[0]['soma_valor'] = processo_lista[0]['soma_valor'] + itens_lista[k]['VLR_TOTAL']

        processo_lista[0]['soma_peso_brt'] = processo_lista[0]['soma_peso_brt'] + itens_lista[k]['PESO_BRT_TOT']
        processo_lista[0]['soma_peso_liq'] = processo_lista[0]['soma_peso_liq'] + itens_lista[k]['PESO_LIQ_TOT']
        processo_lista[0]['soma_cubagem'] = processo_lista[0]['soma_cubagem'] + itens_lista[k]['CUBAGEM_TOT']

        itens_lista[k]['VLR_LIQ'] = locale.format_string('%.2f', itens_lista[k]['VLR_LIQ'], grouping=True)
        itens_lista[k]['VLR_TOTAL'] = locale.format_string('%.2f', itens_lista[k]['VLR_TOTAL'], grouping=True)
        itens_lista[k]['PESO_LIQ'] = locale.format_string('%.3f', itens_lista[k]['PESO_LIQ'], grouping=True)
        itens_lista[k]['PESO_BRT'] = locale.format_string('%.3f', itens_lista[k]['PESO_BRT'], grouping=True)
        itens_lista[k]['CUBAGEM'] = locale.format_string('%.3f', itens_lista[k]['CUBAGEM'], grouping=True)
        itens_lista[k]['PESO_LIQ_TOT'] = locale.format_string('%.3f', itens_lista[k]['PESO_LIQ_TOT'], grouping=True)
        itens_lista[k]['PESO_BRT_TOT'] = locale.format_string('%.3f', itens_lista[k]['PESO_BRT_TOT'], grouping=True)
        itens_lista[k]['CUBAGEM_TOT'] = locale.format_string('%.3f', itens_lista[k]['CUBAGEM_TOT'], grouping=True)

        if itens_lista[k]['ITEM'] == produto:
            itens_lista[k]['CONT_IMG_INV'] = 0
            itens_lista[k]['CONT_IMG_PACK'] = 0
            itens_lista[k]['PRODUTO_IMAGEM'] = ''
            itens_lista[k]['CONFORTO'] = ''
            if 'CAIXA' in itens_lista[k]['DESC_ITEM']  or 'CAPA' in itens_lista[k]['DESC_ITEM']:
                itens_lista[k-1]['CONT_CROQUI'] = 2
                itens_lista[k-1]['CONT_PACK'] = 2
            if itens_lista[k]['ID_MASC']  == id_masc:
                itens_lista[k - cont]['CONT_CROQUI'] = cont+1
                itens_lista[k]['CONT_CROQUI'] = 0
                cont += 1
            else : cont = 1
        produto = itens_lista[k]['ITEM']
        id_masc = itens_lista[k]['ID_MASC']

        if itens_lista[k]['CONT_CROQUI'] == 0:
            itens_lista[k]['COR_BACK'] = cor_back
        elif cor_back == '255,255,255':
            cor_back = '235,235,235'
            itens_lista[k]['COR_BACK'] = cor_back
        else:
            cor_back = '255,255,255'
            itens_lista[k]['COR_BACK'] = cor_back
        

        try:
            conforto_imagem = open('exportacao/static/img/conforto/'+itens_lista[k]['CONFORTO']+'.png', "rb")
            itens_lista[k]['CONFORTO_IMAGEM'] = base64.b64encode(conforto_imagem.read()).decode('utf-8')
            v_conforto_imagem = open('exportacao/static/img/conforto/v_'+itens_lista[k]['CONFORTO']+'.png', "rb")
            itens_lista[k]['V_CONFORTO_IMAGEM'] = base64.b64encode(v_conforto_imagem.read()).decode('utf-8')
        except: None

        try:
            croqui = 'exportacao/static/img/croqui/'+itens_lista[k]['MODULACAO']+'.png'
            if itens_lista[k]['LADO'] == 'DIREITO':
                croqui = remove_background_from_base64(croqui)
                croqui_invertido = invert_image_x(croqui)
                itens_lista[k]['MODULACAO_IMAGEM'] = remove_background_from_base64(croqui_invertido)
            else:
                itens_lista[k]['MODULACAO_IMAGEM'] = remove_background_from_base64(croqui)
        
        except: None
        itens_lista[k]['QTDE'] = int(itens_lista[k]['QTDE'])
        itens.append(itens_lista[k])
        
    processo_lista[0]['soma_total'] = processo_lista[0]['soma_valor'] + processo_lista[0]['soma_frete']
    processo_lista[0]['soma_total'] = locale.format_string('%.2f', round(processo_lista[0]['soma_total'],2), grouping=True)
    processo_lista[0]['soma_valor'] = locale.format_string('%.2f', round(processo_lista[0]['soma_valor'],2), grouping=True)
    processo_lista[0]['soma_frete'] = locale.format_string('%.2f', round(processo_lista[0]['soma_frete'],2), grouping=True)
    processo_lista[0]['soma_peso_brt'] = locale.format_string('%.2f', round(processo_lista[0]['soma_peso_brt'],2), grouping=True)
    processo_lista[0]['soma_peso_liq'] = locale.format_string('%.2f', round(processo_lista[0]['soma_peso_liq'],2), grouping=True)
    processo_lista[0]['soma_cubagem'] = locale.format_string('%.2f', round(processo_lista[0]['soma_cubagem'],2), grouping=True)
    processo = processo_lista[0]

    return processo, itens, frete


def image_to_base64(image):
    """Converte uma imagem PIL para uma string base64."""
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode('utf-8')


def remove_background_from_base64(imagem):

    try:
        try:
            image_file = open(imagem, "rb")
            imagem = base64.b64encode(image_file.read()).decode('utf-8')
        except: None

        # Decodificar a imagem base64
        image_data = base64.b64decode(imagem)
        
        # Abrir a imagem usando PIL
        img = Image.open(BytesIO(image_data)).convert("RGBA")
        
        # Converter a imagem para um array numpy para processamento com OpenCV
        np_img = np.array(img)
        
        # Converter a imagem para o formato BGR que o OpenCV usa
        bgr_img = cv2.cvtColor(np_img, cv2.COLOR_RGBA2BGRA)

        # Aplicar filtro de desfoque para suavizar a imagem
        blurred_img = cv2.GaussianBlur(bgr_img, (5, 5), 0)
        
        # Convertendo para o formato de imagem em escala de cinza
        gray_img = cv2.cvtColor(blurred_img, cv2.COLOR_BGRA2GRAY)
        
        # Aplicar um limiar para criar uma máscara binária
        _, mask = cv2.threshold(gray_img, 240, 255, cv2.THRESH_BINARY)
        
        # Inverter a máscara
        mask_inv = cv2.bitwise_not(mask)
        
        # Aplicar a máscara invertida para remover o fundo
        img_no_bg = cv2.bitwise_and(bgr_img, bgr_img, mask=mask_inv)
        
        # Converter a imagem de volta para formato RGBA
        img_no_bg = cv2.cvtColor(img_no_bg, cv2.COLOR_BGRA2RGBA)
        
        # Criar uma imagem PIL a partir do array numpy
        img_no_bg_pil = Image.fromarray(img_no_bg)
        
        # Salvar a imagem resultante em um buffer
        buffer = BytesIO()
        img_no_bg_pil.save(buffer, format="PNG")
        
        # Converter o buffer para base64
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

        return img_base64
    
    except Exception as e:
        return ''
    

def base64_to_image(base64_image):
    """Converte uma string de imagem em base64 para um objeto de imagem PIL."""
    try:
        # Decodifica a string base64
        image_data = base64.b64decode(base64_image)
        
        # Abre a imagem usando Pillow
        image = Image.open(BytesIO(image_data))
        
        return image
    
    except Exception as e:
        return None


def invert_image_x(base64_image):
    """Inverte uma imagem base64 no eixo X e retorna a nova imagem em base64."""
    try:
        # Converter base64 para imagem PIL
        img = base64_to_image(base64_image)
        if img is None:
            return ''
        
        # Inverter a imagem horizontalmente
        img_inverted = img.transpose(Image.FLIP_LEFT_RIGHT)
        
        # Converter a imagem resultante para base64
        return image_to_base64(img_inverted)
    
    except Exception as e:
        print(f"Error in invert_image_x: {e}")
        return ''


def get_ordinal_suffix(day):
    """Retorna o sufixo ordinal para um dia."""
    if 4 <= day <= 20 or 24 <= day <= 30:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
    return suffix


def format_date():
    """Retorna a data atual no formato 'January 1st, 2021'."""
    locale.setlocale(locale.LC_TIME, 'en_US.UTF-8') #'en_US.UTF-8' or 'pt_BR.UTF-8'
    now = datetime.now()
    month_name = now.strftime('%B')
    day = now.day
    year = now.year
    ordinal_suffix = get_ordinal_suffix(day)
    
    formatted_date = f"{month_name} {day}{ordinal_suffix}, {year}"
    return formatted_date