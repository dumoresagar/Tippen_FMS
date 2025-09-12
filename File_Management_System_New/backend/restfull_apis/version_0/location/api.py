from rest_framework import generics
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework import status
from django.db.models import Sum
from rest_framework.generics import ListAPIView, RetrieveAPIView

from users.models import User
from restfull_apis.version_0.permissions.guest import IsTrustedGuest
from .serializer import *
from rest_framework.views import APIView
from core.models import District,MapType,PreScanningDocument,PaginationMaster,DistrictTalukaAdmin,PreDraftingReport,TeamDistrictMaster
from .permissions import DistrictPermission
from rest_framework.pagination import PageNumberPagination
from core.csv_utils import generate_data_csv,format_datetime
from urllib.parse import quote
from mimetypes import guess_type
import os
from os.path import splitext
from django.shortcuts import get_object_or_404
from datetime import datetime,date, time, timedelta
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.http import JsonResponse
from django.db.models import F, Func,Q
from django.db.models.functions import Length
from math import ceil

from restfull_apis.version_0.document.serializer import AllDocumentListSerialzer

class CustomPageNumberPagination(PageNumberPagination):
    page_size_query_param = 'page_size'

    def get_page_size(self, request):
        # Retrieve the PaginationMaster object for the current user
        try:
            # Assuming 'pagination_user' is the correct field name in your model
            pagination_master = PaginationMaster.objects.get(pagination_user=request.user)
        except PaginationMaster.DoesNotExist:
            # Set a default page size if PaginationMaster doesn't exist for the user
            return 20  # Replace with your default page size

        return pagination_master.page_size

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'per_page_count': self.get_page_size(self.request),  # Call the method with the request
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })
    
class NewCustomPageNumberPagination(PageNumberPagination):
    page_size_query_param = 'page_size'

    def get_page_size(self, request):
        # Retrieve the PaginationMaster object for the current user
        try:
            # Assuming 'pagination_user' is the correct field name in your model
            pagination_master = PaginationMaster.objects.get(pagination_user=request.user)
        except PaginationMaster.DoesNotExist:
            # Set a default page size if PaginationMaster doesn't exist for the user
            return 20  # Replace with your default page size

        return pagination_master.page_size

    def get_paginated_response(self, data):
        total_pages = ceil(self.page.paginator.count / self.get_page_size(self.request))

        return Response({
            'total_pages':total_pages,
            'current_page': self.page.number, 
            'count': self.page.paginator.count,
            'per_page_count': self.get_page_size(self.request),  # Call the method with the request
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })
    
class PostDistrictAPIView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = CreateDistrictSerializer
    

    def post(self, request, format=None):
        serializer = CreateDistrictSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RetriveDistrictAPIView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = CreateDistrictSerializer

    def get(self, request, *args, **kwargs):
        try:

            dist_obj = District.objects.get(id=kwargs.get('pk'))
            data1 = CreateDistrictSerializer(dist_obj).data
            return Response({"data1":data1,"message": "Success"},status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"data": {"message": str(e)}, "status": status.HTTP_204_NO_CONTENT})
    
    def delete(self,*args,**kwargs):
        dist_obj = District.objects.get(id=kwargs.get("pk"))
        dist_obj.delete()
        return Response({"message": "Record deleted successfully","status":True},status=status.HTTP_204_NO_CONTENT)

class ListDistrictAPIView(generics.ListCreateAPIView):
    queryset = District.objects.all()
    serializer_class = CreateDistrictSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    @method_decorator(cache_page(600))  # Cache for 10 minutes
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def list(self, request):
        try:
            job_details = self.get_queryset()
            serializer = CreateDistrictSerializer(job_details, many=True)
            return Response({"data": serializer.data, "message": "Success"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"data": {"message": str(e)}, "status": status.HTTP_500_INTERNAL_SERVER_ERROR})


class UpdateDistrictAPIView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = CreateDistrictSerializer

    def put(self,request,*args,**kwargs):
        if id:
            try:
                dist_obj = District.objects.get(id=kwargs.get("pk"))
            except dist_obj.DoesNotExist:
                return Response({"msg":"record does not exist"})
            serializer = CreateDistrictSerializer(dist_obj, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"data":serializer.data,"message":"Success","status":True})
            return Response(serializer.errors)
        return Response({"msg":"please send id"})

############################################################################
class PostMapTypeAPIView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = CreateMapTypeSerializer

    def post(self, request, format=None):
        serializer = CreateMapTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ListMapTypeAPIView(generics.ListCreateAPIView):
    queryset = MapType.objects.all()
    serializer_class = CreateMapTypeSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def list(self, request):
        try:
            maptype_obj = self.get_queryset()
            serializer = CreateMapTypeSerializer(maptype_obj, many=True)
            return Response({"data": serializer.data, "message": "Success"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"data": {"message": str(e)}, "status": status.HTTP_500_INTERNAL_SERVER_ERROR})


   
class RetriveMapTypeAPIView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = CreateMapTypeSerializer

    def get(self, request, *args, **kwargs):
        try:

            map_obj = MapType.objects.get(id=kwargs.get('pk'))
            data1 = CreateDistrictSerializer(map_obj).data
            return Response({"data1":data1,"message": "Success"},status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"data": {"message": str(e)}, "status": status.HTTP_204_NO_CONTENT})
    
    def delete(self,*args,**kwargs):
        map_obj = MapType.objects.get(id=kwargs.get("pk"))
        map_obj.delete()
        return Response({"message": "Record deleted successfully","status":True},status=status.HTTP_204_NO_CONTENT)


class UpdateMapTypeAPIView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = CreateMapTypeSerializer

    def put(self,request,*args,**kwargs):
        if id:
            try:
                map_obj = MapType.objects.get(id=kwargs.get("pk"))
            except map_obj.DoesNotExist:
                return Response({"msg":"record does not exist"})
            serializer = CreateMapTypeSerializer(map_obj, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"data":serializer.data,"message":"Success","status":True})
            return Response(serializer.errors)
        return Response({"msg":"please send id"})
    
##################################################################################

class PostTalukaAPIView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = CreateTalukaSerializer

    def post(self, request, format=None):
        serializer = CreateTalukaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


   
class RetriveTalukaAPIView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = RetriveTalukaSerializer

    @method_decorator(cache_page(600))  # Cache for 10 minutes
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        try:
            taluka_obj = Taluka.objects.filter(district__district_code=kwargs.get('pk'))
            data1 = RetriveTalukaSerializer(taluka_obj,many=True).data
            return Response({"data1":data1,"message": "Success"},status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"data": {"message": str(e)}, "status": status.HTTP_204_NO_CONTENT})
    
    def delete(self,*args,**kwargs):
        taluka_obj = Taluka.objects.get(id=kwargs.get("pk"))
        taluka_obj.delete()
        return Response({"message": "Record deleted successfully","status":True},status=status.HTTP_204_NO_CONTENT)


class UpdateTalukaAPIView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = CreateTalukaSerializer

    def put(self,request,*args,**kwargs):
        if id:
            try:
                taluka_obj = Taluka.objects.get(id=kwargs.get("pk"))
            except taluka_obj.DoesNotExist:
                return Response({"msg":"record does not exist"})
            serializer = CreateMapTypeSerializer(taluka_obj, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"data":serializer.data,"message":"Success","status":True})
            return Response(serializer.errors)
        return Response({"msg":"please send id"})
    
###########################################################

class PostVillageAPIView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = CreateVillageSerializer

    def post(self, request, format=None):
        serializer = CreateVillageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


   
class RetriveVillageAPIView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = RetriveVillageSerializer

    @method_decorator(cache_page(600))  # Cache for 10 minutes
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        try:
            village_obj = Village.objects.filter(taluka__taluka_code=kwargs.get('pk'))
            data1 = RetriveVillageSerializer(village_obj,many=True).data
            return Response({"data1":data1,"message": "Success"},status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"data": {"message": str(e)}, "status": status.HTTP_204_NO_CONTENT})
    
    def delete(self,*args,**kwargs):
        village_obj = Village.objects.get(id=kwargs.get("pk"))
        village_obj.delete()
        return Response({"message": "Record deleted successfully","status":True},status=status.HTTP_204_NO_CONTENT)


