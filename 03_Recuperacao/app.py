from flask import Flask, render_template, request, redirect, url_for
from buscador import Buscador

app = Flask(__name__)
buscador = Buscador(
    './02_Representacao/indice/indice_invertido_por_campo.json')


@app.route('/', methods=['GET', 'POST'])
def index():
    resultados = None
    consulta = None
    if request.method == 'POST':
        # Recebe dados do form e redireciona com query string
        return redirect(url_for('index',
                                origem=request.form.get("origem", ""),
                                destino=request.form.get("destino", ""),
                                companhia=request.form.get("companhia", ""),
                                preco=request.form.get("preco", ""),
                                escalas=request.form.get("escalas", "")))
    # Aqui trata o GET com os parâmetros na URL
    consulta = {
        "origem": request.args.get("origem", ""),
        "destino": request.args.get("destino", ""),
        "companhia": request.args.get("companhia", ""),
        "preco": request.args.get("preco", ""),
        "escalas": request.args.get("escalas", "")
    }

    resultados = buscador.buscar(consulta) if any(consulta.values()) else None

    return render_template("index.html", resultados=resultados, consulta=consulta)
@app.route('/documento/<doc_id>')
def documento(doc_id):
    documento = buscador.get_documento_por_id(doc_id)
    if not documento:
        return "Erro no documento."
        #return render_template('404.html'), 404  # você pode criar uma página 404 depois
    return render_template('documento.html', documento=documento)

if __name__ == '__main__':
    app.run(debug=True)
