from flask import Flask

__all__ = ['app']

app = Flask(__name__)


@app.route('/')
def index():
    return '<h2>Welcome to Cookie Pool System</h2>'


@app.route('/getCode')
def getCode():
    return parseCOde()


if __name__ == '__main__':
    app.run()
