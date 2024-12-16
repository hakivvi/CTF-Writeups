from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.settings import api_settings
from django.contrib.auth import get_user_model

User = get_user_model()

class UserAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.headers.get('Token')
        if not token:
            raise AuthenticationFailed('Authentication credentials were not provided.', code=401)

        try:
            token = token.split("Bearer ")[1]
            access_token = AccessToken(token)
            
            access_token.verify()
            
            user_id = access_token[api_settings.USER_ID_CLAIM]
            user = User.objects.get(id=user_id)
            
            return (user, access_token)
        
        except TokenError as e:
            raise AuthenticationFailed(f'Invalid token: {str(e)}', code=401)
        except User.DoesNotExist:
            raise AuthenticationFailed('User not found.', code=404)
        except Exception as e:
            AuthenticationFailed('Authentication credentials were not provided.', code=401)

class AdminAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.headers.get('Token')
        if not token:
            raise AuthenticationFailed('Authentication credentials were not provided.', code=401)
        
        try:
            token = token.split("Bearer ")[1]
            access_token = AccessToken(token)
            
            access_token.verify()
            
            user_id = access_token[api_settings.USER_ID_CLAIM]
            user = User.objects.get(id=user_id)
            
            if not user.is_admin:
                raise AuthenticationFailed(f'You are not an admin.', code=401)
            return (user, access_token)
        
        except TokenError as e:
            raise AuthenticationFailed(f'Invalid token: {str(e)}', code=401)
        except User.DoesNotExist:
            raise AuthenticationFailed('User not found.', code=404)
        except Exception as e:
            AuthenticationFailed('Authentication credentials were not provided.', code=401)

