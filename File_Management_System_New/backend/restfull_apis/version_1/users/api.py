from django.http import JsonResponse
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status as http_status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework import status
from django.conf import settings

from .serializer import (UserDetailSerializers, UserUpdateSerializers,ChangePasswordSerializer,)
from users.models import User
from .serializer import UserLoginSerializer
from django.contrib.auth import authenticate
from restfull_apis.version_0.permissions.guest import IsTrustedGuest
from django.contrib.auth import  login,logout
from .serializer import *
from rest_framework.views import APIView
from .serializer import SendPasswordResetEmailSerializer, UserPasswordResetSerializer,LoginSerializer,AdminLoginSerializer
from .renderers import UserRenderer
from rest_framework.authtoken.models import Token


class ProfileDetailsAPI(generics.GenericAPIView):

    """
    <h1 id="api_title">Profile Details API</h1>
    <p id="api_details">API get requested users profile details.</p>
    <pre>
        <code>
            API Method : GET
            Token Type : Auth Token ==> Authorization : Token {user-auth-token}
        </code>
    </pre>
    <p id="api_response_title"><strong>Response</strong></p>
    <pre>
        <code>
            {
                "id": "IntField",
                "username": "CharField",
                "email": "CharField",
                "is_active": "BooleanField",
                "mobile_number": "CharField",
                "date_created": "DateField",
                "date_updated": "DateField"
            }
        </code>
    </pre>
    <p id="api_response_title"><strong>API Status</strong></p>
    <pre>
        <code>
            <span>200 : Password Changed.</span>
            <span>500 : Internal server error.</span>
        </code>
    </pre>
    """

    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    serializer_class = UserDetailSerializers

    def get(self, request, *args, **kwargs):

        serializer = self.serializer_class(request.user)
        return Response(serializer.data, status=http_status.HTTP_200_OK)


