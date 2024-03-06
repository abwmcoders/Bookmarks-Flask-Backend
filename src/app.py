from flask import Flask, jsonify

app = Flask(__name__)

if __name__ == "__main":
    app.run(debug=True)