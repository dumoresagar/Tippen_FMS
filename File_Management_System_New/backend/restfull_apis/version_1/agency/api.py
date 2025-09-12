from rest_framework import generics
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView

from restfull_apis.version_0.permissions.guest import IsTrustedGuest
from .serializer import *
from rest_framework.views import APIView
from core.models import Document,DocumentStatus
from datetime import datetime
from users.models import User,Agency
from os.path import splitext
from django.http import HttpResponse,Http404
from users.models import Agency
from rest_framework.pagination import PageNumberPagination
from mimetypes import guess_type
import os
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.pagination import PageNumberPagination

class CustomPageNumberPagination(PageNumberPagination):
    page_size = 2
    page_size_query_param = 'page_size'


class PostAgencyAPIView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = AgencySerialzier
    

    def post(self, request, format=None):
        serializer = AgencySerialzier(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ListDepartmentAPIView(generics.ListCreateAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def list(self, request):
        try:
            job_details = self.get_queryset()
            serializer = DepartmentSerializer(job_details, many=True)
            return Response({"data": serializer.data, "message": "Success"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"data": {"message": str(e)}, "status": status.HTTP_500_INTERNAL_SERVER_ERROR})

class PostDepartmentAPIView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = DepartmentSerializer
    

    def post(self, request, format=None):
        serializer = DepartmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DepartmentWiseUserListView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = UserListSerializer

    def get(self, request, *args, **kwargs):
        try:
            agency_ids = User.objects.filter(id=self.request.user.id).values_list('agency', flat=True)
            team_ids = User.objects.filter(id=self.request.user.id).values_list('agency__team', flat=True)   
            if User.objects.filter(id=self.request.user.id, user_role__role_name="Super Admin"):
                user_obj = User.objects.filter(department=kwargs.get('pk'))
            elif User.objects.filter(id=self.request.user.id, user_role__role_name="Team Admin"):
                user_obj = User.objects.filter(agency__team__in=team_ids,department=kwargs.get('pk'))
            elif User.objects.filter(id=self.request.user.id, user_role__role_name="Agency Admin"):
                user_obj = User.objects.filter(agency__in=agency_ids,department=kwargs.get('pk'))

            data1 = UserListSerializer(user_obj,many=True).data
            return Response({"data1":data1,"message": "Success"},status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"data": {"message": str(e)}, "status": status.HTTP_204_NO_CONTENT})
        