class UpdateVillageAPIView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = CreateVillageSerializer

    def put(self,request,*args,**kwargs):
        if id:
            try:
                village_obj = Village.objects.get(id=kwargs.get("pk"))
            except village_obj.DoesNotExist:
                return Response({"msg":"record does not exist"})
            serializer = CreateVillageSerializer(village_obj, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"data":serializer.data,"message":"Success","status":True})
            return Response(serializer.errors)
        return Response({"msg":"please send id"})
    

class PostPreScanningDocumentAPIView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = PostPreScanningDocumentSerializer

    def post(self, request, format=None):
        serializer = PostPreScanningDocumentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self,request,*args,**kwargs):
        if id:
            try:
                prescan_obj = PreScanningDocument.objects.get(id=kwargs.get("pk"))
            except prescan_obj.DoesNotExist:
                return Response({"msg":"record does not exist"})
            serializer = PostPreScanningDocumentSerializer(prescan_obj, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"data":serializer.data,"message":"Success","status":True})
            return Response(serializer.errors)
        return Response({"msg":"please send id"})

class RetrivePreScanningDocumentAPIView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = PreScanningDocumentSerializer

    def get(self, request, *args, **kwargs):
        try:
            prescan_obj = PreScanningDocument.objects.get(id=kwargs.get('pk'))
            data = PreScanningDocumentSerializer(prescan_obj).data
            return Response({"data":data,"message": "Success"},status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"data": {"message": str(e)}, "status": status.HTTP_204_NO_CONTENT})
        


