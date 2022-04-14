import flask
import altair as alt
from vega_datasets import data
import pandas as pd

app = flask.Flask(__name__)

df = pd.DataFrame({'A': [0, 1, 2, 3, 4],
                   'B': [5, 6, 7, 8, 9],
                   'C': ['a', 'b', 'c--', 'd', 'e']})

def get_pca_charts():
    # ideally you pull these from the database, but for now they're hard coded
    pca_charts = [
        {"filename": "2012PCA_scatter_plot.html", "year": "2012"},
        {"filename": "2018PCA_scatter_plot.html", "year": "2018"},
    ]
    return pca_charts

@app.route('/')
def index():
     # the list to be rendered into the template
    return flask.render_template('index.html')
    # key is charts (referred to in the template), value is charts items from get_charts() function

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

# @app.route('/table')
# def html_table():
#     return flask.render_template('table.html',  tables=[df.to_html(classes='data', index=False)], titles=df.columns.values)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
