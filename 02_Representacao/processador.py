import os
import json
from bs4 import BeautifulSoup

def formatar_dados(dados):
    """
    Padroniza os dados extraídos para melhor indexação com tratamento especial por campo.
    
    Parâmetros:
        dados (dict): Dicionário com os dados brutos extraídos do HTML
        
    Retorna:
        dict: Dicionário com os dados formatados e padronizados
    """
    formatados = {}
    
    for campo, valor in dados.items():
        # Se o valor estiver vazio, armazena string vazia e pula para próximo campo
        if not valor:
            formatados[campo] = ''
            continue
            
        # Remove espaços não-quebráveis (\xa0) e espaços em branco no início/fim
        valor = valor.replace('\xa0', ' ').strip()
        
        # Tratamento específico para cada campo:
        
        # Campo: companhia aérea
        if campo == 'companhia':
            # Padroniza nomes da LATAM (considerando variações como "LATAM Airlines")
            if 'LATAM' in valor.upper():
                formatados[campo] = 'LATAM'
            else:
                # Remove espaços extras entre palavras
                formatados[campo] = ' '.join(valor.split())

        # Campos: horários de partida e chegada
        elif campo in ['partida', 'chegada']:
            # Remove espaços e mantém indicador de "+1 dia" se existir
            formatados[campo] = valor.replace(" ", "").replace("+", "+")

        # Campo: preço do voo
        elif campo == 'preco':
            # Remove espaços e formata moeda (ex: "R$ 1.000" -> "R$1000")
            preco_limpo = valor.replace(" ", "").replace("R$", "R$")
            # Remove pontos de milhar
            formatados[campo] = preco_limpo.replace(".", "")

        # Campo: duração do voo
        elif campo == 'duracao':
            # Converte formatos como "7 h 30 min" para "7h30min"
            dur = valor.replace(" h ", "h").replace(" min", "").replace(" ", "")
            formatados[campo] = dur

        # Campo: número de escalas
        elif campo == 'escalas':
            # Padroniza para formato com underscore ("1_parada")
            esc = valor.lower()
            if 'parada' in esc or 'paradas' in esc:
                esc = esc.replace("paradas", "parada").replace(" ", "_")
                formatados[campo] = esc
            else:
                formatados[campo] = valor.replace(" ", "_")

        # Para outros campos sem tratamento específico, mantém o valor original
        else:
            formatados[campo] = valor
            
    return formatados

def extrair_voos(html_content):
    """
    Extrai informações de voos do HTML do Google Voos.
    
    Parâmetros:
        html_content (str): Conteúdo HTML da página de resultados
        
    Retorna:
        list: Lista de dicionários contendo informações dos voos
    """
    # Cria objeto BeautifulSoup para parsear o HTML
    soup = BeautifulSoup(html_content, 'lxml')
    voos = []  # Lista dos voos extraídos

    # Encontra todos os elementos HTML que representam cards de voo
    for card in soup.find_all('li', class_='pIav2d'):
        try:
            # Dicionário com valores padrão para os campos
            dados_brutos = {
                'companhia': '',
                'partida': '',
                'chegada': '',
                'preco': 'Preço indisponível',  # Valor padrão caso não encontre preço
                'duracao': '',
                'escalas': ''
            }

            # Extração da companhia aérea
            companhia_div = card.find('div', class_='sSHqwe')
            if companhia_div:
                dados_brutos['companhia'] = companhia_div.get_text(separator=' ', strip=True)

            # Extração dos horários de partida e chegada
            partida_div = card.find('div', attrs={'aria-label': lambda x: x and 'Horário de partida' in x})
            chegada_div = card.find('div', attrs={'aria-label': lambda x: x and 'Horário de chegada' in x})
            dados_brutos['partida'] = partida_div.get_text(strip=True) if partida_div else ''
            dados_brutos['chegada'] = chegada_div.get_text(strip=True) if chegada_div else ''

            # Extração do preço
            preco_element = card.select_one('div.YMlIz.FpEdX') or card.select_one('div.YMlIz.FpEdX.jLMuyc')
            if preco_element:
                dados_brutos['preco'] = preco_element.get_text(strip=True)

            # Extração da duração do voo
            duracao = card.find('div', class_='gvkrdb')
            if duracao:
                dados_brutos['duracao'] = duracao.get_text(strip=True)

            # Extração do número de escalas
            escalas_element = card.find('div', class_='EfT7Ae')
            if escalas_element:
                span = escalas_element.find('span')
                if span:
                    dados_brutos['escalas'] = span.get_text(strip=True)

            # Formata os dados brutos para padronização
            voo_formatado = formatar_dados(dados_brutos)
            voos.append(voo_formatado)

        except Exception as e:
            print(f"[Erro ao extrair voo]: {str(e)}")
            continue  # Continua para o próximo voo em caso de erro

    return voos

def processar_coletas(pasta_coletas):
    """
    Processa todos os arquivos HTML de coletas de voos.
    
    Parâmetros:
        pasta_coletas (str): Caminho para a pasta contendo os arquivos HTML
        
    Retorna:
        dict: Dicionário com todos os voos processados organizados por chave única
    """
    dados = {}  # Armazenará todos os dados processados
    total_arquivos = 0
    total_voos_extraidos = 0

    # Percorre cada pasta de origem (ex: GRU, BSB)
    for origem in os.listdir(pasta_coletas):
        pasta_origem = os.path.join(pasta_coletas, origem)

        if os.path.isdir(pasta_origem):
            # Percorre cada arquivo HTML na pasta de origem
            for arquivo in os.listdir(pasta_origem):
                if arquivo.endswith('.html'):
                    # Extrai destino e data do nome do arquivo (formato: voos_ORIGEM_DESTINO_DATA.html)
                    partes = arquivo.split('_')
                    if len(partes) >= 3:
                        destino = partes[1]
                        data = partes[2].replace('.html', '')

                        caminho_arquivo = os.path.join(pasta_origem, arquivo)
                        try:
                            # Lê o arquivo e extrai os voos
                            with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                                voos = extrair_voos(f.read()) #f Extrai o voos
                        except Exception as e:
                            print(f"[Erro ao ler arquivo]: {arquivo} - {str(e)}")
                            continue

                        # Cria chave única para agrupamento (ORIGEM_DESTINO_DATA)
                        chave = f"{origem}_{destino}_{data}"
                        dados[chave] = {
                            'origem': origem,
                            'destino': destino,
                            'data': data,
                            'total_voos': len(voos),
                            'voos': voos
                        }

                        # Atualiza contadores
                        total_arquivos += 1
                        total_voos_extraidos += len(voos)

                        # Feedback periódico do progresso
                        if total_arquivos % 100 == 0:
                            print(f"Processados {total_arquivos} arquivos...")

    # Exibe resumo ao final do processamento
    print(f"\nResumo:")
    print(f" - Total de arquivos processados: {total_arquivos}")
    print(f" - Total de voos extraídos: {total_voos_extraidos}")

    os.makedirs('./02_Representacao', exist_ok=True)

    # Salva os dados processados em arquivo JSON
    with open('./02_Representacao/voos_processados.json', 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

    return dados

if __name__ == "__main__":
    print("Iniciando processamento dos arquivos HTML...\n")
    dados_voos = processar_coletas("./01_Coleta/coletas_html")
    print("\nConcluído! Resultados salvos em: ./02_Representacao/voos_processados.json")