class DistrictWisePreScanningDocumentView(APIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    # This API User Base Count Display
    def get(self, request):
        excluded_district_codes = [466,470,488,489,491,494,496,495,493]

        admin_district_code  = DistrictTalukaAdmin.objects.filter(user_id=self.request.user.id).values_list('district_id__district_code', flat=True)
        admin_taluka_code  = DistrictTalukaAdmin.objects.filter(user_id=self.request.user.id).values_list('taluka_id__taluka_code', flat=True)
        if User.objects.filter(id=self.request.user.id, user_role__role_name="Super Admin"):
            district_prescan = District.objects.exclude(district_code__in=excluded_district_codes).order_by('-date_created')
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="District Admin"):
            district_prescan = District.objects.filter(district_code__in=admin_district_code).order_by('-date_created')
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Taluka Admin"):
            district_prescan = District.objects.filter(district_code__in=admin_district_code).order_by('-date_created')


        else:
            district_prescan = []

        counts_by_district_prescan = []

        for district_prescan_obj in district_prescan:
            district_id = district_prescan_obj.id
            district_name = district_prescan_obj.district_name
            disctrict_code = district_prescan_obj.district_code
  
            counts = {
                'doc_received_count':0,
                'pre_scanning_count':0,
                'scanning_complete_count':0,
                'rescanning_count':0,
                'document_return':0,
                'number_of_people_present':0,
                'document_rejected':0,
                'no_of_taluka_center':0

            }

            mis_start_date = self.request.query_params.get('mis_start_date',None)
            mis_end_date = self.request.query_params.get('mis_end_date',None)

            if mis_start_date and mis_end_date:
                mis_start_date = datetime.strptime(mis_start_date, '%Y-%m-%d')
                mis_end_date = datetime.strptime(mis_end_date, '%Y-%m-%d')

           

            if User.objects.filter(id=self.request.user.id, user_role__role_name="Super Admin"):
                if mis_start_date and mis_end_date:
                    counts['doc_received_count'] = PreScanningDocument.objects.filter(district_id__district_code=disctrict_code,
                                                mis_date__gte=mis_start_date.date(),
                                                mis_date__lt=(mis_end_date.date()+ timedelta(days=1))                                   
                                                ).aggregate(total_doc_received_count=Sum('doc_received_count'))['total_doc_received_count'] or 0
                    counts['pre_scanning_count'] = PreScanningDocument.objects.filter(district_id__district_code=disctrict_code,
                                                mis_date__gte=mis_start_date.date(),
                                                mis_date__lt=(mis_end_date.date()+ timedelta(days=1))                                     
                                                ).aggregate(total_pre_scanning_count=Sum('pre_scanning_count'))['total_pre_scanning_count'] or 0
                    counts['scanning_complete_count'] = PreScanningDocument.objects.filter(district_id__district_code=disctrict_code,
                                                mis_date__gte=mis_start_date.date(),
                                                mis_date__lt=(mis_end_date.date()+ timedelta(days=1))
                                                ).aggregate(total_scanning_complete_count=Sum('scanning_complete_count'))['total_scanning_complete_count'] or 0
                    counts['rescanning_count'] = PreScanningDocument.objects.filter(district_id__district_code=disctrict_code,
                                                mis_date__gte=mis_start_date.date(),
                                                mis_date__lt=(mis_end_date.date()+ timedelta(days=1))
                                                ).aggregate(total_rescanning_count=Sum('rescanning_count'))['total_rescanning_count'] or 0
                    counts['document_return'] = PreScanningDocument.objects.filter(district_id__district_code=disctrict_code,
                                                mis_date__gte=mis_start_date.date(),
                                                mis_date__lt=(mis_end_date.date()+ timedelta(days=1))
                                                ).aggregate(total_document_return=Sum('document_return'))['total_document_return'] or 0
                    counts['number_of_people_present'] = PreScanningDocument.objects.filter(district_id__district_code=disctrict_code,
                                                mis_date__gte=mis_start_date.date(),
                                                mis_date__lt=(mis_end_date.date()+ timedelta(days=1))
                                                ).aggregate(total_number_of_people_present=Sum('number_of_people_present'))['total_number_of_people_present'] or 0
                    counts['document_rejected'] = PreScanningDocument.objects.filter(district_id__district_code=disctrict_code,
                                                mis_date__gte=mis_start_date.date(),
                                                mis_date__lt=(mis_end_date.date()+ timedelta(days=1))
                                                ).aggregate(total_document_rejected=Sum('document_rejected'))['total_document_rejected'] or 0
                    counts['no_of_taluka_center'] = PreScanningDocument.objects.filter(district_id__district_code=disctrict_code,
                                                mis_date__gte=mis_start_date.date(),
                                                mis_date__lt=(mis_end_date.date()+ timedelta(days=1))
                                                ).values('taluka_id').distinct().count()
                
                else:
                    counts['doc_received_count'] = PreScanningDocument.objects.filter(district_id__district_code=disctrict_code).aggregate(total_doc_received_count=Sum('doc_received_count'))['total_doc_received_count'] or 0
                    counts['pre_scanning_count'] = PreScanningDocument.objects.filter(district_id__district_code=disctrict_code).aggregate(total_pre_scanning_count=Sum('pre_scanning_count'))['total_pre_scanning_count'] or 0
                    counts['scanning_complete_count'] = PreScanningDocument.objects.filter(district_id__district_code=disctrict_code).aggregate(total_scanning_complete_count=Sum('scanning_complete_count'))['total_scanning_complete_count'] or 0
                    counts['rescanning_count'] = PreScanningDocument.objects.filter(district_id__district_code=disctrict_code).aggregate(total_rescanning_count=Sum('rescanning_count'))['total_rescanning_count'] or 0
                    counts['document_return'] = PreScanningDocument.objects.filter(district_id__district_code=disctrict_code).aggregate(total_document_return=Sum('document_return'))['total_document_return'] or 0
                    counts['number_of_people_present'] = PreScanningDocument.objects.filter(district_id__district_code=disctrict_code).aggregate(total_number_of_people_present=Sum('number_of_people_present'))['total_number_of_people_present'] or 0
                    counts['document_rejected'] = PreScanningDocument.objects.filter(district_id__district_code=disctrict_code).aggregate(total_document_rejected=Sum('document_rejected'))['total_document_rejected'] or 0
                    counts['no_of_taluka_center'] = PreScanningDocument.objects.filter(district_id__district_code=disctrict_code).values('taluka_id').distinct().count()

            elif User.objects.filter(id=self.request.user.id, user_role__role_name="District Admin"):
                if mis_start_date and mis_end_date:
                    counts['doc_received_count'] = PreScanningDocument.objects.filter(district_id__district_code=disctrict_code,
                                                mis_date__gte=mis_start_date.date(),
                                                mis_date__lt=(mis_end_date.date()+ timedelta(days=1))                                   
                                                ).aggregate(total_doc_received_count=Sum('doc_received_count'))['total_doc_received_count'] or 0
                    counts['pre_scanning_count'] = PreScanningDocument.objects.filter(district_id__district_code=disctrict_code,
                                                mis_date__gte=mis_start_date.date(),
                                                mis_date__lt=(mis_end_date.date()+ timedelta(days=1))                                     
                                                ).aggregate(total_pre_scanning_count=Sum('pre_scanning_count'))['total_pre_scanning_count'] or 0
                    counts['scanning_complete_count'] = PreScanningDocument.objects.filter(district_id__district_code=disctrict_code,
                                                mis_date__gte=mis_start_date.date(),
                                                mis_date__lt=(mis_end_date.date()+ timedelta(days=1))
                                                ).aggregate(total_scanning_complete_count=Sum('scanning_complete_count'))['total_scanning_complete_count'] or 0
                    counts['rescanning_count'] = PreScanningDocument.objects.filter(district_id__district_code=disctrict_code,
                                                mis_date__gte=mis_start_date.date(),
                                                mis_date__lt=(mis_end_date.date()+ timedelta(days=1))
                                                ).aggregate(total_rescanning_count=Sum('rescanning_count'))['total_rescanning_count'] or 0
                    counts['document_return'] = PreScanningDocument.objects.filter(district_id__district_code=disctrict_code,
                                                mis_date__gte=mis_start_date.date(),
                                                mis_date__lt=(mis_end_date.date()+ timedelta(days=1))
                                                ).aggregate(total_document_return=Sum('document_return'))['total_document_return'] or 0
                    counts['number_of_people_present'] = PreScanningDocument.objects.filter(district_id__district_code=disctrict_code,
                                                mis_date__gte=mis_start_date.date(),
                                                mis_date__lt=(mis_end_date.date()+ timedelta(days=1))
                                                ).aggregate(total_number_of_people_present=Sum('number_of_people_present'))['total_number_of_people_present'] or 0
                    counts['document_rejected'] = PreScanningDocument.objects.filter(district_id__district_code=disctrict_code,
                                                mis_date__gte=mis_start_date.date(),
                                                mis_date__lt=(mis_end_date.date()+ timedelta(days=1))
                                                ).aggregate(total_document_rejected=Sum('document_rejected'))['total_document_rejected'] or 0
                    counts['no_of_taluka_center'] = PreScanningDocument.objects.filter(district_id__district_code=disctrict_code,
                                                mis_date__gte=mis_start_date.date(),
                                                mis_date__lt=(mis_end_date.date()+ timedelta(days=1))
                                                ).values('taluka_id').distinct().count()
                else:
                    counts['doc_received_count'] = PreScanningDocument.objects.filter(district_id__district_code=disctrict_code).aggregate(total_doc_received_count=Sum('doc_received_count'))['total_doc_received_count'] or 0
                    counts['pre_scanning_count'] = PreScanningDocument.objects.filter(district_id__district_code=disctrict_code).aggregate(total_pre_scanning_count=Sum('pre_scanning_count'))['total_pre_scanning_count'] or 0
                    counts['scanning_complete_count'] = PreScanningDocument.objects.filter(district_id__district_code=disctrict_code).aggregate(total_scanning_complete_count=Sum('scanning_complete_count'))['total_scanning_complete_count'] or 0
                    counts['rescanning_count'] = PreScanningDocument.objects.filter(district_id__district_code=disctrict_code).aggregate(total_rescanning_count=Sum('rescanning_count'))['total_rescanning_count'] or 0
                    counts['document_return'] = PreScanningDocument.objects.filter(district_id__district_code=disctrict_code).aggregate(total_document_return=Sum('document_return'))['total_document_return'] or 0
                    counts['number_of_people_present'] = PreScanningDocument.objects.filter(district_id__district_code=disctrict_code).aggregate(total_number_of_people_present=Sum('number_of_people_present'))['total_number_of_people_present'] or 0
                    counts['document_rejected'] = PreScanningDocument.objects.filter(district_id__district_code=disctrict_code).aggregate(total_document_rejected=Sum('document_rejected'))['total_document_rejected'] or 0
                    counts['no_of_taluka_center'] = PreScanningDocument.objects.filter(district_id__district_code=disctrict_code).values('taluka_id').distinct().count()

            elif User.objects.filter(id=self.request.user.id, user_role__role_name="Taluka Admin"):
                if mis_start_date and mis_end_date:
                    counts['doc_received_count'] = PreScanningDocument.objects.filter(district_id__district_code=disctrict_code,taluka_id__taluka_code__in=admin_taluka_code,
                                                mis_date__gte=mis_start_date.date(),
                                                mis_date__lt=(mis_end_date.date()+ timedelta(days=1))                                   
                                                ).aggregate(total_doc_received_count=Sum('doc_received_count'))['total_doc_received_count'] or 0
                    counts['pre_scanning_count'] = PreScanningDocument.objects.filter(district_id__district_code=disctrict_code,taluka_id__taluka_code__in=admin_taluka_code,
                                                mis_date__gte=mis_start_date.date(),
                                                mis_date__lt=(mis_end_date.date()+ timedelta(days=1))                                     
                                                ).aggregate(total_pre_scanning_count=Sum('pre_scanning_count'))['total_pre_scanning_count'] or 0
                    counts['scanning_complete_count'] = PreScanningDocument.objects.filter(district_id__district_code=disctrict_code,taluka_id__taluka_code__in=admin_taluka_code,
                                                mis_date__gte=mis_start_date.date(),
                                                mis_date__lt=(mis_end_date.date()+ timedelta(days=1))
                                                ).aggregate(total_scanning_complete_count=Sum('scanning_complete_count'))['total_scanning_complete_count'] or 0
                    counts['rescanning_count'] = PreScanningDocument.objects.filter(district_id__district_code=disctrict_code,taluka_id__taluka_code__in=admin_taluka_code,
                                                mis_date__gte=mis_start_date.date(),
                                                mis_date__lt=(mis_end_date.date()+ timedelta(days=1))
                                                ).aggregate(total_rescanning_count=Sum('rescanning_count'))['total_rescanning_count'] or 0
                    counts['document_return'] = PreScanningDocument.objects.filter(district_id__district_code=disctrict_code,taluka_id__taluka_code__in=admin_taluka_code,
                                                mis_date__gte=mis_start_date.date(),
                                                mis_date__lt=(mis_end_date.date()+ timedelta(days=1))
                                                ).aggregate(total_document_return=Sum('document_return'))['total_document_return'] or 0
                    counts['number_of_people_present'] = PreScanningDocument.objects.filter(district_id__district_code=disctrict_code,taluka_id__taluka_code__in=admin_taluka_code,
                                                mis_date__gte=mis_start_date.date(),
                                                mis_date__lt=(mis_end_date.date()+ timedelta(days=1))
                                                ).aggregate(total_number_of_people_present=Sum('number_of_people_present'))['total_number_of_people_present'] or 0
                    counts['document_rejected'] = PreScanningDocument.objects.filter(district_id__district_code=disctrict_code,taluka_id__taluka_code__in=admin_taluka_code,
                                                mis_date__gte=mis_start_date.date(),
                                                mis_date__lt=(mis_end_date.date()+ timedelta(days=1))
                                                ).aggregate(total_document_rejected=Sum('document_rejected'))['total_document_rejected'] or 0
                    counts['no_of_taluka_center'] = PreScanningDocument.objects.filter(district_id__district_code=disctrict_code,taluka_id__taluka_code__in=admin_taluka_code,
                                                mis_date__gte=mis_start_date.date(),
                                                mis_date__lt=(mis_end_date.date()+ timedelta(days=1))
                                                ).values('taluka_id').distinct().count()
                    
                else:
                
                    counts['doc_received_count'] = PreScanningDocument.objects.filter(district_id__district_code=disctrict_code,taluka_id__taluka_code__in=admin_taluka_code).aggregate(total_doc_received_count=Sum('doc_received_count'))['total_doc_received_count'] or 0
                    counts['pre_scanning_count'] = PreScanningDocument.objects.filter(district_id__district_code=disctrict_code,taluka_id__taluka_code__in=admin_taluka_code).aggregate(total_pre_scanning_count=Sum('pre_scanning_count'))['total_pre_scanning_count'] or 0
                    counts['scanning_complete_count'] = PreScanningDocument.objects.filter(district_id__district_code=disctrict_code,taluka_id__taluka_code__in=admin_taluka_code).aggregate(total_scanning_complete_count=Sum('scanning_complete_count'))['total_scanning_complete_count'] or 0
                    counts['rescanning_count'] = PreScanningDocument.objects.filter(district_id__district_code=disctrict_code,taluka_id__taluka_code__in=admin_taluka_code).aggregate(total_rescanning_count=Sum('rescanning_count'))['total_rescanning_count'] or 0
                    counts['document_return'] = PreScanningDocument.objects.filter(district_id__district_code=disctrict_code,taluka_id__taluka_code__in=admin_taluka_code).aggregate(total_document_return=Sum('document_return'))['total_document_return'] or 0
                    counts['number_of_people_present'] = PreScanningDocument.objects.filter(district_id__district_code=disctrict_code,taluka_id__taluka_code__in=admin_taluka_code).aggregate(total_number_of_people_present=Sum('number_of_people_present'))['total_number_of_people_present'] or 0
                    counts['document_rejected'] = PreScanningDocument.objects.filter(district_id__district_code=disctrict_code,taluka_id__taluka_code__in=admin_taluka_code).aggregate(total_document_rejected=Sum('document_rejected'))['total_document_rejected'] or 0
                    counts['no_of_taluka_center'] = PreScanningDocument.objects.filter(district_id__district_code=disctrict_code,taluka_id__taluka_code__in=admin_taluka_code).values('taluka_id').distinct().count()

            
           
            counts_by_district_prescan.append({
                'district_id': district_id,
                'district_name':district_name,
                'disctrict_code':disctrict_code,
                **counts,
            })

        response_data = {
            'counts_by_district_prescan': counts_by_district_prescan,
            'status': True
        }

        return Response(data=response_data, status=status.HTTP_200_OK)

