from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .serializers import RegistrationSerializer, LoginSerializer, ConfirmationSerializer
from .google_oauth import get_google_user_info, get_or_create_user, generate_jwt_for_user
from rest_framework.views import APIView


class RegistrationView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key}, status=status.HTTP_200_OK)


class ConfirmationView(generics.GenericAPIView):
    serializer_class = ConfirmationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        user.is_active = True
        user.save()
        return Response({"message": "Пользователь активирован"}, status=status.HTTP_200_OK)


class GoogleAuthView(APIView):
    def post(self, request):
        code = request.data.get("code")
        redirect_uri = request.data.get("redirect_uri")
        if not code or not redirect_uri:
            return Response({"error": "Не передан код или redirect_uri"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            google_user = get_google_user_info(code, redirect_uri)
            user = get_or_create_user(google_user)
            token = generate_jwt_for_user(user)
            return Response(token, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
