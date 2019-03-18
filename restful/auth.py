from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework.authentication import get_authorization_header, BaseAuthentication
from rest_framework import exceptions, status
from rest_framework.response import Response
from hashlib import sha256
from hmac import HMAC
import jwt

SALT = 'MINESWEEPER'


class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        try:
            jwt_token = self.check_token_in_header(request)
  
            if jwt_token:
                payload = jwt.decode(jwt_token, SALT)
                userid = payload['id']
                user = User.objects.get(pk=userid)
            else:
                return (None, None)

        except jwt.ExpiredSignature or jwt.DecodeError or jwt.InvalidTokenError:
            return (None, None)

        except User.DoesNotExist:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return (user, jwt_token)

    def check_token_in_header(self, request):
        token = get_authorization_header(request).split()
        print(token)
        if (not token) or (token[0] != b'Bearer') or (not token[1]):
            return False
        # return the jwt
        return token[1]

    def authenticate_header(self, request):
        return 'Bearer'

    # todo: token refresh


def hash_password(password, salt='mine1234'):
    print('password', password)
    password = password.encode('utf-8')
    print('password', password)
    result = HMAC(password, salt, sha256).digest()

    return salt + result


def valid_password(hashed, input_password):
    return hashed == hash_password(input_password, salt=hashed[:8])


def create_jwt(user):
    return jwt.encode(user, SALT)
