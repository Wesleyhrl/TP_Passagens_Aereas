from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from itertools import permutations
import time
import os
import datetime

# Lista completa de aeroportos domésticos brasileiros
AEROPORTOS_BR = [
    'BSB', 'CGH', 'GIG', 'SSA', 'FLN', 'POA', 'VCP', 'REC', 'CWB', 'BEL',
    'VIX', 'SDU', 'CGB', 'CGR', 'FOR', 'MCP', 'MGF', 'GYN', 'NVT', 'MAO',
    'NAT', 'BPS', 'MCZ', 'PMW', 'SLZ', 'GRU', 'LDB', 'PVH', 'RBR', 'JOI',
    'UDI', 'CXJ', 'IGU', 'THE', 'AJU', 'JPA', 'PNZ', 'CNF', 'BVB', 'CPV',
    'STM', 'IOS', 'JDO', 'IMP', 'XAP', 'MAB', 'CZS', 'PPB', 'FEN',
    'JTC', 'MOC'
]

# Configurações do navegador


def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    return driver

# Função para configurar a busca no Google Voos


def configurar_busca(driver, origem, destino, data):
    driver.get("https://www.google.com/travel/flights?tfs=CBwQARoOagwIAhIIL20vMGwzcTJAAUgBcAGCAQsI____________AZgBAg&tfu=KgIIAw")

    time.sleep(2)  # esperar carregar a pagina

    # Preencher data
    input_data = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable(
            (By.XPATH, '/html/body/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[1]/div[1]/div[1]/div/div[2]/div[2]/div/div/div[1]/div/div/div[1]/div/div[1]/div/input'))
    )
    input_data.clear()
    input_data.send_keys(data)

    # Preencher origem
    input_origem = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable(
            (By.XPATH, '/html/body/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[1]/div[1]/div[1]/div/div[2]/div[1]/div[1]/div/div/div[1]/div/div/input'))
    )
    input_origem.clear()
    input_origem.send_keys(origem)

    try:
        select_origem = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(
                (By.XPATH, '/html/body/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[1]/div[1]/div[1]/div/div[2]/div[1]/div[6]/div[3]/ul/li[1]'))
        )
        select_origem.click()
    except:
        print(f"Não encontrou aeroporto de origem: {origem}")
        return False

    # Preencher destino
    input_destino = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable(
            (By.XPATH, '/html/body/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[1]/div[1]/div[1]/div/div[2]/div[1]/div[4]/div/div/div[1]/div/div/input'))
    )
    input_destino.clear()
    input_destino.send_keys(destino)

    try:
        select_destino = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(
                (By.XPATH, '/html/body/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[1]/div[1]/div[1]/div/div[2]/div[1]/div[6]/div[3]/ul/li[1]'))
        )
        select_destino.click()
    except:
        print(f"Não encontrou aeroporto de destino: {destino}")
        return False

    # Clicar em pesquisar
    button_pesquisar = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable(
            (By.XPATH, '/html/body/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[1]/div[1]/div[2]/div/button'))
    )
    button_pesquisar.click()

    return True

# Função para coletar os dados da página


def coletar_dados(driver, origem, destino, data):
    
    try:
        # Verificar primeiro se aparece a mensagem de "não há voos"
        try:
            WebDriverWait(driver, 6).until(
                EC.text_to_be_present_in_element((By.CLASS_NAME, "QEk4oc.BgYkof"), "Não há nenhum voo para sua pesquisa")
            )
            print(f"Não há voos disponíveis para {origem}-{destino} em {data}")
            
            # Salvar a página mesmo sem voos (para registro)
            html_content = driver.page_source
            salvar_html(html_content, origem, destino, data)
            return True
            
        except Exception as NenhumVooException:
            # Se não encontrou a mensagem de "sem voos", prossegue com o fluxo normal
            pass

        # Fluxo normal quando há voos disponíveis
        try:
            # Esperar e clicar em "Mais voos" (se existir)
            button_mais_voos = WebDriverWait(driver, 6).until(
                EC.element_to_be_clickable((By.CLASS_NAME, 'zISZ5c.QB2Jof'))
            )
            button_mais_voos.click()
            
            # Esperar até que "Mostrar menos voos" apareça
            WebDriverWait(driver, 6).until(
                EC.text_to_be_present_in_element((By.CLASS_NAME, 'bEfgkb'), "Mostrar menos voos")
            )
            
            time.sleep(2)  # Espera adicional para garantir carregamento
            
        except Exception as SemMaisVoosException:
            # Se não encontrar o botão "Mais voos", pode ser que já estejam todos carregados
            print("Botão 'Mais voos' não encontrado - provavelmente poucos resultados")
            pass

        # Capturar o HTML em qualquer caso
        html_content = driver.page_source
        salvar_html(html_content, origem, destino, data)
        return True
        
    except Exception as e:
        print(f"Erro ao coletar dados para {origem}-{destino} em {data}: {str(e)}")
        return False

# Função para salvar o HTML


def salvar_html(html_content, origem, destino, data):
    # Criar estrutura de pastas
    base_dir = os.path.join(os.path.dirname(__file__), "coletas_html")
    os.makedirs(base_dir, exist_ok=True)

    pasta_origem = os.path.join(base_dir, origem)
    os.makedirs(pasta_origem, exist_ok=True)

    # Nome do arquivo
    nome_arquivo = f"{origem}_{destino}_{data.replace('/', '-')}.html"
    caminho_completo = os.path.join(pasta_origem, nome_arquivo)

    # Salvar arquivo
    with open(caminho_completo, "w", encoding="utf-8") as file:
        file.write(html_content)

    print(f"Arquivo salvo: {caminho_completo}")

# Função principal


def main():
    driver = setup_driver()

    # Definir período de 7 dias a partir de amanhã
    data_inicio = datetime.datetime.strptime("01/05/2025", "%d/%m/%Y").date()
    datas = [data_inicio + datetime.timedelta(days=i) for i in range(7)]
    datas_formatadas = [data.strftime("%d/%m/%Y") for data in datas]

    # Gerar todas as combinações de rotas (sem repetição de origem e destino)
    rotas = permutations(AEROPORTOS_BR, 2)

    # Contadores
    total_coletado = 0
    total_erros = 0

    try:
        for origem, destino in rotas:
            for data in datas_formatadas:
                print(f"\nColetando: {origem} -> {destino} em {data}")

                if configurar_busca(driver, origem, destino, data):
                    if coletar_dados(driver, origem, destino, data):
                        total_coletado += 1
                    else:
                        total_erros += 1

                # Pausa entre requisições para evitar bloqueio
                time.sleep(4)

    finally:
        driver.quit()
        print(
            f"\nColeta concluída! Total de páginas salvas: {total_coletado} | Erros: {total_erros}")


if __name__ == "__main__":
    main()