class PreScanninfDocumentListAPI(APIView):
    """
    <p id="api_response_title"><strong>API Status</strong></p>
    <pre>
        <code>
            <span>401 :{"detail": "Authentication credentials were not provided." }
            <span>200 :OK.</span>
            <span>500 : Internal server error.</span>
        </code>
    </pre>
    """
    serializer_class = PreScanningDocumentSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk=None, **kwargs):
        try:
            admin_taluka_code  = DistrictTalukaAdmin.objects.filter(user_id=self.request.user.id).values_list('taluka_id__taluka_code', flat=True)
            if User.objects.filter(id=self.request.user.id, user_role__role_name="Super Admin"):
                pre_scaning = PreScanningDocument.objects.filter(district_id__district_code=pk).order_by("-mis_date")
            elif User.objects.filter(id=self.request.user.id, user_role__role_name="District Admin"):
                pre_scaning = PreScanningDocument.objects.filter(district_id__district_code=pk).order_by("-mis_date")
            elif User.objects.filter(id=self.request.user.id, user_role__role_name="Taluka Admin"):
                pre_scaning = PreScanningDocument.objects.filter(district_id__district_code=pk,taluka_id__taluka_code__in=admin_taluka_code).order_by("-mis_date")

            taluka_name = self.request.query_params.get('taluka_name', None)
            mis_start_date = self.request.query_params.get('mis_start_date',None)
            mis_end_date = self.request.query_params.get('mis_end_date',None)

            if taluka_name:
                pre_scaning = pre_scaning.filter(taluka_id__taluka_name__icontains=taluka_name)
                
            if mis_start_date and mis_end_date:
                mis_start_date = datetime.strptime(mis_start_date, '%Y-%m-%d')
                mis_end_date = datetime.strptime(mis_end_date, '%Y-%m-%d')
                pre_scaning = pre_scaning.filter(mis_date__gte=mis_start_date.date(),mis_date__lt=(mis_end_date.date()+ timedelta(days=1)))

            paginator = CustomPageNumberPagination()
            paginated_pre_scanning = paginator.paginate_queryset(pre_scaning, request)
            serializer = PreScanningDocumentSerializer(paginated_pre_scanning, many=True)

            return paginator.get_paginated_response(serializer.data)
            # serializer = PreScanningDocumentSerializer(pre_scaning,many=True)
            # return Response({"data":serializer.data,"message": "Success"},status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"data": {"message": str(e)}, "status": status.HTTP_204_NO_CONTENT})


import os
import subprocess
from django.http import FileResponse,HttpResponse

# def download_postgres_sql(request):
#     db_name = 'file_management'
#     db_user = 'postgres'
#     db_password = 'postgres'  # Replace with your actual password
#     dump_file_path = 'dump.sql'

#     # Set the password in the environment variable
#     os.environ['PGPASSWORD'] = db_password

#     command = f"pg_dump -h localhost -U {db_user} -d {db_name} -f {dump_file_path}"

#     try:
#         process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#         stdout, stderr = process.communicate()

#         if process.returncode != 0:
#             print(f"Error output: {stderr.decode('utf-8')}")
#             return HttpResponse(f'Error: {stderr.decode("utf-8")}', status=500)

#         with open(dump_file_path, 'rb') as f:
#             response = HttpResponse(f.read(), content_type='application/force-download')
#             response['Content-Disposition'] = f'attachment; filename=dump.sql'
#             return response
#     except Exception as e:
#         return HttpResponse(f'Error: {str(e)}', status=500)


def download_postgres_sql(request):
    db_name = 'file_management'
    db_user = 'postgres'
    db_password = 'postgres'  # Replace with your actual password
    dump_file_path = 'dump.sql'

    # Set the password in the environment variable
    os.environ['PGPASSWORD'] = db_password

    # Command to dump the PostgreSQL database to a file
    command = f"pg_dump -h localhost -U {db_user} -d {db_name} -f {dump_file_path}"

    try:
        # Run the pg_dump command to create the SQL dump
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        # Check if the dump was successful
        if process.returncode != 0:
            print(f"Error output: {stderr.decode('utf-8')}")
            return HttpResponse(f'Error: {stderr.decode("utf-8")}', status=500)

        # Use FileResponse to stream the file back to the client
        response = FileResponse(open(dump_file_path, 'rb'), as_attachment=True, filename='dump.sql')
        return response
    except Exception as e:
        return HttpResponse(f'Error: {str(e)}', status=500)


class PostPreDraftingReportAPIView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = PostPreDraftingReportSerializer

    def post(self, request, format=None):
        serializer = PostPreDraftingReportSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self,request,*args,**kwargs):
        if id:
            try:
                predraft_obj = PreDraftingReport.objects.get(id=kwargs.get("pk"))
            except predraft_obj.DoesNotExist:
                return Response({"msg":"record does not exist"})
            serializer = PostPreDraftingReportSerializer(predraft_obj, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"data":serializer.data,"message":"Success","status":True})
            return Response(serializer.errors)
        return Response({"msg":"please send id"})

class RetrivePreDraftingReportAPIView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = PreDraftingReportSerializer

    def get(self, request, *args, **kwargs):
        try:
            predraft_obj = PreDraftingReport.objects.get(id=kwargs.get('pk'))
            data = PreDraftingReportSerializer(predraft_obj).data
            return Response({"data":data,"message": "Success"},status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"data": {"message": str(e)}, "status": status.HTTP_204_NO_CONTENT})
        

