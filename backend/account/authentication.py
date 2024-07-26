from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework import exceptions
from django.contrib.auth.models import User
from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from django.contrib.auth.models import User

class JWTUtility:

    @staticmethod
    def create_access_token(user_id):
        access_token = AccessToken()
        access_token['user_id'] = user_id
        return str(access_token)
    
    @staticmethod
    def create_refresh_token(user_id):
        refresh_token = RefreshToken()
        refresh_token['user_id'] = user_id
        return str(refresh_token)
    
    @staticmethod
    def decode_access_token(token):
        try:
            decoded_token = AccessToken(token)
            user_id = decoded_token['user_id']
            return user_id
        except TokenError as e:
            raise exceptions.AuthenticationFailed(f'Invalid token: {str(e)}')
        
    @staticmethod
    def decode_refresh_token(token):
        try:
            decoded_token = RefreshToken(token)
            user_id = decoded_token['user_id']
            return user_id
        except TokenError as e:
            raise exceptions.AuthenticationFailed(f'Invalid refresh token: {str(e)}')

    @staticmethod
    def get_user_from_token(token):
        try:
            user_id = JWTUtility.decode_access_token(token)
            user = User.objects.get(pk=user_id)
            return user
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('User not found')


class JWTAuthentication(BaseAuthentication):

    def authenticate(self, request):
        auth_header = request.headers.get('Authorization', None)
        
        if not auth_header or not auth_header.startswith('Bearer '):
            raise exceptions.AuthenticationFailed('Authorization header must start with Bearer')

        token = auth_header.split()[1]

        try:
            user = JWTUtility.get_user_from_token(token)
            return (user, token)
        except exceptions.AuthenticationFailed as e:
            raise e  # Pass on the exception from decode_token
        except Exception as e:
            raise exceptions.AuthenticationFailed(f'An error occurred: {str(e)}')
