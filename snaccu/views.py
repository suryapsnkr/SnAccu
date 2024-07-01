from snaccu.models import User, Friend
from django.contrib.auth  import logout
from django.contrib.auth import login as auth_login
from validate_email import validate_email
from django.views.decorators.csrf import csrf_exempt, csrf_protect, ensure_csrf_cookie
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.tokens import default_token_generator
from rest_framework.authtoken.models import Token
from django.conf import settings
from django.db.models.signals import post_save
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from rest_framework.views import APIView
from snaccu.serializers import UserSerializer, CreateUserSerializer, LoginUserSerializer, QuerySerializer, FRSerializer, FASerializer, FListSerializer
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from django.contrib.auth import authenticate
import json

@method_decorator(ensure_csrf_cookie, name='dispatch')
class GetCSRFToken(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        return Response({"Success": "CSRF Cookie Set"})


@method_decorator(csrf_protect, name='dispatch')
class GetUser(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, n):
        if n<=0:
            return Response({"Message": "Negative Indexing is Not Supported"})
        else:    
            users = User.objects.all()[(n-1)*10:n*10]
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data)
    
    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial = True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.error_messages)

@method_decorator(ensure_csrf_cookie, name='dispatch')
class LoginUser(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [AllowAny]
    def post(self, request):
            serializer = LoginUserSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = authenticate(email = serializer.initial_data['email'], password = serializer.initial_data['password'])
            if user is not None:
                auth_login(request, user)
                return Response({'Message': "Login Success"})
            else:
                return Response({'Message': "Invalid Email OR Password"})

@method_decorator(csrf_protect, name='dispatch')
class SignupUser(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = CreateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'Message': 'SignUp Success'})

@method_decorator(csrf_protect, name='dispatch')
class QuerySearch(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated] 
    def get(self, request):
        serializer = QuerySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if validate_email(serializer.initial_data["query"]):
            query= User.objects.filter(email__icontains = serializer.initial_data["query"])
            serializer = UserSerializer(query, many = True)
            return Response(serializer.data)
        else:
            query= User.objects.filter(first_name__icontains = serializer.initial_data["query"])
            serializer = UserSerializer(query, many = True)
            return Response(serializer.data)


@method_decorator(csrf_protect, name='dispatch')
class FriendRequest(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]    
    def post(self, request):
        serializer = FRSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if Friend.objects.filter(fuser = request.user, tuser = request.data['tuser']).exists() or Friend.objects.filter(fuser = request.data['tuser'], tuser = request.user).exists() or request.user.id == request.data['tuser']:
            return Response({'Message': "Request All Ready Exists"})
        elif Friend.objects.filter(fuser = request.user, is_active = True, is_friend = False, created_at__gte=timezone.now() - timedelta(minutes=1)).count()<3:
            Friend.objects.create(fuser = request.user, tuser = User.objects.get(id = request.data["tuser"]))
            return Response({'Message': "Request Send Success"})
        else:
            return Response({'Message': "Three Request Can't Send Within a Minute"})
    

@method_decorator(csrf_protect, name='dispatch')
class FriendAccept(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated] 
    def patch(self, request):
            serializer = FASerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            if Friend.objects.filter(fuser = request.data['fuser'], tuser = request.user.id, is_active = True, is_friend = False).exists():
                r = Friend.objects.get(fuser = request.data['fuser'], tuser = request.user.id)
                r.is_friend = True
                r.save()
                return Response({'Message': 'Request Accept Success'})
            else:
                return Response({'Message': "Request Dosn't Exists OR Request All Ready Accepted"})


@method_decorator(csrf_protect, name='dispatch')
class FriendReject(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated] 
    def patch(self, request):
            serializer = FASerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            if Friend.objects.filter(fuser = request.data['fuser'], tuser = request.user.id, is_active = True, is_friend = False).exists():
                r = Friend.objects.get(fuser = request.data['fuser'], tuser = request.user.id)
                r.is_active = False
                r.save()
                return Response({'Message': 'Request Reject Success'})
            else:
                return Response({'Message': "Request Dosn't Exists OR Request All Ready Rejected"})


class FriendList(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        fr = []
        if Friend.objects.filter(fuser = request.user, is_active = True, is_friend = True).exists():
            f = Friend.objects.filter(fuser = request.user)
            for i in f:
                fr.append(str(i.tuser))
        elif Friend.objects.filter(tuser = request.user, is_active = True, is_friend = True).exists():
            f = Friend.objects.filter(tuser = request.user)
            for i in f:
                fr.append(str(i.fuser))
        return Response({"Friends":fr})

class ChangePassword(APIView):
    def post(self, request):
        cpassword = request.data.get('cpassword')
        npassword = request.data.get('npassword')
        user = request.user
        if not user.check_password(cpassword):
            return Response({'Message': 'Invalid Current Password'})
        user.set_password(npassword)
        user.save()
        return Response({'Message': 'Password Change Successfully'})
    
class LogoutUser(APIView):
    def post(self, request):
        logout(request)
        return Response({'Message': 'Logout Success'})
