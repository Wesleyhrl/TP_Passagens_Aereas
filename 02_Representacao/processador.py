import os
import json
from bs4 import BeautifulSoup

def extrair_voos(html_content):
    """Extrai informações de voos do HTML do Google Flights"""
    soup = BeautifulSoup(html_content, 'lxml')
    voos = []

    for card in soup.find_all('li', class_='pIav2d'):
        try:
            # Companhia aérea
            companhia_div = card.find('div', class_='sSHqwe')
            if companhia_div:
                raw_text = companhia_div.get_text(separator=' ', strip=True)
                if 'LATAM' in raw_text.upper():
                    companhia = 'LATAM Airlines Brasil'
                else:
                    companhia = raw_text
            else:
                companhia = ''

            # Horários
            partida_div = card.find('div', attrs={'aria-label': lambda x: x and 'Horário de partida' in x})
            chegada_div = card.find('div', attrs={'aria-label': lambda x: x and 'Horário de chegada' in x})
            partida = partida_div.get_text(strip=True) if partida_div else ''
            chegada = chegada_div.get_text(strip=True) if chegada_div else ''

            # Preço
            preco_element = card.select_one('div.YMlIz.FpEdX') or card.select_one('div.YMlIz.FpEdX.jLMuyc')
            preco = preco_element.get_text(strip=True) if preco_element else 'Preço indisponível'

            # Duração
            duracao = card.find('div', class_='gvkrdb')
            duracao = duracao.get_text(strip=True) if duracao else ''

            # Escalas
            escalas_element = card.find('div', class_='EfT7Ae')
            if escalas_element:
                span = escalas_element.find('span')
                escalas = span.get_text(strip=True) if span else ''
            else:
                escalas = ''

            voo = {
                'companhia': companhia,
                'partida': partida,
                'chegada': chegada,
                'preco': preco,
                'duracao': duracao,
                'escalas': escalas,
            }
            voos.append(voo)

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

                        # Log de progresso
                        if total_arquivos % 100 == 0:
                            print(f"Processados {total_arquivos} arquivos...")

    print(f"\nResumo:")
    print(f" - Total de arquivos processados: {total_arquivos}")
    print(f" - Total de voos extraídos: {total_voos_extraidos}")

    # Garante que o diretório de saída exista
    os.makedirs('./02_Representacao', exist_ok=True)

    # Salva o JSON final
    with open('./02_Representacao/voos_processados.json', 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

    return dados


if __name__ == "__main__":
    print("Iniciando processamento dos arquivos HTML...\n")
    dados_voos = processar_coletas("./01_Coleta/coletas_html_teste")
    print("\nConcluído! Resultados salvos em: ./02_Representacao/voos_processados.json")
