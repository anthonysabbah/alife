from flask import Flask, url_for, send_from_directory
import os
from flask_ngrok import run_with_ngrok
app = Flask(__name__)
root = os.getcwd()
run_with_ngrok(app)   
  
@app.route("/")
def home():
  return send_from_directory("static", "rendered.jpg")
  # p = os.path.join(root, "static/rendered.jpg") 
  # return f'<p><img src="{p}" alt="Dinosaur" /></p>'
    
app.run()