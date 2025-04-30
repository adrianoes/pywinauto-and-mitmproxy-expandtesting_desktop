from mitmproxy import http

def response(flow: http.HTTPFlow) -> None:
    # Lista de endpoints a mockar com erro 500
    endpoints = [
        "/notes/api/health-check",
        "/notes/api/users/login",
        "/notes/api/users/register",
        "/notes/api/users/profile",
        "/notes/api/users/logout",
        "/notes/api/users/change-password",
        "/notes/api/users/delete-account",
        "/notes/api/notes",
        "/notes/api/notes/"  # necessário para requests com ID no final
    ]

    if any(endpoint in flow.request.pretty_url for endpoint in endpoints):
        flow.response = http.Response.make(
            500,
            b'{"success": false, "status": 500, "message": "Internal Error Server"}',
            {"Content-Type": "application/json"}
        )