class DistrictWisePreDraftingReportView(APIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    # This API User Base Count Display
    def get(self, request):
        excluded_district_codes = [466,470,488,489,491,494,496,495,493]

        admin_district_code  = DistrictTalukaAdmin.objects.filter(user_id=self.request.user.id).values_list('district_id__district_code', flat=True)
        admin_taluka_code  = DistrictTalukaAdmin.objects.filter(user_id=self.request.user.id).values_list('taluka_id__taluka_code', flat=True)
        if User.objects.filter(id=self.request.user.id, user_role__role_name="Super Admin"):
            district_predraft = District.objects.exclude(district_code__in=excluded_district_codes).order_by('-date_created')
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="District Admin"):
            district_predraft = District.objects.filter(district_code__in=admin_district_code).order_by('-date_created')
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Taluka Admin"):
            district_predraft = District.objects.filter(district_code__in=admin_district_code).order_by('-date_created')


        else:
            district_predraft = []

        counts_by_district_predraft = []

        for district_predraft_obj in district_predraft:
            district_id = district_predraft_obj.id
            district_name = district_predraft_obj.district_name
            disctrict_code = district_predraft_obj.district_code
  
            counts = {
                'drafting_map_count':0,
                'correction_uploading_map_count':0,
            }
            
            drafting_start_date = self.request.query_params.get('drafting_start_date',None)
            drafting_end_date = self.request.query_params.get('drafting_end_date',None)


            if drafting_start_date and drafting_end_date:
                drafting_start_date = datetime.strptime(drafting_start_date, '%Y-%m-%d')
                drafting_end_date = datetime.strptime(drafting_end_date, '%Y-%m-%d')


            if User.objects.filter(id=self.request.user.id, user_role__role_name="Super Admin"):
                if drafting_start_date and drafting_end_date:
                    counts['drafting_map_count'] = PreDraftingReport.objects.filter(district_id__district_code=disctrict_code,
                                                pre_drafting_date__gte=drafting_start_date.date(),
                                                pre_drafting_date__lt=(drafting_end_date.date()+ timedelta(days=1))
                                                ).aggregate(total_drafting_map_count=Sum('drafting_map_count'))['total_drafting_map_count'] or 0
                    counts['correction_uploading_map_count'] = PreDraftingReport.objects.filter(district_id__district_code=disctrict_code,
                                                            pre_drafting_date__gte=drafting_start_date.date(),
                                                            pre_drafting_date__lt=(drafting_end_date.date()+ timedelta(days=1))
                                                            ).aggregate(total_correction_uploading_map_count=Sum('correction_uploading_map_count'))['total_correction_uploading_map_count'] or 0

                else:
                    counts['drafting_map_count'] = PreDraftingReport.objects.filter(district_id__district_code=disctrict_code).aggregate(total_drafting_map_count=Sum('drafting_map_count'))['total_drafting_map_count'] or 0
                    counts['correction_uploading_map_count'] = PreDraftingReport.objects.filter(district_id__district_code=disctrict_code).aggregate(total_correction_uploading_map_count=Sum('correction_uploading_map_count'))['total_correction_uploading_map_count'] or 0
              
            elif User.objects.filter(id=self.request.user.id, user_role__role_name="District Admin"):
                if drafting_start_date and drafting_end_date:
                    counts['drafting_map_count'] = PreDraftingReport.objects.filter(district_id__district_code=disctrict_code,
                                                pre_drafting_date__gte=drafting_start_date.date(),
                                                pre_drafting_date__lt=(drafting_end_date.date()+ timedelta(days=1))
                                                ).aggregate(total_drafting_map_count=Sum('drafting_map_count'))['total_drafting_map_count'] or 0
                    counts['correction_uploading_map_count'] = PreDraftingReport.objects.filter(district_id__district_code=disctrict_code,                                                                                        
                                                            pre_drafting_date__gte=drafting_start_date.date(),
                                                            pre_drafting_date__lt=(drafting_end_date.date()+ timedelta(days=1))
                                                            ).aggregate(total_correction_uploading_map_count=Sum('correction_uploading_map_count'))['total_correction_uploading_map_count'] or 0
                else:
                    counts['drafting_map_count'] = PreDraftingReport.objects.filter(district_id__district_code=disctrict_code).aggregate(total_drafting_map_count=Sum('drafting_map_count'))['total_drafting_map_count'] or 0
                    counts['correction_uploading_map_count'] = PreDraftingReport.objects.filter(district_id__district_code=disctrict_code).aggregate(total_correction_uploading_map_count=Sum('correction_uploading_map_count'))['total_correction_uploading_map_count'] or 0
            elif User.objects.filter(id=self.request.user.id, user_role__role_name="Taluka Admin"):
                if drafting_start_date and drafting_end_date:
                    counts['drafting_map_count'] = PreDraftingReport.objects.filter(district_id__district_code=disctrict_code,taluka_id__taluka_code__in=admin_taluka_code,
                                                            pre_drafting_date__gte=drafting_start_date.date(),
                                                            pre_drafting_date__lt=(drafting_end_date.date()+ timedelta(days=1))
                                                            ).aggregate(total_drafting_map_count=Sum('drafting_map_count'))['total_drafting_map_count'] or 0
                    counts['correction_uploading_map_count'] = PreDraftingReport.objects.filter(district_id__district_code=disctrict_code,taluka_id__taluka_code__in=admin_taluka_code,
                                                            pre_drafting_date__gte=drafting_start_date.date(),
                                                            pre_drafting_date__lt=(drafting_end_date.date()+ timedelta(days=1))
                                                            ).aggregate(total_correction_uploading_map_count=Sum('correction_uploading_map_count'))['total_correction_uploading_map_count'] or 0
    
                else:
                    counts['drafting_map_count'] = PreDraftingReport.objects.filter(district_id__district_code=disctrict_code,taluka_id__taluka_code__in=admin_taluka_code).aggregate(total_drafting_map_count=Sum('drafting_map_count'))['total_drafting_map_count'] or 0
                    counts['correction_uploading_map_count'] = PreDraftingReport.objects.filter(district_id__district_code=disctrict_code,taluka_id__taluka_code__in=admin_taluka_code).aggregate(total_correction_uploading_map_count=Sum('correction_uploading_map_count'))['total_correction_uploading_map_count'] or 0
        
           
            counts_by_district_predraft.append({
                'district_id': district_id,
                'district_name':district_name,
                'disctrict_code':disctrict_code,
                **counts,
            })

        response_data = {
            'counts_by_district_predraft': counts_by_district_predraft,
            'status': True
        }

        return Response(data=response_data, status=status.HTTP_200_OK)
    
