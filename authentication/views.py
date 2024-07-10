# 데이터 처리
from .serializers import *

# APIView 사용
from rest_framework.views import APIView

# Response 관련
from rest_framework import status
from rest_framework.response import Response

# 인증 관련
from rest_framework import permissions
from django.contrib.auth import authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication


# 회원가입 view
class SignupAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            
            res = Response(
                {
                    "user": serializer.data,
                    "message": "회원가입 완료",
                },
                status=status.HTTP_200_OK
            )
            return res
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
# 로그인 view
class LoginAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        user = authenticate(
            email = request.data.get("email"),
            password = request.data.get("password"),
        )
        
        if user is not None:
            serializer = UserSerializer(user)
            
            token = TokenObtainPairSerializer.get_token(user)
            access_token = str(token.access_token)
            
            res = Response(
                {
                    "email": serializer.data['email'],
                    "user_name": serializer.data['user_name'],
                    "token": {
                        "access": access_token
                    },
                },
                status=status.HTTP_200_OK
            )
            res.set_cookie("access", access_token, httponly=True)
            return res
        else:
            return Response(
                {
                    "message": "아이디가 존재하지 않거나, 비밀번호가 올바르지 않습니다."
                },
                status=status.HTTP_400_BAD_REQUEST
            )
            
            
# 로그아웃
class LogoutAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    # 로그아웃
    def delete(self, request):
        # 쿠키에 저장된 토큰 삭제 -> 로그아웃
        res = Response(
            {
                "message": "로그아웃되었습니다."
            },
            status=status.HTTP_202_ACCEPTED
        )
        res.delete_cookie("access")
        return res