class UpdateProfileAPI(generics.GenericAPIView):

    """
    <h1 id="api_title">Update profile api</h1>
    <p id="api_details">API to update users profile.</p>
    <pre>
        <code>
            API Method : POST
            Token Type : Auth Token ==> Authorization : Token {user-auth-token}
        </code>
    </pre>
    <p id="api_response_title"><strong>Parameters</strong></p>
    <pre>
        <code>
           {
               "username": "CharField",  # username (required)
               "email": "CharField",  # password (required)
           }
       </code>
   </pre>
    <p id="api_response_title"><strong>Response</strong></p>
    <pre>
        <code>
            {
               "username": "CharField",
               "email": "CharField"
           }
        </code>
    </pre>
    <p id="api_response_title"><strong>API Status</strong></p>
    <pre>
        <code>
            <span>200 : Password uppdated.</span>
            <span>400 : Data validation error.</span>
            <span>500 : Internal server error.</span>
        </code>
    </pre>
    """

    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    serializer_class = UserUpdateSerializers

    def put(self, request, *args, **kwargs):

        try:
            serializer = self.serializer_class(data=request.data, instance=request.user)

            if not serializer.is_valid():
                return Response(serializer.errors, status=http_status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response(serializer.data, status=http_status.HTTP_200_OK)

        except Exception as e:
            return Response(e.args, status=http_status.HTTP_500_INTERNAL_SERVER_ERROR)


class AdminLoginAPI(generics.GenericAPIView):  

    permission_classes = [IsTrustedGuest,]
    authentication_classes = [TokenAuthentication,]

    def post(self, request, format=None):
        serializer = AdminLoginSerializer(data=self.request.data,
            context={ 'request': self.request })
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _token = Token.objects.get_or_create(user=user)
        if user.is_authenticated :
            login(request, user)
            user_details = User.objects.get(id=user.id)
            user_serializer = LoginUserDetailsSerialzer(user_details)
            return Response({'message':'Login Successfully',"Token":token.key,"email":request.user.email,"username":request.user.username,"user_id":request.user.id,"user_details":user_serializer.data}, status=status.HTTP_202_ACCEPTED)
        else:
            return Response({"message":"This User Is Not Active"},status=status.HTTP_404_NOT_FOUND)

  
'''
# permission_classes = (IsTrustedGuest,)
# authentication_classes = (TokenAuthentication,)


# def post(self, request, *args, **kwargs):
#         username = request.data["username"]
#         password = request.data["password"]

#         authenticated_user = authenticate(request,username=username, password=password)
#         token, _token = Token.objects.get_or_create(user=authenticated_user)
#         if authenticated_user != None:

#             if(authenticated_user.is_authenticated and authenticated_user.is_superuser):
#                 login(request,authenticated_user)
#                 return JsonResponse({"Message":"User is Authenticated.","Token":token.key,"email":authenticated_user.email})   
#             else:
#                 return JsonResponse({"message":"Admin is not authenticated. "})
#         else:
#             return JsonResponse({"Message":"Either User is not registered or password does not match"})
'''


class AdminLogoutAPI(generics.GenericAPIView):
    def post(self,request,*args,**kwargs):
        logout(request)
        return JsonResponse({"message":"logout"})


class ChangePasswordView(generics.UpdateAPIView):
    """
    <h1 id="api_title">Change Password API</h1>
    <p id="api_details">API to change users password takes input as old and new passwords.</p>
    <pre>
        <code>
            API Method : POST
            Token Type : Auth Token ==> Authorization : Token {user-auth-token}
        </code>
    </pre>
    <p id="api_response_title"><strong>Parameters</strong></p>
    <pre>
        <code>
        {
            "old_password": "CharField",  # Old Password (required)
            "new_password1": "CharField",  # New Password 1 (required)
            "new_password2": "CharField",  # New Password 2 (required)
        }
    </code>
</pre>
    <p id="api_response_title"><strong>Response</strong></p>
    <pre>
        <code>
            {
                "detail": "CharField"
            }
        </code>
    </pre>
    <p id="api_response_title"><strong>API Status</strong></p>
    <pre>
        <code>
            <span>200 : Password Changed.</span>
            <span>400 : Data validation error.</span>
            <span>500 : Internal server error.</span>
        </code>
    </pre>
    """
    
    serializer_class = ChangePasswordSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def post(self, request, *args, **kwargs):
       
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        response = {
            "isSuccess": True,
            'message': 'Password updated successfully',
        }
        

        return Response(response)





class SendPasswordResetEmailView(APIView):
  """
    <h1 id="api_title">Send Password Reset Email API</h1>
    <p id="api_details">API to request for the Reset password. API accept the email address and sends the email.</p>
    <pre>
        <code>
            API Method : POST
            Token Type : Guest Token ==> GUEST-AUTH-TOKEN : {token_provided_by_developer}
        </code>
    </pre>
    <p id="api_response_title"><strong>Parameters</strong></p>
    <pre>
        <code>
           {
               "email": "EmailField",  # Users Email
           }
       </code>
   </pre>
    <p id="api_response_title"><strong>Response</strong></p>
    <pre>
        <code>
            {
                "detail": "CharField"
            }
        </code>
    </pre>
    <p id="api_response_title"><strong>API Status</strong></p>
    <pre>
        <code>
            <span>200 : Forgot password email sent.</span>
            <span>400 : Data validation error.</span>
            <span>500 : Internal server error.</span>
        </code>
    </pre>
    """


  renderer_classes = [UserRenderer]
  permission_classes = [AllowAny,]
  
  def post(self, request, format=None):
    serializer = SendPasswordResetEmailSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    return Response({'msg':'Password Reset link send. Please check your Email',"status":True}, status=status.HTTP_200_OK)

class UserPasswordResetView(APIView):
  renderer_classes = [UserRenderer]
  permission_classes = [AllowAny,]
  def post(self, request, uid, token, format=None):
    serializer = UserPasswordResetSerializer(data=request.data, context={'uid':uid, 'token':token})
    serializer.is_valid(raise_exception=True)
    return Response({'msg':'Password Reset Successfully'}, status=status.HTTP_200_OK)
  
    
class UserProfileDetailsAPI(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)
    serializer_class = UserProfileDetailsSerializer

    def get(self, request, *args, **kwargs):
        try:
            user = self.request.user
            queryset = User.objects.get(id=user.id)
            data = self.serializer_class(queryset).data
            return Response({"data": data, "message": "Success"},status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"data": {"message": str(e)}, "status": status.HTTP_500_INTERNAL_SERVER_ERROR})
        
class CreateUserAPI(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    serializer_class = CreateUserSerialzier

    def post(self, request, *args, **kwargs):
        serializer = CreateUserSerialzier(data=request.data)
        if serializer.is_valid():
           serializer.save()
           return Response(serializer.data)