class PreDraftingReportListAPI(APIView):
    """
    <p id="api_response_title"><strong>API Status</strong></p>
    <pre>
        <code>
            <span>401 :{"detail": "Authentication credentials were not provided." }
            <span>200 :OK.</span>
            <span>500 : Internal server error.</span>
        </code>
    </pre>
    """
    serializer_class = PreDraftingReportSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk=None, **kwargs):
        try:
            admin_taluka_code  = DistrictTalukaAdmin.objects.filter(user_id=self.request.user.id).values_list('taluka_id__taluka_code', flat=True)
            if User.objects.filter(id=self.request.user.id, user_role__role_name="Super Admin"):
                pre_draft = PreDraftingReport.objects.filter(district_id__district_code=pk).order_by("-pre_drafting_date")
            elif User.objects.filter(id=self.request.user.id, user_role__role_name="District Admin"):
                pre_draft = PreDraftingReport.objects.filter(district_id__district_code=pk).order_by("-pre_drafting_date")
            elif User.objects.filter(id=self.request.user.id, user_role__role_name="Taluka Admin"):
                pre_draft = PreDraftingReport.objects.filter(district_id__district_code=pk,taluka_id__taluka_code__in=admin_taluka_code).order_by("-pre_drafting_date")

            taluka_name = self.request.query_params.get('taluka_name', None)
            drafting_start_date = self.request.query_params.get('drafting_start_date',None)
            drafting_end_date = self.request.query_params.get('drafting_end_date',None)

            if taluka_name:
                pre_draft = pre_draft.filter(taluka_id__taluka_name__icontains=taluka_name)
                
            if drafting_start_date and drafting_end_date:
                drafting_start_date = datetime.strptime(drafting_start_date, '%Y-%m-%d')
                drafting_end_date = datetime.strptime(drafting_end_date, '%Y-%m-%d')
                pre_draft = pre_draft.filter(pre_drafting_date__gte=drafting_start_date.date(),pre_drafting_date__lt=(drafting_end_date.date()+ timedelta(days=1)))

            paginator = CustomPageNumberPagination()
            paginated_pre_drafting = paginator.paginate_queryset(pre_draft, request)
            serializer = PreDraftingReportSerializer(paginated_pre_drafting, many=True)

            return paginator.get_paginated_response(serializer.data)
            # serializer = PreDraftingReportSerializer(pre_draft,many=True)
            # return Response({"data":serializer.data,"message": "Success"},status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"data": {"message": str(e)}, "status": status.HTTP_204_NO_CONTENT})
        



class PostAgencyInventryAPIView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = AgencyInventrySerializer

    def post(self, request, format=None):
        serializer = AgencyInventrySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self,request,*args,**kwargs):
        if id:
            try:
                agency_inventry_obj = AgencyInventry.objects.get(id=kwargs.get("pk"))
            except agency_inventry_obj.DoesNotExist:
                return Response({"msg":"record does not exist"})
            serializer = AgencyInventrySerializer(agency_inventry_obj, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"data":serializer.data,"message":"Success","status":True})
            return Response(serializer.errors)
        return Response({"msg":"please send id"})

class GetAgencyInventryAPIView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = AgencyInventrySerializer

    def get(self, request, *args, **kwargs):
        try:
            agency_inventry_obj = AgencyInventry.objects.get(id=kwargs.get('pk'))
            data = AgencyInventrySerializer(agency_inventry_obj).data
            return Response({"data":data,"message": "Success"},status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"data": {"message": str(e)}, "status": status.HTTP_204_NO_CONTENT})
        



class PreScanningDistrictTalukaTotalToday(generics.ListAPIView):
    queryset = District.objects.all()
    permission_classes = [IsAuthenticated,]
    authentication_classes = (TokenAuthentication,)
    serializer_class = DistrcitWiseTalukaTodalTodaySerialzier
   


    def get_queryset(self):
        queryset = self.queryset
        team_ids = User.objects.filter(id=self.request.user.id).values_list('agency__team', flat=True)
        team_district_code = TeamDistrictMaster.objects.filter(team__in=team_ids).values_list('district_id__district_code', flat=True)
        distrcit_taluka_admin= DistrictTalukaAdmin.objects.filter(user_id=self.request.user.id).values_list('district_id__district_code',flat=True)

        if User.objects.filter(id=self.request.user.id, user_role__role_name="Super Admin"):
            query_set = queryset.all().order_by('-date_created')
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Team Admin"):
            query_set = queryset.filter(district_code__in=team_district_code).order_by('-date_created')
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Agency Admin"):
            query_set = queryset.filter(district_code__in=team_district_code).order_by('-date_created')
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="District Admin"):
            query_set = queryset.filter(district_code__in=distrcit_taluka_admin).order_by('-date_created')
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Taluka Admin"):
            query_set = queryset.filter(district_code__in=distrcit_taluka_admin).order_by('-date_created')


        else:
            query_set = queryset.none()  # Return an empty queryset for other roles
  
      
            
        return query_set

class PreDraftingDistrictTalukaTotalToday(generics.ListAPIView):
    queryset = District.objects.all()
    permission_classes = [IsAuthenticated,]
    authentication_classes = (TokenAuthentication,)
    serializer_class = PreDraftDistrcitWiseTalukaTodalTodaySerialzier
   


    def get_queryset(self):
        queryset = self.queryset
        team_ids = User.objects.filter(id=self.request.user.id).values_list('agency__team', flat=True)
        team_district_code = TeamDistrictMaster.objects.filter(team__in=team_ids).values_list('district_id__district_code', flat=True)
        distrcit_taluka_admin= DistrictTalukaAdmin.objects.filter(user_id=self.request.user.id).values_list('district_id__district_code',flat=True)

        if User.objects.filter(id=self.request.user.id, user_role__role_name="Super Admin"):
            query_set = queryset.all().order_by('-date_created')
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Team Admin"):
            query_set = queryset.filter(district_code__in=team_district_code).order_by('-date_created')
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Agency Admin"):
            query_set = queryset.filter(district_code__in=team_district_code).order_by('-date_created')
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="District Admin"):
            query_set = queryset.filter(district_code__in=distrcit_taluka_admin).order_by('-date_created')
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Taluka Admin"):
            query_set = queryset.filter(district_code__in=distrcit_taluka_admin).order_by('-date_created')


        else:
            query_set = queryset.none()  # Return an empty queryset for other roles
  
      
            
        return query_set



class DynamsoftProductKey(APIView):
    permission_classes = [AllowAny,]
    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        dynamsoft_product_key = "t0115QAEAAGZRADNIaTQYoNXOa7+gSGSayHTxvkwydx/i8RdV6+I7jzbptgxzXEwL4vhpaIosRGHaWJi5DrR6pmHHBo+Fombq2WR8M5U5un/K9PUE7pp5LA/d5cFzzuyPpvyDP55SqTO5a4xkRhTRLIQbCcNAgA=="
        # You can add any additional logic to validate or process the product key here

        return Response({"product_key": dynamsoft_product_key}, status=status.HTTP_200_OK)
    
