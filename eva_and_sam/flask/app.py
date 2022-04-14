import flask
import altair as alt
import pandas as pd

app = flask.Flask(__name__)

@app.route('/')
def index():
    return flask.render_template('index.html')

@app.route('/optim-components')
def components():
    return flask.render_template('optimal_components.html')

@app.route('/pca-2012')
def pcatrain():
    return flask.render_template('pca-2012.html')

@app.route('/pca-2018')
def pcatest():
    return flask.render_template('pca-2018.html')

@app.route('/predictions-2018')
def preds():
    return flask.render_template('predictions-2018.html')

@app.route('/residuals-2012')
def residual():
    return flask.render_template('residuals.html')

@app.route('/model-evaluation')
def eval():
    return flask.render_template('model-evaluation.html')

@app.route('/insights')
def insights():
    return flask.render_template('insights.html')

@app.route('/insights-2')
def insights2():
    return flask.render_template('insights-2.html')


if __name__ == "__main__":
    app.run(port=5000, debug=False)
