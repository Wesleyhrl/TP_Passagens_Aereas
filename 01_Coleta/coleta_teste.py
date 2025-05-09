from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

# Configurar o navegador
options = webdriver.EdgeOptions()
options.add_experimental_option("detach", True)
driver = webdriver.Edge(options=options)
driver.maximize_window()
driver.get("https://www.google.com/travel/flights")

# Selecionar tipo de passagem (Só ida)
select_passagem = driver.find_element(By.XPATH, '/html/body/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[1]/div[1]/div[1]/div/div[1]/div[1]/div/div/div')
select_passagem.click()

option_ida = driver.find_element(By.XPATH, '/html/body/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[1]/div[1]/div[1]/div/div[1]/div[1]/div/div/div/div[2]/ul/li[2]')
option_ida.click()

# Preencher data
input_data = driver.find_element(By.XPATH, '/html/body/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[1]/div[1]/div[1]/div/div[2]/div[2]/div/div/div[1]/div/div/div[1]/div/div[1]/div/input')
input_data.clear()
input_data.send_keys("05/05/2025")

# Preencher origem e destino
input_origem = driver.find_element(By.XPATH, '/html/body/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[1]/div[1]/div[1]/div/div[2]/div[1]/div[1]/div/div/div[1]/div/div/input')
input_origem.clear()
input_origem.send_keys("CNF")

select_origem = WebDriverWait(driver, 5).until(
    EC.presence_of_element_located((By.XPATH, '/html/body/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[1]/div[1]/div[1]/div/div[2]/div[1]/div[6]/div[3]/ul/li[1]'))
)
select_origem.click()

input_destino = driver.find_element(By.XPATH, '/html/body/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[1]/div[1]/div[1]/div/div[2]/div[1]/div[4]/div/div/div[1]/div/div/input')
input_destino.clear()
input_destino.send_keys("CGH")

select_destino = WebDriverWait(driver, 5).until(
    EC.presence_of_element_located((By.XPATH, '/html/body/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[1]/div[1]/div[1]/div/div[2]/div[1]/div[6]/div[3]/ul/li[1]'))
)
select_destino.click()

# Clicar em pesquisar
button_pesquisar = driver.find_element(By.XPATH, '/html/body/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[1]/div[1]/div[2]/div/button')
button_pesquisar.click()

# Esperar e clicar em "Mais voos"
button_mais_voos = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, 'zISZ5c.QB2Jof'))
)
button_mais_voos.click()

# *** ESPERAR ATÉ QUE "MOSTRAR MENOS VOOS" APAREÇA (SINAL DE QUE TUDO CARREGOU) ***
WebDriverWait(driver, 10).until(EC.text_to_be_present_in_element((By.CLASS_NAME, 'bEfgkb'),"Mostrar menos voos"));

time.sleep(6);

# Capturar o HTML ATUALIZADO (com todos os voos)
html_content = driver.page_source




# Criar pasta 'coletas_html' (se não existir)
pasta_coletas = os.path.join(os.path.dirname(__file__), "coletas_html")
os.makedirs(pasta_coletas, exist_ok=True)

#  Definir caminho do arquivo
nome_arquivo = "voos_resultado.html"
caminho_completo = os.path.join(pasta_coletas, nome_arquivo)

# Salvar em um arquivo

with open(caminho_completo, "w", encoding="utf-8") as file:
    file.write(html_content)

print("Página com TODOS os voos salva com sucesso!")
driver.quit()