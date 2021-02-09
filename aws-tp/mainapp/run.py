from flask import (Flask, request, render_template)
import requests

app = Flask(__name__)

IP = "localhost"
PORT = 3000

def build_url(route):
    return F"http://{IP}:{PORT}/{route}"

def build_html_url(route, name):
    route = build_url(route)
    return F"<a href={route} target='_blank'>{name}</a>"
    
@app.route("/")
def hello():
    return F"Hello from this super app, list of available routes:<br>{build_html_url('load/s3', 'load data from s3')}" \
                F"<br>{build_html_url('load/rds', 'load data from rds')}" \
                F"<br>{build_html_url('clear', 'clear rds data')}" \
                F"<br>{build_html_url('transfert/rds', 'transfert s3 data to rds')}" 
                
@app.route("/load/s3")
def loadS3():
    return requests.get(url=build_url("/load/s3")).text
    
@app.route("/load/rds")
def loadRDS():
    return requests.get(url=build_url("/load/rds")).text
    
@app.route("/clear")
def clearRDS():
    return requests.get(url=build_url("/clear")).text

@app.route("/transfert/rds")
def transfertToRDS():
    return requests.get(url=build_url("/transfert/rds")).text


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3001)
