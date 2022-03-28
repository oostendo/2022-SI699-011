import flask

app = flask.Flask(__name__)

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
    return flask.render_templates('index.html', charts=charts)
    # key is charts (referred to in the template), value is charts items from get_charts() function

@app.route('/about')
def about():
    return flask.render_templates('about.html')

if __name__ == "__main__":
    app.run(debug=True)