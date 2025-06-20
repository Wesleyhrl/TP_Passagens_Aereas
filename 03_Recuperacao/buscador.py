import json
import re
import math
import nltk
from nltk.corpus import stopwords
from nltk.stem import RSLPStemmer
from nltk.tokenize import word_tokenize
from collections import defaultdict

# Baixa recursos necessários do NLTK
nltk.download('punkt')
nltk.download('stopwords')

class Buscador:
    def __init__(self, caminho_indice):
        """Inicializa o buscador carregando o índice invertido e dados processados"""
        with open(caminho_indice, 'r', encoding='utf-8') as f:
            self.indice = json.load(f)

        # Carrega os dados dos voos processados
        with open('./02_Representacao/voos_processados.json', 'r', encoding='utf-8') as f:
            self.voos_processados = json.load(f)

        # Configurações para pré-processamento de texto
        self.stop_words = set(stopwords.words('portuguese'))
        self.stemmer = RSLPStemmer()
        self.campos = list(self.indice.keys())

        # Número de documentos únicos para cálculo de IDF
        self.doc_count = self.contar_documentos()

        # Pesos por campo para cálculo de relevância
        self.pesos = {
            "origem": 2.0,    # Maior peso para origem/destino
            "destino": 2.0,
            "companhia": 1.6, # Peso intermediário para companhia
            "preco": 1.0,     # Menor peso para preço
            "escalas": 1.5    # Peso intermediário para escalas
        }

    def contar_documentos(self):
        """Calcula o número total de documentos únicos no índice"""
        docs = set()
        for campo in self.indice:
            for termo in self.indice[campo]:
                docs.update(self.indice[campo][termo].keys())
        return len(docs)

    def preprocessar_texto(self, texto):
        """Realiza pré-processamento do texto: tokenização, limpeza e stemming"""
        if not texto:
            return []
            
        # Tokenização e normalização
        tokens = word_tokenize(texto.lower(), language='portuguese')
        
        # Remove caracteres não alfanuméricos
        tokens = [re.sub(r'\W+', '', t) for t in tokens if re.match(r'\w+', t)]
        
        # Stemming e remoção de stopwords
        return [self.stemmer.stem(t) for t in tokens if t not in self.stop_words and t != '']

    def buscar(self, consulta_dict):
        """Executa a busca com base nos parâmetros da consulta"""
        pontuacoes = defaultdict(float)  # Armazena scores dos documentos

        for campo, texto in consulta_dict.items():
            if campo not in self.indice:
                continue

            # Pré-processa os termos da consulta
            termos = self.preprocessar_texto(texto)
            peso_campo = self.pesos.get(campo, 1.0)

            for termo in termos:
                if termo not in self.indice[campo]:
                    continue

                postings = self.indice[campo][termo]
                df = len(postings)  # Document frequency
                
                # IDF com suavização para evitar divisão por zero
                idf = math.log((self.doc_count + 1) / (df + 1)) + 1

                # Calcula TF-IDF para cada documento que contém o termo
                for doc_id, tf in postings.items():
                    # Normaliza TF pelo máximo no campo
                    max_tf = max(postings.values())
                    # Calcula a pontuação (score) do documento para o termo atual
                    pontuacoes[doc_id] += (tf / max_tf) * idf * peso_campo

        # Ordena resultados por score decrescente
        resultados_ordenados = dict(
            sorted(pontuacoes.items(), key=lambda x: x[1], reverse=True))

        # Prepara termos da consulta para highlight(destaque) nos resultados
        termos_consulta = {
            campo: self.preprocessar_texto(texto)
            for campo, texto in consulta_dict.items()
            if campo in self.pesos
        }

        # Monta resposta final com metadados
        resultados_completos = []
        for doc_id, score in list(resultados_ordenados.items())[:100]:  # Limita a 100 resultados
            metadados = self.voos_processados.get(doc_id)
            if not metadados:
                continue

            # Calcula relevância dos voos individuais
            voos = metadados.get("voos", [])
            voos_com_scores = []
            
            for voo in voos:
                score_voo = 0.0
                for campo in ['companhia', 'escalas']:  # Campos para highlight(destaque)
                    if campo in termos_consulta:
                        texto_voo = str(voo.get(campo, "")).lower()
                        for termo in termos_consulta[campo]:
                            if termo in texto_voo:
                                score_voo += self.pesos.get(campo, 1.0)
                voos_com_scores.append((voo, score_voo))

            # Seleciona os voos mais relevantes (até 6)
            voos_relevantes = [v for v, _ in sorted(
                voos_com_scores, key=lambda x: x[1], reverse=True)[:6]]

            resultados_completos.append({
                "doc_id": doc_id,
                "score": round(score, 2),
                "origem": metadados.get("origem"),
                "destino": metadados.get("destino"),
                "data": metadados.get("data"),
                "total_voos": metadados.get("total_voos"),
                "voos": voos_relevantes
            })

        return resultados_completos

    def get_documento_por_id(self, doc_id):
        """Recupera um documento completo pelo seu ID"""
        metadados = self.voos_processados.get(doc_id)
        if not metadados:
            return None
        return {
            "doc_id": doc_id,
            "cod_origem": metadados.get("cod_origem"),
            "cod_destino": metadados.get("cod_destino"),
            "origem": metadados.get("origem"),
            "destino": metadados.get("destino"),
            "data": metadados.get("data"),
            "total_voos": metadados.get("total_voos"),
            "voos": metadados.get("voos", [])
        }
    
    def calcular_estatisticas_documento(self, doc_id):
        """Calcula estatísticas avançadas para um documento específico"""
        documento = self.get_documento_por_id(doc_id)
        if not documento or not documento.get("voos"):
            return None

        voos = documento["voos"]
        
        # Pré-processamento dos dados dos voos
        voos_processados = []
        for voo in voos:
            try:
                # Converte preço para float
                preco = float(voo["preco"].replace("R$", "").replace(".", "").replace(",", "."))
                
                # Converte duração para minutos
                duracao = 0
                if "h" in voo["duracao"]:
                    horas, minutos = voo["duracao"].split("h")
                    duracao = int(horas) * 60
                    if minutos:
                        duracao += int(minutos.replace("m", ""))
                
                # Processa número de escalas
                escalas = 0
                if "Sem_escalas" in voo["escalas"]:
                    escalas = 0
                elif "_parada" in voo["escalas"]:
                    escalas = int(voo["escalas"].split("_")[0])
                
                voos_processados.append({
                    **voo,  # Mantém todos os dados originais
                    "preco_float": preco,          # Preço como float
                    "duracao_minutos": duracao,    # Duração em minutos
                    "num_escalas": escalas         # Número de escalas como int
                })
            except (ValueError, AttributeError):
                continue  # Ignora voos com formato inválido
        
        if not voos_processados:
            return None

        # Cálculo de estatísticas básicas
        precos = [v["preco_float"] for v in voos_processados]
        duracoes = [v["duracao_minutos"] for v in voos_processados]
        companhias = [v["companhia"] for v in voos_processados]
        
        estatisticas = {
            "total_voos": len(voos_processados),
            "preco_medio": round(sum(precos) / len(precos), 2),
            "preco_min": min(precos),
            "preco_max": max(precos),
            "duracao_media": round(sum(duracoes) / len(duracoes)),
            "duracao_min": min(duracoes),
            "duracao_max": max(duracoes),
            "companhias_disponiveis": list(set(companhias)),
            "voos_por_companhia": {},
            "melhor_custo_beneficio": [],
            "voos_mais_baratos": [],
            "voos_mais_rapidos": [],
            "voos_sem_escalas": []
        }

        # Estatísticas por companhia aérea
        for companhia in estatisticas["companhias_disponiveis"]:
            voos_companhia = [v for v in voos_processados if v["companhia"] == companhia]
            precos_companhia = [v["preco_float"] for v in voos_companhia]
            
            estatisticas["voos_por_companhia"][companhia] = {
                "quantidade": len(voos_companhia),
                "preco_medio": round(sum(precos_companhia) / len(precos_companhia), 2),
                "preco_min": min(precos_companhia),
                "preco_max": max(precos_companhia)
            }

        # Cálculo de custo-benefício(custo-tempo) (preço por minuto)
        for voo in voos_processados:
            if voo["duracao_minutos"] > 0:
                custo_beneficio = voo["preco_float"] / voo["duracao_minutos"]
            else:
                custo_beneficio = float('inf')
            
            estatisticas["melhor_custo_beneficio"].append({
                **{k: v for k, v in voo.items() if k not in ["preco_float", "duracao_minutos", "num_escalas"]},
                "custo_beneficio": round(custo_beneficio, 4)
            })
        
        # Ordenações diversas
        estatisticas["melhor_custo_beneficio"].sort(key=lambda x: x["custo_beneficio"])
        estatisticas["voos_mais_baratos"] = sorted(voos_processados, key=lambda x: x["preco_float"])[:10]
        estatisticas["voos_mais_rapidos"] = sorted(voos_processados, key=lambda x: x["duracao_minutos"])[:10]
        estatisticas["voos_sem_escalas"] = [v for v in voos_processados if v["num_escalas"] == 0]

        # Função auxiliar para formatação de exibição
        def formatar_voo(voo):
            formatted = {**voo}
            if "preco_float" in formatted:
                formatted["preco"] = f"R${formatted['preco_float']:,.2f}".replace(".", ",").replace(",", ".", 1)
            if "duracao_minutos" in formatted:
                horas = formatted["duracao_minutos"] // 60
                minutos = formatted["duracao_minutos"] % 60
                formatted["duracao"] = f"{horas}h{minutos:02d}m" if minutos else f"{horas}h"
            return formatted

        # Aplica formatação aos resultados
        for key in ["melhor_custo_beneficio", "voos_mais_baratos", "voos_mais_rapidos", "voos_sem_escalas"]:
            estatisticas[key] = [formatar_voo(v) for v in estatisticas[key]]

        return estatisticas