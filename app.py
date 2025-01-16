from flask import Flask
from app2 import ocr_blueprint

app = Flask(__name__)
app.register_blueprint(ocr_blueprint, url_prefix='/ocr')

if __name__ == '__main__':
    app.run(debug=True, port=8888)
