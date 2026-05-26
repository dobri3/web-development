from flask import jsonify


def success_response(data=None, status_code=200):
    body = {"success": True}
    if data is not None:
        body["data"] = data
    return jsonify(body), status_code


def error_response(code: str, detail, status_code: int):
    return jsonify({
        "success": False,
        "error": {
            "code": code,
            "detail": detail,
            "status_code": status_code,
        },
    }), status_code