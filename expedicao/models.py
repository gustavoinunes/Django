import requests
import base64
import cx_Oracle
import base64
from io import BytesIO
from PIL import Image

#Criado no programa "Cadastro de Tokens de Acesso" no sistema FOCCO com nome de PYTHON_DJANGO
token = 'CfDJ8PhfB8i7Kx1KkLkxk_yYZ7OuHQUNRC9s73wJYl6zG55YmwVbrofRPOt9eoGt8oofhrAydXyuKi6-OYwk0TtKEk0-ZNmvjbqrACrwn91pkOVM0E0B56DY0BN2w6ww0tLfyoaEyV0J-0__dHgUcyL5cU7PsFUjLELQ992frNIwEoYHy0nl504Z0nhEqT032KFFKGJamfuG0KdhWo3Kx16XGn4-fuMz1rkr4CiL2ehx7aU5DqypnASY8KGf2y8XtHUhYBjZh7aVU_t377-5UBBqP8BQlTFYwgw8MCqNbRSGpuW9PjplPw6fk9yOvG97Kqd6KkGwzf8BjVSgp1u80vHf2gsHeTVR5EGwjfUxgtXuIbbstzd-6bqvpSu-gMgzoy7c3W1kjGjcKUucgJQZcSG3yhyGml60fTJDteEQBWnmJY4IaeBFQkoJ_nPHN-AU49cFt5LhPc1_22EWtn954aZFatIlpwDWdja4lSDj0fdUOD0B6fC5DCXi0nK95-W39i-vkCZ-Xj3X_FujR4tIXLFAECc'


def API_etiqueta(pedido):
    # Define a URL para a API com a chave e o número do pedido
    url = 'https://sistema.meucentury.com/PROWeb/FoccoIntegrador/api/v1/Exportacao/py_etiqueta?Chave=5459905092&NUM_PED=' + pedido
    # Faz uma requisição GET à URL e inclui o token de autorização no cabeçalho
    dados = requests.get(url, headers={'Authorization': 'Bearer ' + token})
    # Converte a resposta em formato JSON
    dados = dados.json()
    # Extrai os dados relevantes do JSON
    dados = dados['value']
    return dados  # Retorna os dados extraídos


def API_etiqueta_2(pedido):
    # Define a URL para a segunda API com a chave e o número do pedido
    url = 'https://sistema.meucentury.com/PROWeb/FoccoIntegrador/api/v1/Exportacao/py_etiqueta_2?Chave=5459905092&NUM_PED=' + pedido
    # Faz uma requisição GET à URL e inclui o token de autorização no cabeçalho
    dados = requests.get(url, headers={'Authorization': 'Bearer ' + token})
    # Converte a resposta em formato JSON
    dados = dados.json()
    # Extrai os dados relevantes do JSON
    dados = dados['value']
    return dados  # Retorna os dados extraídos


def Query(sql,params):
    # Definir a string de conexão
    dsn_tns = cx_Oracle.makedsn('10.1.57.181', '1521', service_name='f3ipro')
    connection = cx_Oracle.connect(user='otimiza', password='otimiza#century', dsn=dsn_tns)

    try:
        # Iniciar uma transação
        cursor = connection.cursor()

        # Definir uma consulta SQL
        # query = open('expedicao/static/sql/etiqueta.sql').read()
        
        # Executar a consulta
        cursor.execute(sql, params)

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


