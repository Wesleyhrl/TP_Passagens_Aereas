### 🧩 Etapa 2 - Representação dos Dados de Voos

Transformação e estruturação dos dados HTML coletados em uma forma textual compreensível para sistemas de busca, por meio de técnicas de pré-processamento e indexação invertida.

---

#### ✅ Objetivos

* **Ler HTMLs de voos** salvos pela etapa 1.
* Extrair e **formatar dados estruturados** como companhia, escalas, duração, origem, destino e preço.
* Gerar **índice invertido por campo**, permitindo buscas por diferentes critérios no futuro.

---

#### 📂 Estrutura dos Scripts

* `processador.py` – Extrai os dados dos arquivos HTML e padroniza os campos.
* `indexador.py` – Aplica tokenização, remoção de stopwords, stemming e cria o índice invertido por campo.

---

#### 📁 Entradas esperadas

* HTMLs salvos em `coletas_html/` pela Etapa 1.

---

#### 🛠️ Pré-requisitos

* Bibliotecas: `nltk`, `beautifulsoup4`, `json`
* Downloads necessários (executados automaticamente no primeiro uso):

```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
```
Instalação:

```bash
pip install -r requirements.txt
```

---

#### ⚙️ Como usar

1. **Processar HTMLs**:

Você pode usar as funções do `processador.py` para ler os arquivos HTML salvos e extrair os dados relevantes de cada voo.

2. **Indexar os dados**:

O `indexador.py` recebe os dados limpos e gera um índice invertido por campo com as seguintes etapas:

* Tokenização
* Remoção de palavras irrelevantes (stopwords)
* Stemming com `RSLPStemmer` (ex: "voando" → "vo")
* Geração de índice em `indice_invertido_por_campo.json`

---

#### ▶️ Como executar

1. Navegue até a pasta:

```bash
cd 02_Representacao
```

2. Execute o:

```bash
python processador.py
```

3. Depois, Execute o:

```bash
python indexador.py
```

---

#### 🧠 Campos indexados

* **companhia**
* **escalas**
* **duração**
* **origem / destino**
* **códigos IATA**
* **preço** (como texto, para permitir buscas por termos com faixa de preço etc.)

---

#### 🗂️ Saída esperada

```bash
02_Representacao/
├── indice_invertido_por_campo.json
```

Este arquivo é consumido na etapa seguinte para responder consultas e fazer ranking dos documentos.

