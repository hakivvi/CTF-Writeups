from django.shortcuts import render

from django.contrib.auth import get_user_model, authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from .authentication import UserAuthentication, AdminAuthentication
import os.path

from .models import Experience, WebFramework
from .serializers import ExperienceSerializer, WebFrameworkSerializer

User = get_user_model()

class LoginView(APIView):

    def post(self, request):
        data = request.data
        if all(isinstance(data[key], str) for key in ["username", "password"]):
            user = authenticate(request, username=data["username"], password=data["password"])
            if user:
                access_token = AccessToken.for_user(user)
                return Response({
                    "token": str(access_token),
                    "message": "logged in successfully!",
                    "user_id": user.id
                }, status=status.HTTP_200_OK)

        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class WebFrameworks(APIView):
    authentication_classes = APIView.authentication_classes + [UserAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        webframeworks = WebFramework.objects.all()
        serializer = WebFrameworkSerializer(webframeworks, many=True)
        return Response(serializer.data)

class WebFrameworkExperiencesView(APIView):
    authentication_classes =  APIView.authentication_classes + [UserAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        experiences = Experience.objects.all()[:50]
        serializer = ExperienceSerializer(experiences, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ExperienceSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SetHotOfExperienceView(APIView):
    authentication_classes = APIView.authentication_classes + [AdminAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, id, hot):
        print(f"UPDATE {Experience._meta.db_table} SET hot='{hot}' WHERE id = {id}")
        Experience.objects.raw(f"UPDATE {Experience._meta.db_table} SET hot='{hot}' WHERE id = %s", [id])._fetch_all()

        return Response({"message": "OK!"}, status=status.HTTP_200_OK)

class AddWebFrameworkView(APIView):
    authentication_classes = APIView.authentication_classes + [AdminAuthentication]
    permission_classes = [IsAuthenticated]
    LOCATION = "/tmp"

    def post(self, request):
        data = request.data
        if all(isinstance(data[key], str) for key in ["filename", "content"]):
            filename = data["filename"]
            content = data["content"]
            if any(t in filename for t in ["../", "..", "\\", "//", "\\\\", ".py"]):
                return Response({'error': '?'}, status=status.HTTP_400_BAD_REQUEST)
            dir = os.path.dirname(filename)
            if os.path.exists(dir) and dir != AddWebFrameworkView.LOCATION:
                return Response({'error': '?'}, status=status.HTTP_400_BAD_REQUEST)
            with open(os.path.realpath(filename), "w") as f:
                f.write(content)
        return Response({'message': 'OK!'}, status=status.HTTP_201_CREATED)
