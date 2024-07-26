from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, exceptions
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from .authentication import JWTAuthentication, JWTUtility
from .models import UserToken, Reset
import pytz
import datetime
import random
import string
import certifi
import ssl


class RegisterView(APIView):
    def post(self, request):
        data = request.data
        
        if data['password'] != data['password_confirm']:
            raise exceptions.APIException('Passwords do not match!')
        
        user_serializer = UserSerializer(data=data)
        
        if user_serializer.is_valid():
            if not User.objects.filter(username=data['email']).exists():
                user = User.objects.create(
                    first_name=data['first_name'],
                    last_name=data['last_name'],
                    username=data['email'],
                    email=data['email'],
                    password=make_password(data['password']),
                )
                return Response({'message': 'User registered.', 'data': UserSerializer(user).data}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'User already exists'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(APIView):
    def post(self, request):
        data = request.data
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return Response({'error': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.filter(email=email).first()
        
        if user is None or not user.check_password(password):
            raise exceptions.AuthenticationFailed("Invalid Credentials")
        
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        
        tz = pytz.UTC
        UserToken.objects.create(
            user_id = user.id,
            token = refresh_token,
            expired_at = datetime.datetime.now(tz) + datetime.timedelta(days=7),
        )
        
        response = Response()
        response.set_cookie(
            key='refresh_token', 
            value=refresh_token, 
            httponly=True, 
            secure=True,  # Use secure=True in production
            samesite='Lax'
        )
        response.data = {
            'access_token': access_token,
        }
        
        return response



class UserAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        user = request.user

        user_data = {
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
        }
        
        return Response(user_data, status=status.HTTP_200_OK)


class RefreshAPIView(APIView):
    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        
        if not refresh_token:
            raise exceptions.AuthenticationFailed('Refresh token not found')
        
        id = JWTUtility.decode_refresh_token(refresh_token)
        
        if not UserToken.objects.filter(
            user_id = id,
            token = refresh_token,
            expired_at__gt = datetime.datetime.now(tz=datetime.timezone.utc),
        ).exists():
            raise exceptions.AuthenticationFailed("unauthenticated")
        
        access_token = JWTUtility.create_access_token(id)
        
        response = Response()
        
        response.data = {
            'access_token': access_token,
        }
        
        return Response(response.data)

class LogoutAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    
    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        
        UserToken.objects.filter(token=refresh_token).delete()
        response =  Response()
        response.delete_cookie(key='refresh_token')
        response.data = {
            'message' : 'success'
        }
        return response
    
class ForgotAPIView(APIView):
    def post(self, request):
        email = request.data['email']
        token = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))
        
        Reset.objects.create(
            email=email,
            token=token,
        )
        
        url = f'http://localhost:3000/reset/{token}'
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        send_mail(
            subject='Reset your password',
            message=f'Click <a href="{url}">here</a> to reset your password.',
            from_email='from@example.com',
            recipient_list=[email],
            html_message=f'Click <a href="{url}">here</a> to reset your password.'
        )
        
        return Response({
            'message': 'success'
        })
        
class ResetAPIView(APIView):
    def post(self, request):
        data = request.data
        
        if data['password'] != data['password_confirm']:
            raise exceptions.APIException('Passwords do not match!')
        
        reset_password = Reset.objects.filter(token=data['token']).first()
        
        if not reset_password:
            raise exceptions.APIException('Invalid link!')

        user = User.objects.filter(email=reset_password.email).first()
        
        if not user:
            raise exceptions.APIException('User was not found')
        
        user.set_password(data['password'])
        user.save()
        
        return Response({
            'message': 'success'
        })