import pandas as pd
from .serializer import PolygonUpdateSerializer
class UpdatePolygonCount(generics.GenericAPIView):
    permission_classes = [AllowAny]
    authentication_classes = (TokenAuthentication,)
    serializer_class = PolygonUpdateSerializer 

    def put(self, request, *args, **kwargs):
        action = kwargs.get('action', None)
        uploaded_file = request.FILES['file']

        df = pd.read_excel(uploaded_file)

        if action == 'qc_polygon':
            for index, row in df.iterrows():
                barcode = str(row['DOCID'])
                polygon_count = int(row['NO.POLYGONS'])

                try:
                    document = Document.objects.get(barcode_number=barcode)
                except Document.DoesNotExist:
                    continue

                document.qc_polygon_count = polygon_count
                document.save()

            return Response({'message': 'QC Polygon counts updated successfully'})
        elif action == 'digitize_polygon':
            for index, row in df.iterrows():
                barcode = str(row['DOCID'])
                polygon_count = int(row['NO.POLYGONS'])

                try:
                    document = Document.objects.get(barcode_number=barcode)
                except Document.DoesNotExist:
                    continue

                document.polygon_count = polygon_count
                document.save()

            return Response({'message': 'Digitize Polygon counts updated successfully'})
        else:
                return Response({"message": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)
        



    


class DocumentLocationList(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = DocumentLocationListSerialzer

    def get(self, request, *args, **kwargs):
        try:

            obj = Document.objects.get(barcode_number=kwargs.get('barcode_number'))
            data = DocumentLocationListSerialzer(obj).data
            return Response({"data":data,"message": "Success"},status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"data": {"message": str(e)}, "status": status.HTTP_204_NO_CONTENT})



from django.conf import settings


class MismatchedFileExtensionsView(ListAPIView):
    serializer_class = ExtensionDocumentSerializer
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        # Fetch only necessary fields to improve DB performance
        queryset = Document.objects.only('id', 'scan_upload').filter(scan_upload__isnull=False)

        # List comprehension for fast file existence check
        missing_file_ids = [
            doc.id for doc in queryset.iterator()  # Uses `iterator()` for memory efficiency
            if not os.path.exists(os.path.join(settings.MEDIA_ROOT, str(doc.scan_upload)))
        ]

        # Directly filter IDs in the query
        return Document.objects.filter(id__in=missing_file_ids)
    

class RectifyMismatchedFileExtensionsView(ListAPIView):
    serializer_class = RectifyExtensionDocumentSerializer
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        # Fetch only necessary fields to improve DB performance
        queryset = Document.objects.only('id', 'rectify_upload').filter(rectify_upload__isnull=False)

        # List comprehension for fast file existence check
        missing_file_ids = [
            doc.id for doc in queryset.iterator()  # Uses `iterator()` for memory efficiency
            if not os.path.exists(os.path.join(settings.MEDIA_ROOT, str(doc.rectify_upload)))
        ]

        # Directly filter IDs in the query
        return Document.objects.filter(id__in=missing_file_ids,rectify_completed_date__isnull=False)
    
class DigitizeMismatchedFileExtensionsView(ListAPIView):
    serializer_class = DigitizeExtensionDocumentSerializer
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        # Fetch only necessary fields to improve DB performance
        queryset = Document.objects.only('id', 'digitize_upload').filter(digitize_upload__isnull=False)

        # List comprehension for fast file existence check
        missing_file_ids = [
            doc.id for doc in queryset.iterator()  # Uses `iterator()` for memory efficiency
            if not os.path.exists(os.path.join(settings.MEDIA_ROOT, str(doc.digitize_upload)))
        ]

        # Directly filter IDs in the query
        return Document.objects.filter(id__in=missing_file_ids,digitize_completed_date__isnull=False)
    

class DigitizeCountFileFileView(ListAPIView):
    serializer_class = AllDocumentListSerialzer
    pagination_class = CustomPageNumberPagination


    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)

        if request.GET.get('is_export') and request.GET.get('is_export') in ['1', 1]:
            for_count = 0
            csv_header = ['Sr.No','Barcode Number','District Name','Taluka Name','Village Name','Map Code','Current Status','Scan Uploaded Date','Scan By Username','Rectify Agency Name','Rectify By Username','Rectify Assign Date','Rectify Completed Date','Digitize Agency Name','Digitize By Username','Digitize Polygon Count','Digitize Assign Date','Digitize Completed Date','QC Agency Name','QC By username','Qc Polygon Count','Qc Assign Date','Qc Completed Date','PDF By Username','Pdf Completed Date','Govt QC By Username','Gov Qc Assign Date','Gov Qc Completed Date','Gov Pdf Completed Date','Topology Agency Name','Topology By Username','Topology Assign Date','Topology Completed Date','Shape Agency Name','Shape By Username','Shape Assign Date','Shape Completed Date']
            
            csv_body = []

            qs_data = self.get_serializer(queryset, many=True)

            for qs in qs_data.data:
                for_count += 1
                district_name = qs.get('district_name', {}).get('district_name', '') if qs.get('district_name') else ''
                taluka_name = qs.get('taluka_name', {}).get('taluka_name', '') if qs.get('taluka_name') else ''
                village_name = qs.get('village_name', {}).get('village_name', '') if qs.get('village_name') else ''
                csv_body.append(
                    [
                        for_count,
                        qs.get('barcode_number')+'`',
                        district_name,
                        taluka_name,
                        village_name,
                        qs.get('map_code'),
                        qs.get('current_status'),
                        qs.get('scan_uploaded_date'),
                        qs.get('scan_by_username'),
                        qs.get('rectify_agency_name'),
                        qs.get('rectify_by_username'),
                        format_datetime(qs.get('rectify_assign_date')),
                        format_datetime(qs.get('rectify_completed_date')),
                        qs.get('digitize_agency_name'),
                        qs.get('digitize_by_username'),
                        qs.get('polygon_count'),
                        format_datetime(qs.get('digitize_assign_date')),
                        format_datetime(qs.get('digitize_completed_date')),
                        qs.get('qc_agency_name'),
                        qs.get('qc_by_username'),
                        qs.get('qc_polygon_count'),
                        format_datetime(qs.get('qc_assign_date')),
                        format_datetime(qs.get('qc_completed_date')),
                        qs.get('pdf_by_username'),
                        qs.get('pdf_completed_date'),
                        qs.get('gov_qc_by_username'),
                        qs.get('gov_qc_assign_date'),
                        format_datetime(qs.get('gov_qc_completed_date')),
                        format_datetime(qs.get('gov_pdf_completed_date')),
                        qs.get('topology_agency_name'),
                        qs.get('topology_by_username'),
                        format_datetime(qs.get('topology_assign_date')),
                        format_datetime(qs.get('topology_completed_date')),
                        qs.get('shape_agency_name'),
                        qs.get('shape_by_username'),
                        format_datetime(qs.get('shape_assign_date')),
                        format_datetime(qs.get('shape_completed_date'))

                    ]
                )

            csv_data = generate_data_csv(csv_header, csv_body, f"digitize_report_data_{datetime.now()}_.csv")
            return Response({'csv_path': csv_data.get('csv_path')})

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


    def get_queryset(self):
        return Document.objects.filter(
            Q(digitize_upload__isnull=True) | Q(digitize_upload=''),
            ~Q(polygon_count=0)
        )
    


class QCCountFileFileView(ListAPIView):
    serializer_class = AllDocumentListSerialzer
    pagination_class = CustomPageNumberPagination


    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)

        if request.GET.get('is_export') and request.GET.get('is_export') in ['1', 1]:
            for_count = 0
            csv_header = ['Sr.No','Barcode Number','District Name','Taluka Name','Village Name','Map Code','Current Status','Scan Uploaded Date','Scan By Username','Rectify Agency Name','Rectify By Username','Rectify Assign Date','Rectify Completed Date','Digitize Agency Name','Digitize By Username','Digitize Polygon Count','Digitize Assign Date','Digitize Completed Date','QC Agency Name','QC By username','Qc Polygon Count','Qc Assign Date','Qc Completed Date','PDF By Username','Pdf Completed Date','Govt QC By Username','Gov Qc Assign Date','Gov Qc Completed Date','Gov Pdf Completed Date','Topology Agency Name','Topology By Username','Topology Assign Date','Topology Completed Date','Shape Agency Name','Shape By Username','Shape Assign Date','Shape Completed Date']
            
            csv_body = []

            qs_data = self.get_serializer(queryset, many=True)

            for qs in qs_data.data:
                for_count += 1
                district_name = qs.get('district_name', {}).get('district_name', '') if qs.get('district_name') else ''
                taluka_name = qs.get('taluka_name', {}).get('taluka_name', '') if qs.get('taluka_name') else ''
                village_name = qs.get('village_name', {}).get('village_name', '') if qs.get('village_name') else ''
                csv_body.append(
                    [
                        for_count,
                        qs.get('barcode_number')+'`',
                        district_name,
                        taluka_name,
                        village_name,
                        qs.get('map_code'),
                        qs.get('current_status'),
                        qs.get('scan_uploaded_date'),
                        qs.get('scan_by_username'),
                        qs.get('rectify_agency_name'),
                        qs.get('rectify_by_username'),
                        format_datetime(qs.get('rectify_assign_date')),
                        format_datetime(qs.get('rectify_completed_date')),
                        qs.get('digitize_agency_name'),
                        qs.get('digitize_by_username'),
                        qs.get('polygon_count'),
                        format_datetime(qs.get('digitize_assign_date')),
                        format_datetime(qs.get('digitize_completed_date')),
                        qs.get('qc_agency_name'),
                        qs.get('qc_by_username'),
                        qs.get('qc_polygon_count'),
                        format_datetime(qs.get('qc_assign_date')),
                        format_datetime(qs.get('qc_completed_date')),
                        qs.get('pdf_by_username'),
                        qs.get('pdf_completed_date'),
                        qs.get('gov_qc_by_username'),
                        qs.get('gov_qc_assign_date'),
                        format_datetime(qs.get('gov_qc_completed_date')),
                        format_datetime(qs.get('gov_pdf_completed_date')),
                        qs.get('topology_agency_name'),
                        qs.get('topology_by_username'),
                        format_datetime(qs.get('topology_assign_date')),
                        format_datetime(qs.get('topology_completed_date')),
                        qs.get('shape_agency_name'),
                        qs.get('shape_by_username'),
                        format_datetime(qs.get('shape_assign_date')),
                        format_datetime(qs.get('shape_completed_date'))

                    ]
                )

            csv_data = generate_data_csv(csv_header, csv_body, f"qc_report_data_{datetime.now()}_.csv")
            return Response({'csv_path': csv_data.get('csv_path')})

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

 

    def get_queryset(self):
        return Document.objects.filter(
            Q(qc_upload__isnull=True) | Q(qc_upload=''),
            ~Q(qc_polygon_count=0)
        )
    




