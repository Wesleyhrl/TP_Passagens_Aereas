import json
import re
import os
import time
from collections import defaultdict
from nltk.corpus import stopwords
from nltk.stem import RSLPStemmer
from nltk.tokenize import word_tokenize
import nltk

# Configurações iniciais (executa apenas na primeira vez)
nltk.download('punkt')
nltk.download('stopwords')

class IndexadorVoos:
    def __init__(self):
        self.stop_words = set(stopwords.words('portuguese'))
        self.stemmer = RSLPStemmer()
        self.campos_indice = ["companhia", "escalas", "duracao", "origem", "destino", "preco"]
    
    def preprocessar_texto(self, texto):
        """Limpa, tokeniza e aplica stemming no texto"""
        if not texto:
            return []
            
        tokens = word_tokenize(texto.lower(), language='portuguese')
        tokens = [re.sub(r'\W+', '', t) for t in tokens if re.match(r'\w+', t)]
        return [self.stemmer.stem(t) for t in tokens if t not in self.stop_words and t != '']
    
    def processar_preco(self, preco_str):
        """Converte e classifica o preço em categorias"""
        try:
            valor = float(re.sub(r'[^\d,]', '', preco_str).replace(',', '.'))
        except:
            return "p_nd"
        
        if valor <= 500: return "p_0_500"
        if valor <= 1000: return "p_501_1000"
        if valor <= 2000: return "p_1001_2000"
        return "p_2000+"
    
    def construir_indice(self, arquivo_json, pasta_saida='./02_Representacao/indice'):
        """Método principal que constrói e salva o índice"""
        inicio = time.time()
        
        # Carrega os dados
        with open(arquivo_json, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        
        # Inicializa estrutura do índice
        indice = {campo: defaultdict(set) for campo in self.campos_indice}
        
        # Processa cada documento
        for doc_id, info in dados.items():
            # Origem e destino (sem pré-processamento)
            if info.get("origem"):
                indice["origem"][info["origem"].lower()].add(doc_id)
            if info.get("destino"):
                indice["destino"][info["destino"].lower()].add(doc_id)
            
            # Processa cada voo do documento
            for voo in info["voos"]:
                # Campos textuais (companhia, escalas, duração)
                for campo in ["companhia", "escalas", "duracao"]:
                    for termo in self.preprocessar_texto(voo.get(campo, "")):
                        indice[campo][termo].add(doc_id)
                
                # Campo de preço (tratamento especial)
                if "preco" in voo:
                    categoria = self.processar_preco(voo["preco"])
                    indice["preco"][categoria].add(doc_id)
        
        # Salva o índice
        os.makedirs(pasta_saida, exist_ok=True)
        path_indice = os.path.join(pasta_saida, 'indice_invertido_por_campo.json')
        
        indice_serializavel = {
            campo: {termo: list(docs) for termo, docs in termos.items()}
            for campo, termos in indice.items()
        }
        
        with open(path_indice, 'w', encoding='utf-8') as f:
            json.dump(indice_serializavel, f, ensure_ascii=False, indent=2)
        
        # Gera e salva estatísticas
        estatisticas = self._gerar_estatisticas(indice_serializavel, path_indice, inicio)
        path_estat = os.path.join(pasta_saida, 'estatisticas_indexacao.json')
        
        with open(path_estat, 'w', encoding='utf-8') as f:
            json.dump(estatisticas, f, ensure_ascii=False, indent=2)
        
        print(f"Índice salvo em {path_indice}")
        print(f"Estatísticas salvas em {path_estat}")
    
    def _gerar_estatisticas(self, indice, path_indice, inicio_tempo):
        """Calcula métricas sobre o índice criado"""
        return {
            "total_termos": sum(len(termos) for termos in indice.values()),
            "total_documentos": len(set(
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