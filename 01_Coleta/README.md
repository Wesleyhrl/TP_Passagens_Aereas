# Coletor de Dados de Voos (Passagens Aéreas) - Google Flights

**Automação para coleta de informações, preços e disponibilidade de voos domésticos no Brasil**

Este projeto utiliza Selenium para extrair dados de passagens aéreas do Google Flights, automatizando a busca por todas as combinações possíveis entre aeroportos brasileiros em um período determinado. Os resultados são salvos em HTML para análise posterior.

## Pré-requisitos
- Python 3.8+
- Google Chrome instalado

## Instalação
```bash
git clone [URL_DO_REPOSITORIO]
cd [NOME_DO_REPOSITORIO]
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

## Execução
```bash
python coleta.py
```

## Estrutura de Arquivos
```bash
coletas_html/
└── [ORIGEM]/
    └── ORIGEM_DESTINO_DATA.html
logs/
└── log_coleta_voos_[TIMESTAMP].txt
```

