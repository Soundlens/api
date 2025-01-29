from functools import wraps
from flask import request, jsonify
from .api_key_service import ApiKeyService

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            return jsonify({
                'error': 'No API key provided',
                'message': 'Please provide your API key in the X-API-Key header'
            }), 401

        if not ApiKeyService.validate_key(api_key):
            return jsonify({
                'error': 'Invalid API key',
                'message': 'The provided API key is invalid or inactive'
            }), 403

        return f(*args, **kwargs)
    return decorated_function 