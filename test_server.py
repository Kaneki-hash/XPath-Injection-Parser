# test_server.py
from flask import Flask, request, jsonify, make_response
import xml.etree.ElementTree as ET
from functools import wraps
import logging
import time

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Тестовые данные в XML формате
USERS_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<users>
    <user id="1">
        <username>admin</username>
        <password>admin123</password>
        <role>admin</role>
        <email>admin@example.com</email>
    </user>
    <user id="2">
        <username>user1</username>
        <password>password123</password>
        <role>user</role>
        <email>user1@example.com</email>
    </user>
    <user id="3">
        <username>test</username>
        <password>test123</password>
        <role>user</role>
        <email>test@example.com</email>
    </user>
</users>
'''

def simulate_delay():
    """Симуляция задержки ответа"""
    time.sleep(0.1)

def log_request(f):
    """Декоратор для логирования запросов"""
    @wraps(f)
    def decorated(*args, **kwargs):
        logger.info(f"Request: {request.method} {request.path}")
        logger.info(f"Headers: {dict(request.headers)}")
        logger.info(f"Data: {request.get_data(as_text=True)}")
        return f(*args, **kwargs)
    return decorated

@app.route('/login', methods=['POST'])
@log_request
def login():
    """Эндпоинт для тестирования базовых XPath-инъекций"""
    simulate_delay()
    
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    
    try:
        # Уязвимый XPath-запрос
        xml_root = ET.fromstring(USERS_XML)
        xpath = f".//user[username='{username}' and password='{password}']"
        user = xml_root.find(xpath)
        
        if user is not None:
            return jsonify({
                "status": "success",
                "message": "Login successful",
                "user": {
                    "id": user.get('id'),
                    "role": user.find('role').text
                }
            })
        return jsonify({"status": "error", "message": "Invalid credentials"})
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({"status": "error", "message": "Internal server error"})

@app.route('/user/<user_id>', methods=['GET'])
@log_request
def get_user(user_id):
    """Эндпоинт для тестирования извлечения данных"""
    simulate_delay()
    
    try:
        xml_root = ET.fromstring(USERS_XML)
        user = xml_root.find(f".//user[@id='{user_id}']")
        
        if user is not None:
            return jsonify({
                "id": user.get('id'),
                "username": user.find('username').text,
                "role": user.find('role').text,
                "email": user.find('email').text
            })
        return jsonify({"error": "User not found"}), 404
        
    except Exception as e:
        logger.error(f"Get user error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/users/search', methods=['GET'])
@log_request
def search_users():
    """Эндпоинт для тестирования слепых инъекций"""
    simulate_delay()
    
    role = request.args.get('role', '')
    
    try:
        xml_root = ET.fromstring(USERS_XML)
        xpath = f".//user[role='{role}']"
        users = xml_root.findall(xpath)
        
        return jsonify([{
            "id": user.get('id'),
            "username": user.find('username').text
        } for user in users])
        
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/admin/users', methods=['POST'])
@log_request
def create_user():
    """Эндпоинт для тестирования инъекций в XML"""
    simulate_delay()
    
    try:
        user_xml = request.get_data(as_text=True)
        # Намеренно небезопасный парсинг XML
        ET.fromstring(user_xml)
        return jsonify({"status": "success", "message": "User created"})
        
    except Exception as e:
        logger.error(f"Create user error: {str(e)}")
        return jsonify({"error": str(e)}), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
