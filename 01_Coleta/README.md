
### 📦 Etapa 1 - Coleta de Dados de Voos

Automação de coleta de informações sobre voos domésticos no Brasil a partir do **Google Flights**, usando **Selenium** com navegador automatizado. Este módulo coleta os dados em massa e salva os HTMLs para processamento posterior.

---

#### ✅ Objetivos

* Navegar automaticamente no site Google Voos.
* Gerar combinações de rotas entre aeroportos.
* Capturar e salvar as páginas HTML com detalhes dos voos.
* Registrar logs da operação.

---

#### 🛠️ Pré-requisitos

* Python 3.8 ou superior
* Navegador **Chrome**
* WebDriver compatível com seu navegador (por exemplo, `msedgedriver.exe` ou `chromedriver.exe`)
* Bibliotecas (instaladas via `requirements.txt`):

```bash
pip install -r requirements.txt
```

---

#### 📂 Estrutura dos Scripts

* `coleta.py` - Script principal que faz a varredura automática e salva os HTMLs.
* `coleta_teste.py` - Script de teste rápido que abre a interface e executa manualmente um caso de navegação.

---

#### ▶️ Como executar

1. Navegue até a pasta:

```bash
cd 01_Coleta
```

2. Execute o:

```bash
python coleta.py
```

* O script gerará arquivos `.html` na pasta `coletas_html/`.
* Logs de execução serão salvos em `logs/`.

> **Observação:** o script considera uma lista de aeroportos e combinações, com tempo de espera entre buscas para evitar bloqueios.

---

#### 🧪 Teste Manual (opcional)

Para testar a automação sem varrer todos os voos, rode:

```bash
python coleta_teste.py
```

Esse script acessa o Google Voos, seleciona a opção "Só ida" e preenche manualmente os campos — útil para ajustar XPATHs ou verificar se o site mudou.

---

#### 🧠 Personalização

* **Data de viagem**: pode ser configurada no corpo do script `coleta.py`.
* **Aeroportos**: definidos a partir da lista de aeroportos brasileiros em `docs/Aeroportos Brasileiros.txt`, podem ser mudados em uma lista no `coleta.py`.
* **Tempo entre buscas**: alterável na função principal para evitar bloqueios ou sobrecarga no site.
