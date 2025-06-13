from flask import Flask, render_template, request, redirect, url_for
from buscador import Buscador

# Cria a aplicação Flask
app = Flask(__name__)

# classe Buscador responsável pela lógica de recuperação
# Instancia o buscador com o caminho do índice invertido
buscador = Buscador('./02_Representacao/indice/indice_invertido_por_campo.json')


@app.route('/', methods=['GET', 'POST'])
def index():
    resultados = None 
    consulta = None    

    if request.method == 'POST':
        # Quando o formulário é submetido via POST, redireciona para GET usando query string
        return redirect(url_for(
            'index',
            origem=request.form.get("origem", ""),
            destino=request.form.get("destino", ""),
            cod_origem=request.form.get("cod_origem", ""),
            cod_destino=request.form.get("cod_destino", ""),
            companhia=request.form.get("companhia", ""),
            preco=request.form.get("preco", ""),
            escalas=request.form.get("escalas", "")
        ))

    # Quando o método é GET ler os parâmetros da URL
    consulta = {
        "origem": request.args.get("origem", ""),
        "destino": request.args.get("destino", ""),
        "cod_origem": request.args.get("cod_origem", ""),
        "cod_destino": request.args.get("cod_destino", ""),
        "companhia": request.args.get("companhia", ""),
        "preco": request.args.get("preco", ""),
        "escalas": request.args.get("escalas", "")
    }

    # Só realiza a busca se houver ao menos um campo preenchido
    resultados = buscador.buscar(consulta) if any(consulta.values()) else None

    # Renderiza a página principal com os resultados
    return render_template("index.html", resultados=resultados, consulta=consulta)


@app.route('/documento/<doc_id>')
def documento(doc_id):
    # Busca um documento individual pelo ID
    documento = buscador.get_documento_por_id(doc_id)
    if not documento:
        return "Erro no documento."

    # Renderiza a página com os detalhes do documento
    return render_template('documento.html', documento=documento)


@app.route('/documento/<doc_id>/estatisticas')
def estatisticas_documento(doc_id):
    # Recupera o documento e valida sua existência
    documento = buscador.get_documento_por_id(doc_id)
    if not documento:
        return "Documento não encontrado.", 404

    # Calcula estatísticas específicas do documento
    estatisticas = buscador.calcular_estatisticas_documento(doc_id)

    # Renderiza a página com as estatísticas do voo/documento
    return render_template(
        'estatisticas.html',
        documento=documento,
        estatisticas=estatisticas
    )

if __name__ == '__main__':
    app.run(debug=True)
