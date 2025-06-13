
# ✈️ TP - Sistema de Recuperação de Informações de Voos

Este projeto implementa um pipeline completo de **coleta**, **representação** e **recuperação da informação** sobre **voos domésticos no Brasil**, com base em dados extraídos do **Google Voos**.

---

## 📌 Visão Geral

O sistema está dividido em **3 etapas principais**:

| Etapa              | Objetivo                                                             |
| ------------------ | -------------------------------------------------------------------- |
| 01 - Coleta        | Automatizar a navegação no Google Voos e salvar páginas HTML de voos |
| 02 - Representação | Extrair dados dos HTMLs e gerar um índice invertido por campo        |
| 03 - Recuperação   | Criar uma interface web usando um módulo busca com ranking de resultados           |

---

## 🗂️ Estrutura do Projeto

```
TP_Passagens_Aereas-main/
├── 01_Coleta/              # Scripts de coleta automática com Selenium
├── 02_Representacao/       # Extração e indexação com NLTK
├── 03_Recuperacao/         # Interface web com Flask
├── docs/                   # Documentação e listas de aeroportos
└── README.md               # Este arquivo
```

---

## 🚀 Como Executar o Projeto

### 1. Clone o Repositório

```bash
git clone [URL_DO_REPOSITORIO]
cd [NOME_DO_REPOSITORIO]
```

### 2. Instale os Requisitos

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

---

## 🧪 Etapas

### 🔹 Etapa 1 - Coleta de Dados

* Caminho: `01_Coleta/`
* Requisitos: `selenium`, navegador Edge ou Chrome, driver correspondente.
* Executar com:

```bash
python coleta.py
```

* Resultado: HTMLs salvos em `coletas_html/`.

---

### 🔹 Etapa 2 - Representação e Indexação

* Caminho: `02_Representacao/`
* Requisitos: `nltk`, `beautifulsoup4`
* Processa HTMLs e gera: `indice_invertido_por_campo.json`
* Executar os:

```bash
python processador.py
python indexador.py
```

---

### 🔹 Etapa 3 - Recuperação da Informação

* Caminho: `03_Recuperacao/`
* Requisitos: `flask`, `nltk`
* Inicie a aplicação com:

```bash
python app.py
```

* Acesse: `http://localhost:5000`

Permite busca por:

* Companhia
* Origem / Destino
* Preço
* Duração
* Escalas

---

## 📚 Créditos

Este projeto foi desenvolvido como parte de um trabalho prático da disciplina **Recuperação da Informação na Web e Redes Sociais**, com foco em:

* Web Coletores
* Pré-processamento textual (tokenização, stemming)
* Construção de índice invertido
* Modelo vetorial com TF-IDF
* Algoritmos de ranqueamento
* Interface de apoio à decisão

