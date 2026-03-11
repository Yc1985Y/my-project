from flask import Flask, jsonify, request
from config import Config
from utils import format_response

app = Flask(__name__)
app.config.from_object(Config)


@app.route('/')
def index():
    return format_response({'message': 'Welcome to Flask App!'})


@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username', '')
    password = data.get('password', '')
    
    if username == 'admin' and password == '123456':
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': {'username': username}
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Invalid username or password'
        }), 401


if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'], host=app.config['HOST'], port=app.config['PORT'])
