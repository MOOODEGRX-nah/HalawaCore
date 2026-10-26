import hmac
import re

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class LocalSecurity(BaseHTTPMiddleware):
    def __init__(self, app, token):
        super().__init__(app)
        self.token = token

    async def dispatch(self, request, call_next):
        host = request.headers.get('host', '')
        if not re.fullmatch(r'(127\.0\.0\.1|localhost)(:[0-9]{1,5})?', host):
            return JSONResponse({'error': {'message': 'Only a loopback Host is accepted.'}}, 403)
        if request.headers.get('sec-fetch-site') == 'cross-site':
            return JSONResponse({'error': {'message': 'Cross-site requests are blocked.'}}, 403)
        if request.method not in ('GET', 'HEAD', 'OPTIONS'):
            origin = request.headers.get('origin')
            if origin != f'http://{host}':
                return JSONResponse({'error': {'message': 'A matching local Origin is required.'}}, 403)
            token = request.headers.get('x-halawacore-token', '')
            if not hmac.compare_digest(token.encode(), self.token.encode()):
                return JSONResponse({'error': {'message': 'Local session token is missing or invalid.'}}, 403)
            body = await request.body()
            if len(body) > 131072:
                return JSONResponse({'error': {'message': 'Request is too large.'}}, 413)
        response = await call_next(request)
        response.headers.update({
            'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff',
            'Referrer-Policy': 'no-referrer', 'X-Frame-Options': 'DENY',
            'Content-Security-Policy': "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' blob: data:; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'",
        })
        return response
