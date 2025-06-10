import json
import re
import math
import nltk
from nltk.corpus import stopwords
from nltk.stem import RSLPStemmer
from nltk.tokenize import word_tokenize
from collections import defaultdict

nltk.download('punkt')
nltk.download('stopwords')


class Buscador:
    def __init__(self, caminho_indice):
        with open(caminho_indice, 'r', encoding='utf-8') as f:
            self.indice = json.load(f)

         # Carrega os dados dos voos processados
        with open('./02_Representacao/voos_processados.json', 'r', encoding='utf-8') as f:
            self.voos_processados = json.load(f)

        self.stop_words = set(stopwords.words('portuguese'))
        self.stemmer = RSLPStemmer()
        self.campos = list(self.indice.keys())

        # Número de documentos únicos para cálculo de IDF
        self.doc_count = self.contar_documentos()

        # Pesos por campo
        self.pesos = {
            "origem": 2.0,
            "destino": 2.0,
            "companhia": 1.6,
            "preco": 1.0,
            "escalas": 1.5
        }

    def contar_documentos(self):
        docs = set()
        for campo in self.indice:
            for termo in self.indice[campo]:
                docs.update(self.indice[campo][termo].keys())
        return len(docs)

    def preprocessar_texto(self, texto):
        if not texto:
            return []
        tokens = word_tokenize(texto.lower(), language='portuguese')
        tokens = [re.sub(r'\W+', '', t) for t in tokens if re.match(r'\w+', t)]
        return [self.stemmer.stem(t) for t in tokens if t not in self.stop_words and t != '']

    def buscar(self, consulta_dict):
        pontuacoes = defaultdict(float)

        for campo, texto in consulta_dict.items():
            if campo not in self.indice:
                continue

            termos = self.preprocessar_texto(texto)
            print(termos)
            peso_campo = self.pesos.get(campo, 1.0)

            for termo in termos:
                if termo not in self.indice[campo]:
                    continue

                postings = self.indice[campo][termo]
                df = len(postings)
                idf = math.log((self.doc_count + 1) / (df + 1)
                               ) + 1  # IDF com suavização

                for doc_id, tf in postings.items():
                    # maior tf do termo nesse campo
                    max_tf = max(postings.values())
                    pontuacoes[doc_id] += (tf / max_tf) * idf * peso_campo

        # Resultados ordenados por score decrescente
        resultados_ordenados = dict(
            sorted(pontuacoes.items(), key=lambda x: x[1], reverse=True))

        # Monta resultado com metadados
        resultados_completos = []
        termos_consulta = {
            campo: self.preprocessar_texto(texto)
            for campo, texto in consulta_dict.items()
            if campo in self.pesos
        }

        for doc_id, score in list(resultados_ordenados.items())[:100]:
            metadados = self.voos_processados.get(doc_id)
            if not metadados:
                continue

            voos = metadados.get("voos", [])
            voos_com_scores = []

            for voo in voos:
                score_voo = 0.0
                for campo in ['companhia', 'escalas']:
                    if campo in termos_consulta:
                        texto_voo = str(voo.get(campo, "")).lower()
                        for termo in termos_consulta[campo]:
                            if termo in texto_voo:
                                score_voo += self.pesos.get(campo, 1.0)
                voos_com_scores.append((voo, score_voo))

            # Ordena e pega até 6 voos com maior score
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
