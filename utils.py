from flask import jsonify


def format_response(data, status_code=200):
    """Format API response with standard structure."""
    response = {
        'success': True,
        'data': data
    }
    return jsonify(response), status_code


def format_error(message, status_code=400):
    """Format error response with standard structure."""
    response = {
        'success': False,
        'error': message
    }
    return jsonify(response), status_code
