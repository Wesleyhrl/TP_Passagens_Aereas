### 🔎 Etapa 3 - Recuperação da Informação

Interface web desenvolvida com **Flask** para consultar voos com base em critérios como companhia, preço, escalas, origem, destino e duração, usando um **índice invertido por campo**.

---

#### ✅ Objetivos

* Permitir ao usuário fazer buscas textuais por campos específicos.
* Utilizar o índice invertido gerado na Etapa 2.
* Retornar os documentos (voos) mais relevantes.
* Apresentar estatísticas e detalhes do voo em páginas dedicadas.

---

#### 🧱 Estrutura dos Arquivos

```bash
03_Recuperacao/
├── app.py                   # Inicializa o servidor Flask e define as rotas
├── buscador.py              # Lógica de recuperação, ponderação e ranking
├── templates/
│   ├── index.html           # Página principal do buscador
│   ├── documento.html       # Página de detalhes de um voo
│   └── estatisticas.html    # Estatísticas sobre um documento
├── static/
│   └── style.css            # Estilo da aplicação
```

---

#### 🛠️ Pré-requisitos

* Python 3.8+
* Flask
* NLTK
* Bibliotecas (instaladas via requirements.txt):

Instalação:

```bash
pip install -r requirements.txt
```

---

#### ▶️ Como executar

1. Navegue até a pasta:

```bash
cd 03_Recuperacao
```

2. Execute o app Flask:

```bash
python app.py
```

3. Acesse no navegador:

```
http://localhost:5000
```
```
http://127.0.0.1:5000
```

---

#### 🔍 Funcionalidades

* **Busca por campos**: companhia, origem, destino, escalas, preço, duração.
* **Rankeamento dos resultados**: baseado em presença de termos e peso dos campos.
* **Detalhamento individual**: ao clicar em um resultado, é possível ver detalhes e estatísticas.
* **Estatísticas do Documento**: tempo de voo, quantidade de escalas, faixa de preço, entre outros.

---

#### 💡 Como funciona o ranking?

* O arquivo `buscador.py` calcula um ranking com base no número de ocorrências dos termos de busca em cada campo indexado.
* Campos mais importantes podem ter **peso maior** na pontuação final.

---

#### 📂 Entrada esperada

O arquivo `indice_invertido_por_campo.json` gerado na Etapa 2 deve estar acessível na mesma pasta ou em caminho configurado no buscador.

