import os
import json
from bs4 import BeautifulSoup

def formatar_dados(dados):
    """Padroniza os dados para melhor indexação com tratamento especial"""
    formatados = {}
    
    for campo, valor in dados.items():
        if not valor:
            formatados[campo] = ''
            continue
            
        # Remove espaços não-quebráveis e caracteres especiais
        valor = valor.replace('\xa0', ' ').strip()
        
        # Tratamento específico por campo
        if campo == 'companhia':
            if 'LATAM' in valor.upper():
                formatados[campo] = 'LATAM'
            else:
                formatados[campo] = ' '.join(valor.split())  # Normaliza espaços

        elif campo in ['partida', 'chegada']:
            formatados[campo] = valor.replace(" ", "").replace("+", "+")  # Mantém o +1

        elif campo == 'preco':
            # Remove todos os espaços e formata R$ corretamente
            preco_limpo = valor.replace(" ", "").replace("R$", "R$")
            # Remove pontos de milhar se necessário (opcional)
            formatados[campo] = preco_limpo.replace(".", "")

        elif campo == 'duracao':
            # Converte "7 h" para "7h" e "30 h 15 min" para "30h15min"
            dur = valor.replace(" h ", "h").replace(" min", "").replace(" ", "")
            formatados[campo] = dur

        elif campo == 'escalas':
            # Garante o formato "X_parada(s)"
            esc = valor.lower()
            if 'parada' in esc or 'paradas' in esc:
                esc = esc.replace("paradas", "parada").replace(" ", "_")
                formatados[campo] = esc
            else:
                formatados[campo] = valor.replace(" ", "_")

        else:
            formatados[campo] = valor
            
    return formatados

def extrair_voos(html_content):
    """Extrai informações de voos do HTML do Google Flights"""
    soup = BeautifulSoup(html_content, 'lxml')
    voos = []

    for card in soup.find_all('li', class_='pIav2d'):
        try:
            # Extração dos dados brutos
            dados_brutos = {
                'companhia': '',
                'partida': '',
                'chegada': '',
                'preco': 'Preço indisponível',
                'duracao': '',
                'escalas': ''
            }

            # Companhia aérea
            companhia_div = card.find('div', class_='sSHqwe')
            if companhia_div:
                dados_brutos['companhia'] = companhia_div.get_text(separator=' ', strip=True)

            # Horários
            partida_div = card.find('div', attrs={'aria-label': lambda x: x and 'Horário de partida' in x})
            chegada_div = card.find('div', attrs={'aria-label': lambda x: x and 'Horário de chegada' in x})
            dados_brutos['partida'] = partida_div.get_text(strip=True) if partida_div else ''
            dados_brutos['chegada'] = chegada_div.get_text(strip=True) if chegada_div else ''

            # Preço
            preco_element = card.select_one('div.YMlIz.FpEdX') or card.select_one('div.YMlIz.FpEdX.jLMuyc')
            if preco_element:
                dados_brutos['preco'] = preco_element.get_text(strip=True)

            # Duração
            duracao = card.find('div', class_='gvkrdb')
            if duracao:
                dados_brutos['duracao'] = duracao.get_text(strip=True)

            # Escalas
            escalas_element = card.find('div', class_='EfT7Ae')
            if escalas_element:
                span = escalas_element.find('span')
                if span:
                    dados_brutos['escalas'] = span.get_text(strip=True)

            # Formata os dados para indexação
            voo_formatado = formatar_dados(dados_brutos)
            voos.append(voo_formatado)

        except Exception as e:
            print(f"[Erro ao extrair voo]: {str(e)}")
            continue

    return voos

def processar_coletas(pasta_coletas):
    dados = {}
    total_arquivos = 0
    total_voos_extraidos = 0

    for origem in os.listdir(pasta_coletas):
        pasta_origem = os.path.join(pasta_coletas, origem)

        if os.path.isdir(pasta_origem):
            for arquivo in os.listdir(pasta_origem):
                if arquivo.endswith('.html'):
                    partes = arquivo.split('_')
                    if len(partes) >= 3:
                        destino = partes[1]
                        data = partes[2].replace('.html', '')

                        caminho_arquivo = os.path.join(pasta_origem, arquivo)
                        try:
                            with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                                voos = extrair_voos(f.read())
                        except Exception as e:
                            print(f"[Erro ao ler arquivo]: {arquivo} - {str(e)}")
                            continue

                        chave = f"{origem}_{destino}_{data}"
                        dados[chave] = {
                            'origem': origem,
                            'destino': destino,
                            'data': data,
                            'total_voos': len(voos),
                            'voos': voos
                        }

                        total_arquivos += 1
                        total_voos_extraidos += len(voos)

                        if total_arquivos % 100 == 0:
                            print(f"Processados {total_arquivos} arquivos...")

    print(f"\nResumo:")
    print(f" - Total de arquivos processados: {total_arquivos}")
    print(f" - Total de voos extraídos: {total_voos_extraidos}")

    os.makedirs('./02_Representacao', exist_ok=True)

    with open('./02_Representacao/voos_processados.json', 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

    return dados

if __name__ == "__main__":
    print("Iniciando processamento dos arquivos HTML...\n")
    dados_voos = processar_coletas("./01_Coleta/coletas_html_teste")
    print("\nConcluído! Resultados salvos em: ./02_Representacao/voos_processados.json")