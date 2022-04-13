import flask
import altair as alt
from vega_datasets import data
import pandas as pd

app = flask.Flask(__name__)

df = pd.DataFrame({'A': [0, 1, 2, 3, 4],
                   'B': [5, 6, 7, 8, 9],
                   'C': ['a', 'b', 'c--', 'd', 'e']})

def get_charts():
    # ideally you pull these from the database, but for now they're hard coded
    charts = [
        {"name": "chart1", "type": "scatter plot"},
        {"name": "chart2", "type": "histogram"},
        {"name": "chart3", "type": "bar plot"}
    ]
    return charts

@app.route('/')
def index():
    charts = get_charts() # the list to be rendered into the template
    return flask.render_template('index.html', charts=charts)
    # key is charts (referred to in the template), value is charts items from get_charts() function

# @app.route('/about')
# def about():
#     return flask.render_template('about.html')

@app.route('/pca')
def charts():
    return flask.render_template('pca.html')

# @app.route('/table')
# def html_table():
#     return flask.render_template('table.html',  tables=[df.to_html(classes='data', index=False)], titles=df.columns.values)

if __name__ == "__main__":
    app.run(port=5000, debug=True)