from functools import wraps
from flask import request, url_for
from jose import jwt
import requests
from constants import *

user_id = None


def get_user_id():
    return user_id

## AuthError Exception
class AuthError(Exception):
    """
    AuthError Exception
    A standardized way to communicate auth failure modes
    """

    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code

def get_login_url():
    """
        Returns the auh0 login page url
    """
    return f"""https://{AUTH0_DOMAIN}/authorize?"
            &response_type=code
            &client_id={CLIENT_ID}
            &redirect_uri={url_for(CALLBACK_ENDPOINT, _external=True, _scheme='http')}
            &scope=openid
            &audience={API_AUDIENCE}""".replace("\n","").replace(" ", "")

def get_token_from_code(code):
    data = {"grant_type": "authorization_code",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": code,
            "redirect_uri": url_for(CALLBACK_ENDPOINT, _external=True, _scheme='http')}
    
    headers = {"content-type": "application/x-www-form-urlencoded"}
    
    resp = requests.post(f"https://{AUTH0_DOMAIN}/oauth/token", data=data, headers=headers, timeout=3)
    if resp.status_code == 403:
        raise AuthError({
            "code": "invalid_grant",
            "description": "Invalid authorization code"}, resp.status_code)
    
    token = resp.json().get("access_token") 
    resp.close()
    return token

## Auth Header

def get_token_auth_header():
    """
        Returns the bearer token from the request header
    """
    auth = request.headers.get("Authorization", None)
    if not auth:
        raise AuthError({
            "code": "authorization_header_missing",
            "description": "Authorization header is expected"}, 401)

    auth = auth.split()
    if len(auth) <= 1:
        raise AuthError({
            "code": "invalid_authorization_header",
            "description": "Token not found"}, 401)
    elif len(auth) > 2:
        raise AuthError({
            "code": "invalid_authorization_header",
            "description": "Authorization header must be bearer token"}, 401)
    if auth[0].lower() != "bearer":
        raise AuthError({
            "code": "invalid_authorization_header",
            "description": "Authorization header must start with \"Bearer\""}, 401)

    # If all checks passed return token
    return auth[1]

def verify_decode_jwt(token):
    jsonurl = requests.get(f"https://{AUTH0_DOMAIN}/.well-known/jwks.json", timeout=3)
    jwks = jsonurl.json()
    try:
        unverified_header = jwt.get_unverified_header(token)
    except:
        raise AuthError({
            "code": "invalid_header",
            "description": "Error decoding token headers"
        }, 401)
    rsa_key = {}
    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )

            return payload

        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Please, check the audience and issuer.'
            }, 401)
        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)
    raise AuthError({
        'code': 'invalid_header',
        'description': 'Unable to find the appropriate key.'
    }, 400)

def check_permissions(permission, payload):
    if permission not in payload.get("permissions", ""):
        raise AuthError({
            "code": "forbidden",
            "description": "Missing required permissions"}, 403)

def requires_auth(permission=""):
  def requires_auth_decorator(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = get_token_auth_header()
        payload = verify_decode_jwt(token)
        
        if permission:
            check_permissions(permission, payload)
        
        global user_id
        user_id=payload["sub"]
        return f(*args, **kwargs)
    
    return wrapper
  return requires_auth_decorator