class BarcodeNinetyDigitFileView(ListAPIView):
    serializer_class = AllDocumentListSerialzer
    pagination_class = NewCustomPageNumberPagination


    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)

        if request.GET.get('is_export') and request.GET.get('is_export') in ['1', 1]:
            for_count = 0
            csv_header = ['Sr.No','Barcode Number','District Name','Taluka Name','Village Name','Map Code','Current Status','Scan Uploaded Date','Scan By Username','Rectify Agency Name','Rectify By Username','Rectify Assign Date','Rectify Completed Date','Digitize Agency Name','Digitize By Username','Digitize Polygon Count','Digitize Assign Date','Digitize Completed Date','QC Agency Name','QC By username','Qc Polygon Count','Qc Assign Date','Qc Completed Date','PDF By Username','Pdf Completed Date','Govt QC By Username','Gov Qc Assign Date','Gov Qc Completed Date','Gov Pdf Completed Date','Topology Agency Name','Topology By Username','Topology Assign Date','Topology Completed Date','Shape Agency Name','Shape By Username','Shape Assign Date','Shape Completed Date']
            
            csv_body = []

            qs_data = self.get_serializer(queryset, many=True)

            for qs in qs_data.data:
                for_count += 1
                district_name = qs.get('district_name', {}).get('district_name', '') if qs.get('district_name') else ''
                taluka_name = qs.get('taluka_name', {}).get('taluka_name', '') if qs.get('taluka_name') else ''
                village_name = qs.get('village_name', {}).get('village_name', '') if qs.get('village_name') else ''
                csv_body.append(
                    [
                        for_count,
                        qs.get('barcode_number')+'`',
                        district_name,
                        taluka_name,
                        village_name,
                        qs.get('map_code'),
                        qs.get('current_status'),
                        qs.get('scan_uploaded_date'),
                        qs.get('scan_by_username'),
                        qs.get('rectify_agency_name'),
                        qs.get('rectify_by_username'),
                        format_datetime(qs.get('rectify_assign_date')),
                        format_datetime(qs.get('rectify_completed_date')),
                        qs.get('digitize_agency_name'),
                        qs.get('digitize_by_username'),
                        qs.get('polygon_count'),
                        format_datetime(qs.get('digitize_assign_date')),
                        format_datetime(qs.get('digitize_completed_date')),
                        qs.get('qc_agency_name'),
                        qs.get('qc_by_username'),
                        qs.get('qc_polygon_count'),
                        format_datetime(qs.get('qc_assign_date')),
                        format_datetime(qs.get('qc_completed_date')),
                        qs.get('pdf_by_username'),
                        qs.get('pdf_completed_date'),
                        qs.get('gov_qc_by_username'),
                        qs.get('gov_qc_assign_date'),
                        format_datetime(qs.get('gov_qc_completed_date')),
                        format_datetime(qs.get('gov_pdf_completed_date')),
                        qs.get('topology_agency_name'),
                        qs.get('topology_by_username'),
                        format_datetime(qs.get('topology_assign_date')),
                        format_datetime(qs.get('topology_completed_date')),
                        qs.get('shape_agency_name'),
                        qs.get('shape_by_username'),
                        format_datetime(qs.get('shape_assign_date')),
                        format_datetime(qs.get('shape_completed_date'))

                    ]
                )

            csv_data = generate_data_csv(csv_header, csv_body, f"qc_report_data_{datetime.now()}_.csv")
            return Response({'csv_path': csv_data.get('csv_path')})

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)



    def get_queryset(self):
        return Document.objects.annotate(
            barcode_length=Length('barcode_number')
        ).filter(
            barcode_number__isnull=False,
            barcode_length=19
        )
    

class BarcodeTwentyOneDigitFileView(ListAPIView):
    serializer_class = AllDocumentListSerialzer
    pagination_class = NewCustomPageNumberPagination

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)

        if request.GET.get('is_export') and request.GET.get('is_export') in ['1', 1]:
            for_count = 0
            csv_header = ['Sr.No','Barcode Number','District Name','Taluka Name','Village Name','Map Code','Current Status','Scan Uploaded Date','Scan By Username','Rectify Agency Name','Rectify By Username','Rectify Assign Date','Rectify Completed Date','Digitize Agency Name','Digitize By Username','Digitize Polygon Count','Digitize Assign Date','Digitize Completed Date','QC Agency Name','QC By username','Qc Polygon Count','Qc Assign Date','Qc Completed Date','PDF By Username','Pdf Completed Date','Govt QC By Username','Gov Qc Assign Date','Gov Qc Completed Date','Gov Pdf Completed Date','Topology Agency Name','Topology By Username','Topology Assign Date','Topology Completed Date','Shape Agency Name','Shape By Username','Shape Assign Date','Shape Completed Date']
            
            csv_body = []

            qs_data = self.get_serializer(queryset, many=True)

            for qs in qs_data.data:
                for_count += 1
                district_name = qs.get('district_name', {}).get('district_name', '') if qs.get('district_name') else ''
                taluka_name = qs.get('taluka_name', {}).get('taluka_name', '') if qs.get('taluka_name') else ''
                village_name = qs.get('village_name', {}).get('village_name', '') if qs.get('village_name') else ''
                csv_body.append(
                    [
                        for_count,
                        qs.get('barcode_number')+'`',
                        district_name,
                        taluka_name,
                        village_name,
                        qs.get('map_code'),
                        qs.get('current_status'),
                        qs.get('scan_uploaded_date'),
                        qs.get('scan_by_username'),
                        qs.get('rectify_agency_name'),
                        qs.get('rectify_by_username'),
                        format_datetime(qs.get('rectify_assign_date')),
                        format_datetime(qs.get('rectify_completed_date')),
                        qs.get('digitize_agency_name'),
                        qs.get('digitize_by_username'),
                        qs.get('polygon_count'),
                        format_datetime(qs.get('digitize_assign_date')),
                        format_datetime(qs.get('digitize_completed_date')),
                        qs.get('qc_agency_name'),
                        qs.get('qc_by_username'),
                        qs.get('qc_polygon_count'),
                        format_datetime(qs.get('qc_assign_date')),
                        format_datetime(qs.get('qc_completed_date')),
                        qs.get('pdf_by_username'),
                        qs.get('pdf_completed_date'),
                        qs.get('gov_qc_by_username'),
                        qs.get('gov_qc_assign_date'),
                        format_datetime(qs.get('gov_qc_completed_date')),
                        format_datetime(qs.get('gov_pdf_completed_date')),
                        qs.get('topology_agency_name'),
                        qs.get('topology_by_username'),
                        format_datetime(qs.get('topology_assign_date')),
                        format_datetime(qs.get('topology_completed_date')),
                        qs.get('shape_agency_name'),
                        qs.get('shape_by_username'),
                        format_datetime(qs.get('shape_assign_date')),
                        format_datetime(qs.get('shape_completed_date'))

                    ]
                )

            csv_data = generate_data_csv(csv_header, csv_body, f"qc_report_data_{datetime.now()}_.csv")
            return Response({'csv_path': csv_data.get('csv_path')})

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


    def get_queryset(self):
        return Document.objects.annotate(
            barcode_length=Length('barcode_number')
        ).filter(
            barcode_number__isnull=False,
            barcode_length=21
        )
