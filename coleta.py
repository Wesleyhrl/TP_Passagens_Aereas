from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from itertools import permutations
from bs4 import BeautifulSoup
import time
import os
import datetime
import random

timestamp_arquivo = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
#Registra mensagens no arquivo de log
def registrar_log(mensagem):

    log_dir = os.path.join(os.path.dirname(__file__), "logs")
    os.makedirs(log_dir, exist_ok=True)
    # Usa um timestamp único para o nome do arquivo
    log_file = os.path.join(log_dir, f"log_coleta_voos_{timestamp_arquivo}.txt")
    # Timestamp para as mensagens (formato mais legível)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{timestamp} - {mensagem}"
    
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(log_entry + "\n")
    
    # Também exibe no console
    print(log_entry)

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
    options.add_argument("--headless")
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
                EC.text_to_be_present_in_element(
                    (By.CLASS_NAME, "QEk4oc.BgYkof"), "Não há nenhum voo para sua pesquisa")
            )
            print(f"Não há voos disponíveis para {origem}-{destino} em {data}")
            time.sleep(0.5)
            # Salvar a página mesmo sem voos (para registro)
            html_content_limpo = clean_html(driver.page_source)
            salvar_html(html_content_limpo, origem, destino, data)
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
                EC.text_to_be_present_in_element(
                    (By.CLASS_NAME, 'bEfgkb'), "Mostrar menos voos")
            )

            time.sleep(2)  # Espera adicional para garantir carregamento

        except Exception as SemMaisVoosException:
            # Se não encontrar o botão "Mais voos", pode ser que já estejam todos carregados
            print("Botão 'Mais voos' não encontrado - provavelmente poucos resultados")
            pass

        # Capturar o HTML em qualquer caso
        html_content_limpo = clean_html(driver.page_source)
        salvar_html(html_content_limpo, origem, destino, data)
        return True

    except Exception as e:
        registrar_log(f"Erro ao coletar dados {origem}-{destino}", erro=True, detalhes_erro=str(e))
        return False


# Função para Limpar Html
def clean_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    # Remove as tags selecionas
    for tag in soup(['script', 'link', 'style', 'noscript','svg','path']):
        tag.decompose()

    # Remove todos os atributos que começam com ...
    for tag in soup.find_all(True):  # True = todas as tags
        for attr in list(tag.attrs):  # Usando list() para evitar RuntimeError
           if attr.startswith(('data-', 'js' )):  # Se o atributo começa com 'data-' 'js'
                del tag.attrs[attr]  # Remove o atributo

    return str(soup)


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

    registrar_log(f"Arquivo salvo: {nome_arquivo}")

# CONSTANTES DE CONFIGURAÇÃO
CONFIG = {
    'MAX_TENTATIVAS': 2,                  # Número máximo de tentativas por coleta
    'PAUSA_ENTRE_REQUISICOES': (3, 5),    # Intervalo aleatório entre requisições (min, max)
    'DIAS_COLETA': 7,                     # Período de coleta (dias)
    'LIMITE_ERROS_SEGUIDOS': 3            # Máximo de erros consecutivos antes de parar
}

# Função principal
def main():
    inicio_execucao = time.time()
    registrar_log("=== INÍCIO DA COLETA ===")

    driver = setup_driver()

    # Definir período de dias de coleta
    data_inicio = datetime.datetime.strptime("01/07/2025", "%d/%m/%Y").date()
    datas = [data_inicio + datetime.timedelta(days=i) for i in range(CONFIG['DIAS_COLETA'])]
    datas_formatadas = [data.strftime("%d/%m/%Y") for data in datas]
    
    total_coletado = 0
    total_erros = 0
    erros_seguidos = 0  # Contador de erros consecutivos

    try:
        for origem, destino in permutations(AEROPORTOS_BR, 2): # Gerar todas as combinações de rotas (sem repetição de origem e destino)
            for data in datas_formatadas:
                tentativas = 0
                sucesso = False
                
                while not sucesso and tentativas < CONFIG['MAX_TENTATIVAS']:
                    try:
                        registrar_log(f"Coletando ({tentativas+1}ª tentativa): {origem} -> {destino} em {data}")
                        
                        if configurar_busca(driver, origem, destino, data):
                            if coletar_dados(driver, origem, destino, data):
                                total_coletado += 1
                                sucesso = True
                                erros_seguidos = 0  # Resetar contador de erros
                            else:
                                total_erros += 1
                                erros_seguidos += 1
                                registrar_log(f"Falha ao coletar: {origem}-{destino} ({data})")
                        
                        # Verificar critério de parada por erros consecutivos
                        if erros_seguidos >= CONFIG['LIMITE_ERROS_SEGUIDOS']:
                            registrar_log(f"INTERRUPÇÃO: Muitos erros consecutivos ({erros_seguidos})")
                            raise Exception("Limite de erros consecutivos atingido")
                        
                        # Pausa estratégica entre requisições
                        pausa = random.uniform(*CONFIG['PAUSA_ENTRE_REQUISICOES'])
                        registrar_log(f"Aguardando {pausa:.1f} segundos...")
                        time.sleep(pausa)
                        
                    except Exception as e:
                        tentativas += 1
                        print(f"Erro na tentativa {tentativas}: {str(e)}")
                        if tentativas >= CONFIG['MAX_TENTATIVAS']:
                            total_erros += 1
                            erros_seguidos += 1
                        time.sleep(2)  # Pausa adicional após erro
    except Exception as e:
        registrar_log(f"ERRO GRAVE: {str(e)}")
    finally:
        driver.quit()
        tempo_total = time.time() - inicio_execucao
        
        # Registra o resumo final
        registrar_log("\n=== RESUMO FINAL ===")
        registrar_log(f"Tempo total: {tempo_total/60:.2f} minutos")
        registrar_log(f"Páginas salvas: {total_coletado}")
        registrar_log(f"Erros: {total_erros}")


if __name__ == "__main__":
    main()