def Dados_etiqueta(idioma,tipo_ped,pedido):

    # Definir uma consulta SQL
    sql = open('expedicao/static/sql/etiqueta.sql').read()

    # Executar a consulta
    params =  {'idioma': idioma, 'pedido': pedido,'tipo_ped': tipo_ped}

    # Chama a função API_etiqueta para obter os dados do pedido
    dados_lista = Query(sql,params)
    
    dados = []  # Lista para armazenar os dados processados

    for k in range(len(dados_lista)):

        # Define as cores com base na marca do item
        if dados_lista[k]['marca'] == 'CENTURY':
            dados_lista[k]['cor_1'] = '#04223c'
            dados_lista[k]['cor_2'] = '#E0E6E9'

        elif dados_lista[k]['marca'] == 'PONTOVIRGULA':
            dados_lista[k]['cor_1'] = '#000000'
            dados_lista[k]['cor_2'] = '#dedede'

        elif dados_lista[k]['marca'] == 'BRETON':
            dados_lista[k]['cor_1'] = '#860038'
            dados_lista[k]['cor_2'] = '#e8e8e8'
        else:
            dados_lista[k]['cor_1'] = '#40473e'
            dados_lista[k]['cor_2'] = '#dcdddb'

        # Tenta abrir a imagem da marca correspondente
        try:
            marca_imagem = open('expedicao/static/img/marca/' + dados_lista[k]['marca'] + '.png', "rb")
            dados_lista[k]['marca_imagem'] = base64.b64encode(marca_imagem.read()).decode('utf-8')
        except:
            # Se não encontrar, usa uma imagem padrão
            marca_imagem = open('expedicao/static/img/marca/sohome.png', "rb")
            dados_lista[k]['marca_imagem'] = base64.b64encode(marca_imagem.read()).decode('utf-8')

        # Tenta abrir a imagem do produto correspondente
        try:
            produto_imagem = open('expedicao/static/img/produto/' + dados_lista[k]['item'] + '.png', "rb")
            dados_lista[k]['produto_imagem'] = base64.b64encode(produto_imagem.read()).decode('utf-8')
        except:
            None  # Se não encontrar, ignora o erro

        # Verifica se o lado é "ESQUERDO" e processa a imagem do croqui
        if dados_lista[k]['lado'] == 'ESQUERDO':
            try:
                try:
                    # Tenta abrir a imagem do croqui com base no item e modulação
                    croqui = open('expedicao/static/img/croqui/' + dados_lista[k]['item'] + '/' + dados_lista[k]['modulacao'] + '.png', "rb")
                    croqui = base64.b64encode(croqui.read()).decode('utf-8')
                    # Inverte a imagem do croqui horizontalmente
                    croqui_invertido = Image.open(BytesIO(base64.b64decode(croqui)))
                    croqui_invertido = croqui_invertido.transpose(Image.FLIP_LEFT_RIGHT)
                    buffered = BytesIO()  # Cria um buffer para a imagem invertida
                    croqui_invertido.save(buffered, format="PNG")
                    dados_lista[k]['croqui'] = base64.b64encode(buffered.getvalue()).decode('utf-8')
                except:
                    # Se não encontrar, tenta abrir a imagem com base apenas na modulação
                    croqui = open('expedicao/static/img/croqui/' + dados_lista[k]['modulacao'] + '.png', "rb")
                    croqui = base64.b64encode(croqui.read()).decode('utf-8')
                    croqui_invertido = Image.open(BytesIO(base64.b64decode(croqui)))
                    croqui_invertido = croqui_invertido.transpose(Image.FLIP_LEFT_RIGHT)
                    buffered = BytesIO()
                    croqui_invertido.save(buffered, format="PNG")
                    dados_lista[k]['croqui'] = base64.b64encode(buffered.getvalue()).decode('utf-8')
            except:
                None  # Se não encontrar, ignora o erro
        else:
            # Se o lado não for "ESQUERDO", tenta abrir a imagem normalmente
            try:
                try:
                    croqui = open('expedicao/static/img/croqui/' + dados_lista[k]['item'] + '/' + dados_lista[k]['modulacao'] + '.png', "rb")
                    dados_lista[k]['croqui'] = base64.b64encode(croqui.read()).decode('utf-8')
                except:
                    # Se não encontrar, tenta abrir a imagem com base apenas na modulação
                    croqui_2 = open('expedicao/static/img/croqui/' + dados_lista[k]['modulacao'] + '.png', "rb")
                    dados_lista[k]['croqui'] = base64.b64encode(croqui_2.read()).decode('utf-8')
            except:
                None  # Se não encontrar, ignora o erro

        # Tenta abrir a imagem de conforto correspondente
        try:
            conforto_imagem = open('expedicao/static/img/conforto/' + dados_lista[k]['conforto'] + '.png', "rb")
            dados_lista[k]['conforto_imagem'] = base64.b64encode(conforto_imagem.read()).decode('utf-8')
        except:
            None  # Se não encontrar, ignora o erro

        # Tenta abrir a imagem do QR code
        try:
            qr_code = open('expedicao/static/img/qr_code.png', "rb")
            dados_lista[k]['qr_code'] = base64.b64encode(qr_code.read()).decode('utf-8')
        except:
            None  # Se não encontrar, ignora o erro

        # Arredonda o volume e o converte para inteiro
        dados_lista[k]['volume'] = int(round(dados_lista[k]['volume'], 0))

        # Adiciona os dados processados à lista final
        dados.append(dados_lista[k])

    return dados  # Retorna a lista de dados processados


def Dados_etiqueta_2(idioma,tipo_ped,pedido):

    # Definir uma consulta SQL
    sql = open('expedicao/static/sql/etiqueta_2.sql').read()
    
    # Executar a consulta
    params =  {'idioma': idioma, 'pedido': pedido,'tipo_ped': tipo_ped}

    # Chama a função API_etiqueta para obter os dados do pedido
    dados_lista = Query(sql,params)
    
    dados = []  # Lista para armazenar os dados processados

    for k in range(len(dados_lista)):
        # Tenta processar a imagem do tecido
        try:
            tecido = 'expedicao/static/img/tecido/' + dados_lista[k]['filho'] + '.png'
            dados_lista[k]['tec_imagem'] = processar_imagem(tecido)
        except:
            None  # Se não encontrar, ignora o erro

        # Tenta processar a imagem do acabamento
        try:
            acabamento = 'expedicao/static/img/acabamento/' + dados_lista[k]['pai'] + '/' + dados_lista[k]['filho'] + '.png'
            dados_lista[k]['acab_imagem'] = processar_imagem(acabamento)
        except:
            None  # Se não encontrar, ignora o erro

        # Adiciona os dados processados à lista final
        dados.append(dados_lista[k])

    return dados  # Retorna a lista de dados processados


def processar_imagem(imagem):
    # Abre o arquivo de imagem em modo binário
    image_file = open(imagem, "rb")
    
    # Lê o conteúdo do arquivo e codifica em base64
    imagem = base64.b64encode(image_file.read()).decode('utf-8')

    # Decodifica a string base64 de volta para os dados da imagem
    image_data = base64.b64decode(imagem)
    
    # Abre a imagem usando PIL a partir dos dados decodificados
    img = Image.open(BytesIO(image_data))
    
    # Cria um buffer para salvar a imagem resultante
    buffer = BytesIO()
    
    # Salva a imagem no buffer no formato PNG
    img.save(buffer, format="PNG")
    
    # Codifica o conteúdo do buffer em base64 e decodifica para string
    img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    return img_base64  # Retorna a imagem em base64