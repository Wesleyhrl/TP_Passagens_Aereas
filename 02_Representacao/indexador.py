import json
import re
import os
import time
from collections import defaultdict
from nltk.corpus import stopwords
from nltk.stem import RSLPStemmer
from nltk.tokenize import word_tokenize
import nltk

# Configurações iniciais, Baixa os recursos necessários do NLTK 
nltk.download('punkt')
nltk.download('stopwords')

class IndexadorVoos:
    def __init__(self):
        """Inicializa o indexador com configurações básicas"""
        # Conjunto de stopwords em português para remoção
        self.stop_words = set(stopwords.words('portuguese'))
        # Stemmer em português para redução de palavras à raiz
        self.stemmer = RSLPStemmer()
        # Campos que serão indexados
        self.campos_indice = [
            "companhia", "escalas", "duracao", 
            "origem", "destino", "cod_origem", "cod_destino", "preco"
        ]
    
    def preprocessar_texto(self, texto):
        """
        Realiza pré-processamento de texto incluindo:
        - Tokenização
        - Limpeza de caracteres especiais
        - Remoção de stopwords
        - Stemming
        
        Parâmetros:
            texto (str): Texto a ser processado
            
        Retorna:
            list: Lista de tokens processados
        """
        if not texto:
            return []
            
        # Tokeniza o texto em palavras individuais    
        tokens = word_tokenize(texto.lower(), language='portuguese')
        # Remove caracteres não alfanuméricos e filtra tokens vazios
        tokens = [re.sub(r'\W+', '', t) for t in tokens if re.match(r'\w+', t)]
        # Aplica stemming e remove stopwords
        return [self.stemmer.stem(t) for t in tokens if t not in self.stop_words and t != '']
    
    def processar_preco(self, preco_str):
        """
        Classifica preços em categorias para indexação
        
        Parâmetros:
            preco_str (str): String contendo o preço
            
        Retorna:
            str: Categoria do preço 
        """
        try:
            # Extrai apenas dígitos e converte para float
            valor = float(re.sub(r'[^\d,]', '', preco_str).replace(',', '.'))
        except:
            return "p_nd"  # Retorna categoria para preço não disponível
        
        # Classifica em faixas de preço
        if valor <= 250: return "p_0_250"
        if valor <= 500: return "p_251_500"
        if valor <= 750: return "p_501_750"
        if valor <= 1000: return "p_751_1000"
        if valor <= 1500: return "p_1001_1500"
        if valor <= 2000: return "p_1501_2000"
        if valor <= 3000: return "p_2001_3000"
        return "p_3000m"
    
    def construir_indice(self, arquivo_json, pasta_saida='./02_Representacao/indice'):
        """
        Constrói e salva o índice invertido com frequência de termos por documento.
        
        Parâmetros:
            arquivo_json (str): Caminho para o arquivo JSON com os dados
            pasta_saida (str): Pasta onde serão salvos os resultados
        """
        inicio = time.time()  # Marca início do processamento
        
        # Carrega os dados do arquivo JSON
        with open(arquivo_json, 'r', encoding='utf-8') as f:
            dados = json.load(f)

        # Índice com contagem (frequência) de termos por documento
        indice = {campo: defaultdict(lambda: defaultdict(int)) for campo in self.campos_indice}

        for doc_id, info in dados.items():
            # Indexa nomes de cidades de origem e destino
            for termo in self.preprocessar_texto(info.get("origem", "")):
                indice["origem"][termo][doc_id] += 1
            for termo in self.preprocessar_texto(info.get("destino", "")):
                indice["destino"][termo][doc_id] += 1

            # Códigos de aeroportos
            if info.get("cod_origem"):
                cod = info["cod_origem"].lower()
                indice["cod_origem"][cod][doc_id] += 1
            if info.get("cod_destino"):
                cod = info["cod_destino"].lower()
                indice["cod_destino"][cod][doc_id] += 1

            for voo in info["voos"]:
                for campo in ["companhia", "escalas", "duracao"]:
                    for termo in self.preprocessar_texto(voo.get(campo, "")):
                        indice[campo][termo][doc_id] += 1
                
                # Preço categorizado
                if "preco" in voo:
                    categoria = self.processar_preco(voo["preco"])
                    indice["preco"][categoria][doc_id] += 1

        os.makedirs(pasta_saida, exist_ok=True)
        path_indice = os.path.join(pasta_saida, 'indice_invertido_por_campo.json')

        # Prepara para salvar: defaultdict -> dict
        indice_serializavel = {
            campo: {
                termo: dict(doc_freq) for termo, doc_freq in termos.items()
            } for campo, termos in indice.items()
        }

        with open(path_indice, 'w', encoding='utf-8') as f:
            json.dump(indice_serializavel, f, ensure_ascii=False, indent=2)

        estatisticas = self._gerar_estatisticas(indice_serializavel, path_indice, inicio)
        path_estat = os.path.join(pasta_saida, 'estatisticas_indexacao.json')

        with open(path_estat, 'w', encoding='utf-8') as f:
            json.dump(estatisticas, f, ensure_ascii=False, indent=2)

        print(f"Índice salvo em {path_indice}")
        print(f"Estatísticas salvas em {path_estat}")
    
    def _gerar_estatisticas(self, indice, path_indice, inicio_tempo):
        """
        Calcula métricas sobre o índice criado
        
        Parâmetros:
            indice (dict): Índice invertido criado
            path_indice (str): Caminho do arquivo de índice
            inicio_tempo (float): Timestamp de início do processamento
            
        Retorna:
            dict: Dicionário com diversas estatísticas
        """
        return {
            "total_termos": sum(len(termos) for termos in indice.values()),
            "total_documentos": len(set( # Coleta todos os documentos únicos presentes no índice
                doc for termos in indice.values()
                for doc_ids in termos.values()
                for doc in doc_ids
            )),
            "tamanho_indice_kb": round(os.path.getsize(path_indice) / 1024, 2),
            "tempo_indexacao_segundos": round(time.time() - inicio_tempo, 3),
            "termos_por_campo": {campo: len(termos) for campo, termos in indice.items()}
        }

if __name__ == "__main__":
    indexador = IndexadorVoos()
    indexador.construir_indice('./02_Representacao/voos_processados.json')