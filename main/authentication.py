from rest_framework import authentication

from .models import CustomToken


class TokenAuthentication(authentication.TokenAuthentication):
    model = CustomToken
