from flask import Flask, send_from_directory
import os

app = Flask(__name__)

@app.route('/show')
def show():
    return send_from_directory("templates", "show.html")


@app.route("/")
def home():
    return send_from_directory("templates", "index.html")

if __name__ == "__main__":
    app.run(debug=True)
