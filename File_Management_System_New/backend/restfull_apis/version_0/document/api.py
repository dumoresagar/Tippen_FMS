from rest_framework import generics
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from django.db.models import Sum

from restfull_apis.version_0.permissions.guest import IsTrustedGuest
from .serializer import *
from rest_framework.views import APIView
from core.models import Document,DocumentStatus,PaginationMaster,MapType,DistrictTalukaAdmin,MissingDocument
from datetime import datetime
from users.models import User,Agency
from os.path import splitext
from django.core.files.uploadedfile import SimpleUploadedFile  # Import SimpleUploadedFile
from django.http import HttpResponse,Http404
from django.shortcuts import get_object_or_404
from users.models import Agency
from rest_framework.pagination import PageNumberPagination
from mimetypes import guess_type
import os
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.db.models import OuterRef, Subquery
from core.csv_utils import generate_data_csv,format_datetime
from urllib.parse import quote
from django.db.models import Q
from django.conf import settings
import pandas as pd
from datetime import datetime,timedelta
import io
import zipfile
from django.http import StreamingHttpResponse
import cv2
from pyzbar.pyzbar import decode
from django.http import JsonResponse
from math import ceil
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.exceptions import ObjectDoesNotExist
from io import BytesIO
from django.db.models import Count


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

# class CustomPageNumberPagination(PageNumberPagination):
#     page_size = 20
#     page_size_query_param = 'page_size'

#     def get_paginated_response(self, data):
#         return Response({
#             'count': self.page.paginator.count,
#             'per_page_count': self.page_size,  # Call the method with the request
#             'next': self.get_next_link(),
#             'previous': self.get_previous_link(),
#             'results': data
#         })





class UploadScanDocumentGenericAPI(generics.GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = UploadDocumentSerializer

    def post(self, request, format=None):
        serializer = UploadDocumentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(scan_uploaded_by=self.request.user,scan_uploaded_date=datetime.now())
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UploadRectifyDocumentGenericAPI(generics.GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = UploadDocumentSerializer
    
    def put(self,request,*args,**kwargs):
        try:
            rectify_obj = Document.objects.get(id=kwargs.get("pk"))
        except rectify_obj.DoesNotExist:
            return Response({"msg":"record does not exist"})
        serializer = UploadDocumentSerializer(rectify_obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(rectify_completed_date=datetime.now())
            return Response({"data":serializer.data,"message":"Success","status":True})
        return Response(serializer.errors)
    

class UploadDigitizeDocumentGenericAPI(generics.GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = UploadDocumentSerializer
    
    def put(self,request,*args,**kwargs):
        try:
            digitize_obj = Document.objects.get(id=kwargs.get("pk"))
        except digitize_obj.DoesNotExist:
            return Response({"msg":"record does not exist"})
        serializer = UploadDocumentSerializer(digitize_obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(digitize_completed_date=datetime.now())
            return Response({"data":serializer.data,"message":"Success","status":True})
        return Response(serializer.errors)
    
class UploadQcDocumentGenericAPI(generics.GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = UploadDocumentSerializer
    
    def put(self,request,*args,**kwargs):
        try:
            qc_obj = Document.objects.get(id=kwargs.get("pk"))
        except qc_obj.DoesNotExist:
            return Response({"msg":"record does not exist"})
        serializer = UploadDocumentSerializer(qc_obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(qc_completed_date=datetime.now())
            return Response({"data":serializer.data,"message":"Success","status":True})
        return Response(serializer.errors)
    
class UploadPdfDocumentGenericAPI(generics.GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = UploadDocumentSerializer
    
    def put(self,request,*args,**kwargs):
        try:
            pdf_obj = Document.objects.get(id=kwargs.get("pk"))
        except pdf_obj.DoesNotExist:
            return Response({"msg":"record does not exist"})
        serializer = UploadDocumentSerializer(pdf_obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(pdf_completed_date=datetime.now())
            return Response({"data":serializer.data,"message":"Success","status":True})
        return Response(serializer.errors)

class UploadShapeDocumentGenericAPI(generics.GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = UploadDocumentSerializer
    
    def put(self,request,*args,**kwargs):
        try:
            shape_obj = Document.objects.get(id=kwargs.get("pk"))
        except shape_obj.DoesNotExist:
            return Response({"msg":"record does not exist"})
        serializer = UploadDocumentSerializer(shape_obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(shape_completed_date=datetime.now())
            return Response({"data":serializer.data,"message":"Success","status":True})
        return Response(serializer.errors)
    

class ScanDocumentListView(ListAPIView):
    queryset = Document.objects.all()
    permission_classes = [IsAuthenticated,]
    authentication_classes = (TokenAuthentication,)
    serializer_class = ScanDocumentListSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend,filters.SearchFilter]
    search_fields = []
    filterset_fields = ['taluka_code']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)

        if request.GET.get('is_export') and request.GET.get('is_export') in ['1', 1]:
            for_count = 0
            csv_header = ['Sr.No', 'File Name','District','Taluka','Village','Map Code','Current Status','Remark']
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
                        qs.get('file_name'),
                        district_name,
                        taluka_name,
                        village_name,
                        qs.get('map_code'),
                        qs.get('current_status'),
                        qs.get('remarks',''),
                       
                    ]
                )

            csv_data = generate_data_csv(csv_header, csv_body, f"scan_report_{datetime.now()}_.csv")
            return Response({'csv_path': csv_data.get('csv_path')})

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        queryset = self.queryset
        agency_ids = User.objects.filter(id=self.request.user.id).values_list('agency', flat=True)
        if User.objects.filter(id=self.request.user.id, user_role__role_name="Super Admin"):
            query_set = queryset.filter(current_status=1).order_by('-date_created')
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Agency Admin"):
            query_set = queryset.filter(rectify_agency_id__in=agency_ids,current_status=3).exclude(rectify_by__isnull=False).order_by('-date_created')
        else:
            current_status_values = [1,3, 4, 7,11]
            query_set = queryset.filter(rectify_agency_id__in=agency_ids,rectify_by=self.request.user.id,current_status__in=current_status_values).order_by('-date_created')
        
        village_name = self.request.query_params.get('village_name', None)
        taluka_name = self.request.query_params.get('taluka_name', None)
        district_name = self.request.query_params.get('district_name', None)
        barcode_number = self.request.query_params.get('barcode_number', None)
        file_name = self.request.query_params.get('file_name', None)
        district_code = self.request.query_params.get('district_code', None)
        village_code = self.request.query_params.get('village_code', None)
        map_code = self.request.query_params.get('map_code', None)
        current_status = self.request.query_params.get('current_status', None)
        scan_by_username = self.request.query_params.get('scan_by_username', None)
        rectify_by_username = self.request.query_params.get('rectify_by_username', None)
        digitize_by_username = self.request.query_params.get('digitize_by_username', None)
        qc_by_username = self.request.query_params.get('qc_by_username', None)
        pdf_by_username = self.request.query_params.get('pdf_by_username', None)
        shape_by_username = self.request.query_params.get('shape_by_username', None)
        scan_start_date = self.request.query_params.get('scan_start_date',None)
        scan_end_date = self.request.query_params.get('scan_end_date',None)
        
        if scan_start_date and scan_end_date:
            scan_start_date = datetime.strptime(scan_start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
            scan_end_date = datetime.strptime(scan_end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query_set = query_set.filter(
                        scan_uploaded_date__gte=scan_start_date.date(),
                        scan_uploaded_date__lt=(scan_end_date.date() + timedelta(days=1)))
            
        
        if village_name:
            village_names = Village.objects.filter(village_name__icontains=village_name).values_list('village_code',flat=True)
            query_set = query_set.filter(village_code__in=village_names)
            

        if taluka_name:
            taluka_names = Taluka.objects.filter(taluka_name__icontains=taluka_name).values_list('taluka_code',flat=True)
            query_set = query_set.filter(taluka_code__in=taluka_names)


        if district_name:
            district_names = District.objects.filter(district_name__icontains=district_name).values_list('district_code',flat=True)
            query_set = query_set.filter(district_code__in=district_names)
        
        if barcode_number:
            query_set = query_set.filter(barcode_number__icontains=barcode_number)
        
        if file_name:
            query_set = query_set.filter(file_name__icontains=file_name)
            
        if district_code:
            query_set = query_set.filter(district_code__icontains=district_code)
        
        if village_code:
            query_set = query_set.filter(village_code__icontains=village_code)
       
        if map_code:
            query_set = query_set.filter(map_code__icontains=map_code)

        if scan_by_username:
            query_set = query_set.filter(scan_uploaded_by__username__icontains=scan_by_username)
        
        if rectify_by_username:
            query_set = query_set.filter(rectify_by__username__icontains=rectify_by_username)
            
        if digitize_by_username:
            query_set = query_set.filter(digitize_by__username__icontains=digitize_by_username)
            
        if qc_by_username:
            query_set = query_set.filter(qc_by__username__icontains=qc_by_username)
            
        if pdf_by_username:
            query_set = query_set.filter(pdf_by__username__icontains=pdf_by_username)
            
        if shape_by_username:
            query_set = query_set.filter(shape_by__username__icontains=shape_by_username)
        
        
        if current_status:
            query_set = query_set.filter(current_status__status__icontains=current_status)
        

        return query_set
    

class ScanRectifyListView(ListAPIView):
    queryset = Document.objects.all()
    permission_classes = [IsAuthenticated,]
    authentication_classes = (TokenAuthentication,)
    serializer_class = RectifyDocumentListSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend,filters.SearchFilter]
    search_fields = []
    filterset_fields = ['taluka_code']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)

        if request.GET.get('is_export') and request.GET.get('is_export') in ['1', 1]:
            for_count = 0
            csv_header = ['Sr.No', 'File Name','District','Taluka','Village','Map Code','Current Status','Remark']
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
                        qs.get('file_name'),
                        district_name,
                        taluka_name,
                        village_name,
                        qs.get('map_code'),
                        qs.get('current_status'),
                        qs.get('remarks',''),
                       
                    ]
                )

            csv_data = generate_data_csv(csv_header, csv_body, f"rectify_report_{datetime.now()}_.csv")
            return Response({'csv_path': csv_data.get('csv_path')})

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        queryset = self.queryset
        agency_ids = User.objects.filter(id=self.request.user.id).values_list('agency', flat=True)
        if User.objects.filter(id=self.request.user.id, user_role__role_name="Super Admin"):
            query_set = queryset.filter(current_status=5,digitize_agency_id__isnull=True).order_by('-date_created')
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Agency Admin"):
            current_status_values = [5,8]
            query_set = queryset.filter(digitize_agency_id__in=agency_ids,current_status__in=current_status_values).exclude(digitize_by__isnull=False).order_by('-date_created')
        else:
            current_status_values = [5,8,9,12,16]
            query_set = queryset.filter(digitize_agency_id__in=agency_ids,digitize_by=self.request.user.id,current_status__in=current_status_values).order_by('-date_created')
        
        village_name = self.request.query_params.get('village_name', None)
        taluka_name = self.request.query_params.get('taluka_name', None)
        district_name = self.request.query_params.get('district_name', None)
        barcode_number = self.request.query_params.get('barcode_number', None)
        file_name = self.request.query_params.get('file_name', None)
        district_code = self.request.query_params.get('district_code', None)
        village_code = self.request.query_params.get('village_code', None)
        map_code = self.request.query_params.get('map_code', None)
        current_status = self.request.query_params.get('current_status', None)
        scan_by_username = self.request.query_params.get('scan_by_username', None)
        rectify_by_username = self.request.query_params.get('rectify_by_username', None)
        digitize_by_username = self.request.query_params.get('digitize_by_username', None)
        qc_by_username = self.request.query_params.get('qc_by_username', None)
        pdf_by_username = self.request.query_params.get('pdf_by_username', None)
        shape_by_username = self.request.query_params.get('shape_by_username', None)
        rectify_start_date = self.request.query_params.get('rectify_start_date',None)
        rectify_end_date = self.request.query_params.get('rectify_end_date',None)
        rectify_agency_name = self.request.query_params.get('rectify_agency_name', None)

        if rectify_start_date and rectify_end_date:
            rectify_start_date = datetime.strptime(rectify_start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
            rectify_end_date = datetime.strptime(rectify_end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query_set = query_set.filter(
                        rectify_completed_date__gte=rectify_start_date.date(),
                        rectify_completed_date__lt=(rectify_end_date.date() + timedelta(days=1)))
        
        if rectify_agency_name:
            query_set = query_set.filter(rectify_agency_id__agency_name__icontains=rectify_agency_name)

        if village_name:
            village_names = Village.objects.filter(village_name__icontains=village_name).values_list('village_code',flat=True)
            query_set = query_set.filter(village_code__in=village_names)
            

        if taluka_name:
            taluka_names = Taluka.objects.filter(taluka_name__icontains=taluka_name).values_list('taluka_code',flat=True)
            query_set = query_set.filter(taluka_code__in=taluka_names)


        if district_name:
            district_names = District.objects.filter(district_name__icontains=district_name).values_list('district_code',flat=True)
            query_set = query_set.filter(district_code__in=district_names)
        
        
        if barcode_number:
            query_set = query_set.filter(barcode_number__icontains=barcode_number)
        
        if file_name:
            query_set = query_set.filter(file_name__icontains=file_name)
            
        if district_code:
            query_set = query_set.filter(district_code__icontains=district_code)
        
        if village_code:
            query_set = query_set.filter(village_code__icontains=village_code)
       
        if map_code:
            query_set = query_set.filter(map_code__icontains=map_code)

        if scan_by_username:
            query_set = query_set.filter(scan_uploaded_by__username__icontains=scan_by_username)
        
        if rectify_by_username:
            query_set = query_set.filter(rectify_by__username__icontains=rectify_by_username)
            
        if digitize_by_username:
            query_set = query_set.filter(digitize_by__username__icontains=digitize_by_username)
            
        if qc_by_username:
            query_set = query_set.filter(qc_by__username__icontains=qc_by_username)
            
        if pdf_by_username:
            query_set = query_set.filter(pdf_by__username__icontains=pdf_by_username)
            
        if shape_by_username:
            query_set = query_set.filter(shape_by__username__icontains=shape_by_username)
        
        
        if current_status:
            query_set = query_set.filter(current_status__status__icontains=current_status)
        
        
        return query_set



class UpdateFileCreateView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)
    serializer_class = UploadDocumentSerializer  # Use the custom serializer

    def put(self, request, *args, **kwargs):
        data = request.FILES.getlist('files')
        total_len = 0

        for file in data:
            filename = file.name
            base_filename = splitext(filename)[0]
            code = base_filename.split("_")[0]

            try:
                # Get the existing object based on the barcode
                obj = Document.objects.get(barcode_number=code)

                # Create a SimpleUploadedFile with the file data
                uploaded_file = SimpleUploadedFile(name=filename, content=file.read())

                # Create a dictionary with the data to update
                rectify_obj = self.request.user.id
                completed_date =datetime.now()
                update_data = {
                    'rectify_upload': uploaded_file,  # Pass the uploaded file data
                    "rectify_by":rectify_obj,
                    "rectify_completed_date":completed_date,
                    "current_status":5
                }

                serializer = self.get_serializer(obj, data=update_data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    total_len += 1
                else:
                    print(f"Error validating data for code {code}: {serializer.errors}")

            except Document.DoesNotExist:
                print(f"Object with barcode {code} does not exist.")

        return Response({"message": f"{total_len} Rectify Files Updated"}, status=status.HTTP_200_OK)
    

class ScanUploadDocumentView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)
    serializer_class = UploadScanDocumentSerializer
    # Use the custom serializer

    def post(self, request, *args, **kwargs):
        data = request.FILES.getlist('files')
        total_len = 0
        validation_errors = []
        uploaded_files = [] 
        allowed_extensions = ['.JPG','.JPEG','.jpeg','.jpg']  ###
    
        for file in data:
            filename = file.name
            base_filename,file_extension = os.path.splitext(filename)

          
            if file_extension.lower() not in allowed_extensions:  ###
                print(f"Skipping file {filename}: Only .JPEG files are allowed.")  ###
                continue                                                           ###
            code = base_filename.split("_")[0]

            try:
                # Create a SimpleUploadedFile with the file data
                new_filename = f"{base_filename}{file_extension}"
                uploaded_file = SimpleUploadedFile(name=new_filename, content=file.read())
                district_code = base_filename[:3]
                taluka_code = base_filename[3:7]
                village_code = base_filename[7:13]
                maptype_code = base_filename[13:15]

                try:
                    # Get the district name from the District model
                    district = District.objects.get(district_code=district_code)
                    taluka = Taluka.objects.get(taluka_code=taluka_code)
                    village = Village.objects.get(village_code=village_code)
                    maptype = MapType.objects.get(map_code=maptype_code)
                    status_code = 1
                except Exception:
                    status_code = 28


                # Create a dictionary with the data to update
                scan_upload_by = self.request.user.id
                completed_date =datetime.now()
                update_data = {
                    'scan_upload': uploaded_file,  # Pass the uploaded file data
                    "scan_uploaded_by":scan_upload_by,
                    "scan_uploaded_date":completed_date,
                    "current_status":status_code
                }

                serializer = self.get_serializer(data=update_data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    uploaded_files.append(new_filename)  # Add the uploaded file name to the list
                    total_len += 1
                else:
                    validation_errors.extend(serializer.errors.get('scan_upload', []))


            except Document.DoesNotExist:
                print(f"Object with barcode {code} does not exist.")
        if validation_errors:
            return Response({"message": f"{total_len} Scan Files Uploaded","Uploaded Files": uploaded_files, "errors": validation_errors}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": f"{total_len} Scan Files Uploaded","Uploaded Files": uploaded_files,}, status=status.HTTP_200_OK)
    

class ScanAssignToAgencyView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)
    serializer_class = UploadDocumentSerializer  # Use the custom serializer

    def put(self, request, *args, **kwargs):
        action = kwargs.get('action', None)
        agency_id = kwargs.get('agency_id')

        if action == 'rectify':
            try:
                agency_id = get_object_or_404(Agency, id=agency_id)
            except Http404:
                return Response({"message": f"Agency with ID {agency_id} does not exist"}, status=status.HTTP_404_NOT_FOUND)

            data = request.data.get('document_id', [])
            total_len = 0

            for file in data:
                assign_date =datetime.now()
                created_input_file = Document.objects.filter(id=file,rectify_agency_id__isnull=True).update(rectify_agency_id=agency_id,rectify_assign_date=assign_date,current_status=3)
                if created_input_file > 0:
                    total_len += 1
        elif action == 'digitize':
            try:
                agency_id = get_object_or_404(Agency, id=agency_id)
            except Http404:
                return Response({"message": f"Agency with ID {agency_id} does not exist"}, status=status.HTTP_404_NOT_FOUND)

            data = request.data.get('document_id', [])
            total_len = 0

            for file in data:
                assign_date =datetime.now()
                created_input_file = Document.objects.filter(id=file,rectify_agency_id__isnull=True).update(rectify_agency_id=agency_id,rectify_assign_date=assign_date,digitize_agency_id=agency_id,digitize_assign_date=assign_date,current_status=3)
                if created_input_file > 0:
                    total_len += 1
        elif action == 'qc':
            try:
                agency_id = get_object_or_404(Agency, id=agency_id)
            except Http404:
                return Response({"message": f"Agency with ID {agency_id} does not exist"}, status=status.HTTP_404_NOT_FOUND)

            data = request.data.get('document_id', [])
            total_len = 0

            for file in data:
                assign_date =datetime.now()
                created_input_file = Document.objects.filter(id=file,rectify_agency_id__isnull=True).update(rectify_agency_id=agency_id,rectify_assign_date=assign_date,digitize_agency_id=agency_id,digitize_assign_date=assign_date,qc_agency_id=agency_id,qc_assign_date=assign_date,current_status=3)
                if created_input_file > 0:
                    total_len += 1
        return Response({"message": f"{total_len} Scan Document Assign To Agency"}, status=status.HTTP_201_CREATED)
    

class RectifyAssignToAgencyView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)
    serializer_class = UploadDocumentSerializer  # Use the custom serializer

    def put(self, request, *args, **kwargs):
        agency_id = kwargs.get('agency_id')
        try:
            agency_id = get_object_or_404(Agency, id=agency_id)
        except Http404:
            return Response({"message": f"Agency with ID {agency_id} does not exist"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.get('document_id', [])
        total_len = 0

        for file in data:
            assign_date =datetime.now()
            created_input_file = Document.objects.filter(id=file,digitize_agency_id__isnull=True).update(digitize_agency_id=agency_id,digitize_assign_date=assign_date,current_status=8)
            if created_input_file > 0:
                total_len += 1
        return Response({"message": f"{total_len} Rectify Document Assign To Agency"}, status=status.HTTP_201_CREATED)

class DigitizeAssignToAgencyView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)
    serializer_class = UploadDocumentSerializer  # Use the custom serializer

    def put(self, request, *args, **kwargs):
        agency_id = kwargs.get('agency_id')
        try:
            agency_id = get_object_or_404(Agency, id=agency_id)
        except Http404:
            return Response({"message": f"Agency with ID {agency_id} does not exist"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.get('document_id', [])
        total_len = 0

        for file in data:
            assign_date =datetime.now()
            created_input_file = Document.objects.filter(id=file,qc_agency_id__isnull=True).update(qc_agency_id=agency_id,qc_assign_date=assign_date,current_status=13)
            if created_input_file > 0:
                total_len += 1
        return Response({"message": f"{total_len} Digitize Document Assign To Agency"}, status=status.HTTP_201_CREATED)

class TopologyAssignToAgencyView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)
    serializer_class = UploadDocumentSerializer  # Use the custom serializer

    def put(self, request, *args, **kwargs):
        agency_id = kwargs.get('agency_id')
        try:
            agency_id = get_object_or_404(Agency, id=agency_id)
        except Http404:
            return Response({"message": f"Agency with ID {agency_id} does not exist"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.get('document_id', [])
        total_len = 0

        for file in data:
            assign_date =datetime.now()
            created_input_file = Document.objects.filter(id=file).update(topology_agency_id=agency_id,shape_agency_id=agency_id,topology_assign_date=assign_date,current_status=31)
            total_len += 1

        return Response({"message": f"{total_len} Topology Document Assign To Agency"}, status=status.HTTP_201_CREATED)

class ShapeFileAssignToAgencyView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)
    serializer_class = UploadDocumentSerializer  # Use the custom serializer

    def put(self, request, *args, **kwargs):
        agency_id = kwargs.get('agency_id')
        try:
            agency_id = get_object_or_404(Agency, id=agency_id)
        except Http404:
            return Response({"message": f"Agency with ID {agency_id} does not exist"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.get('document_id', [])
        total_len = 0

        for file in data:
            assign_date =datetime.now()
            created_input_file = Document.objects.filter(id=file).update(shape_agency_id=agency_id,shape_assign_date=assign_date,current_status=23)
            total_len += 1

        return Response({"message": f"{total_len} Shape Document Assign To Agency"}, status=status.HTTP_201_CREATED)
    

class GovtQCAssignToAgencyView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)
    serializer_class = UploadDocumentSerializer  # Use the custom serializer

    def put(self, request, *args, **kwargs):
        agency_id = kwargs.get('agency_id')
        try:
            agency_id = get_object_or_404(Agency, id=agency_id)
        except Http404:
            return Response({"message": f"Agency with ID {agency_id} does not exist"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.get('document_id', [])
        total_len = 0

        for file in data:
            assign_date =datetime.now()
            created_input_file = Document.objects.filter(id=file).update(shape_agency_id=agency_id,shape_assign_date=assign_date,current_status=23)
            total_len += 1

        return Response({"message": f"{total_len} Digitize Document Assign To Agency"}, status=status.HTTP_201_CREATED)
    

class UploadDigitizeView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)
    serializer_class = UploadDocumentSerializer  # Use the custom serializer

    def put(self, request, *args, **kwargs):
        data = request.FILES.getlist('files')
        total_len = 0

        for file in data:
            filename = file.name
            base_filename = splitext(filename)[0]
            code = base_filename.split("_")[0]

            try:
                # Get the existing object based on the barcode
                obj = Document.objects.get(barcode_number=code)

                # Create a SimpleUploadedFile with the file data
                uploaded_file = SimpleUploadedFile(name=filename, content=file.read())

                # Create a dictionary with the data to update
                rectify_obj = self.request.user.id
                completed_date =datetime.now()
                update_data = {
                    'digitize_upload': uploaded_file,  # Pass the uploaded file data
                    "digitize_by":rectify_obj,
                    "digitize_completed_date":completed_date,
                    "current_status":10
                }

                serializer = self.get_serializer(obj, data=update_data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    total_len += 1
                else:
                    print(f"Error validating data for code {code}: {serializer.errors}")

            except Document.DoesNotExist:
                print(f"Object with barcode {code} does not exist.")

        return Response({"message": f"{total_len} Digitize Files Updated"}, status=status.HTTP_200_OK)


class UploadQcView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)
    serializer_class = UploadDocumentSerializer  # Use the custom serializer

    def put(self, request, *args, **kwargs):
        data = request.FILES.getlist('files')
        total_len = 0

        for file in data:
            filename = file.name
            base_filename = splitext(filename)[0]
            code = base_filename.split("_")[0]

            try:
                # Get the existing object based on the barcode
                obj = Document.objects.get(barcode_number=code)

                # Create a SimpleUploadedFile with the file data
                uploaded_file = SimpleUploadedFile(name=filename, content=file.read())

                # Create a dictionary with the data to update
                qc_obj = self.request.user.id
                completed_date =datetime.now()
                update_data = {
                    'qc_upload': uploaded_file,  # Pass the uploaded file data
                    "qc_by":qc_obj,
                    "qc_completed_date":completed_date,
                    "current_status":15
                }

                serializer = self.get_serializer(obj, data=update_data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    total_len += 1
                else:
                    print(f"Error validating data for code {code}: {serializer.errors}")

            except Document.DoesNotExist:
                print(f"Object with barcode {code} does not exist.")

        return Response({"message": f"{total_len} QC Files Updated"}, status=status.HTTP_200_OK)
    


class ScanAssignToAgencyUserView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)
    serializer_class = UploadDocumentSerializer  # Use the custom serializer

    def put(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id')
        user_agency = User.objects.filter(id=user_id).values_list('agency', flat=True).first()

      
        try:
            user_id = get_object_or_404(User, id=user_id)
        except Http404:
            return Response({"message": f"Agency with ID {user_id} does not exist"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.get('document_id', [])
        total_len = 0

        for file in data:
            assign_date =datetime.now()
            documentz_agency= Document.objects.filter(id=file).values_list('rectify_agency_id', flat=True).first()

            if documentz_agency == user_agency:
                created_input_file = Document.objects.filter(id=file,rectify_by__isnull=True).update(rectify_by=user_id,rectify_assign_date=assign_date)
                if created_input_file > 0:
                    total_len += 1
            else:
                return Response({"message": "You do not have permission to assign documents to this user."}, status=status.HTTP_403_FORBIDDEN)

        return Response({"message": f"{total_len} Scan Document Assign To User"}, status=status.HTTP_201_CREATED)

class RectifyAssignToAgencyUserView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)
    serializer_class = UploadDocumentSerializer  # Use the custom serializer

    def put(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id')
        user_agency = User.objects.filter(id=user_id).values_list('agency', flat=True).first()
       

        try:
            user_id = get_object_or_404(User, id=user_id)
        except Http404:
            return Response({"message": f"Agency with ID {user_id} does not exist"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.get('document_id', [])
        total_len = 0

        for file in data:
            assign_date =datetime.now()
            documentz_agency= Document.objects.filter(id=file).values_list('digitize_agency_id', flat=True).first()
            if documentz_agency == user_agency:
                created_input_file = Document.objects.filter(id=file,digitize_by__isnull=True).update(digitize_by=user_id,digitize_assign_date=assign_date)
                if created_input_file > 0:
                    total_len += 1
            else:
                return Response({"message": "You do not have permission to assign documents to this user."}, status=status.HTTP_403_FORBIDDEN)


        return Response({"message": f"{total_len} Rectify Document Assign To User"}, status=status.HTTP_201_CREATED)

class DigitizeAssignToAgencyUserView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)
    serializer_class = UploadDocumentSerializer  # Use the custom serializer

    def put(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id')
        user_agency = User.objects.filter(id=user_id).values_list('agency', flat=True).first()

        try:
            user_id = get_object_or_404(User, id=user_id)
        except Http404:
            return Response({"message": f"Agency with ID {user_id} does not exist"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.get('document_id', [])
        total_len = 0

        for file in data:
            assign_date =datetime.now()
            documentz_agency= Document.objects.filter(id=file).values_list('qc_agency_id', flat=True).first()
            if documentz_agency == user_agency:
                created_input_file = Document.objects.filter(id=file,qc_by__isnull=True).update(qc_by=user_id,qc_assign_date=assign_date)
                if created_input_file > 0:
                    total_len += 1
            else:
                return Response({"message": "You do not have permission to assign documents to this user."}, status=status.HTTP_403_FORBIDDEN)

        return Response({"message": f"{total_len} Digitize Document Assign To User"}, status=status.HTTP_201_CREATED)

######################################
class ScanReAssignToAgencyUserView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)
    serializer_class = UploadDocumentSerializer  # Use the custom serializer

    def put(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id')
        user_agency = User.objects.filter(id=user_id).values_list('agency', flat=True).first()

      
        try:
            user_id = get_object_or_404(User, id=user_id)
        except Http404:
            return Response({"message": f"Agency with ID {user_id} does not exist"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.get('document_id', [])
        total_len = 0

        for file in data:
            assign_date =datetime.now()
            documentz_agency= Document.objects.filter(id=file).values_list('rectify_agency_id', flat=True).first()

            if documentz_agency == user_agency:
                created_input_file = Document.objects.filter(id=file,rectify_completed_date__isnull=True).update(rectify_by=user_id,rectify_assign_date=assign_date)
                if created_input_file > 0:
                    total_len += 1
            else:
                return Response({"message": "You do not have permission to assign documents to this user."}, status=status.HTTP_403_FORBIDDEN)

        return Response({"message": f"{total_len} Scan Document Assign To User"}, status=status.HTTP_201_CREATED)

class RectifyReAssignToAgencyUserView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)
    serializer_class = UploadDocumentSerializer  # Use the custom serializer

    def put(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id')
        user_agency = User.objects.filter(id=user_id).values_list('agency', flat=True).first()
       

        try:
            user_id = get_object_or_404(User, id=user_id)
        except Http404:
            return Response({"message": f"Agency with ID {user_id} does not exist"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.get('document_id', [])
        total_len = 0

        for file in data:
            assign_date =datetime.now()
            documentz_agency= Document.objects.filter(id=file).values_list('digitize_agency_id', flat=True).first()
            if documentz_agency == user_agency:
                created_input_file = Document.objects.filter(id=file,digitize_completed_date__isnull=True).update(digitize_by=user_id,digitize_assign_date=assign_date)
                if created_input_file > 0:
                    total_len += 1
            else:
                return Response({"message": "You do not have permission to assign documents to this user."}, status=status.HTTP_403_FORBIDDEN)


        return Response({"message": f"{total_len} Rectify Document Assign To User"}, status=status.HTTP_201_CREATED)

class DigitizeReAssignToAgencyUserView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)
    serializer_class = UploadDocumentSerializer  # Use the custom serializer

    def put(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id')
        user_agency = User.objects.filter(id=user_id).values_list('agency', flat=True).first()

        try:
            user_id = get_object_or_404(User, id=user_id)
        except Http404:
            return Response({"message": f"Agency with ID {user_id} does not exist"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.get('document_id', [])
        total_len = 0

        for file in data:
            assign_date =datetime.now()
            documentz_agency= Document.objects.filter(id=file).values_list('qc_agency_id', flat=True).first()
            if documentz_agency == user_agency:
                created_input_file = Document.objects.filter(id=file,qc_completed_date__isnull=True).update(qc_by=user_id,qc_assign_date=assign_date)
                if created_input_file > 0:
                    total_len += 1
            else:
                return Response({"message": "You do not have permission to assign documents to this user."}, status=status.HTTP_403_FORBIDDEN)

        return Response({"message": f"{total_len} Digitize Document Assign To User"}, status=status.HTTP_201_CREATED)

#############################################
    
class GovtQCAssignToAgencyUserView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)
    serializer_class = UploadDocumentSerializer  # Use the custom serializer

    def put(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id')
        try:
            user_id = get_object_or_404(User, id=user_id)
        except Http404:
            return Response({"message": f"Agency with ID {user_id} does not exist"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.get('document_id', [])
        total_len = 0

        for file in data:
            assign_date =datetime.now()
            created_input_file = Document.objects.filter(id=file).update(shape_by=user_id,shape_assign_date=assign_date)
            total_len += 1

        return Response({"message": f"{total_len} Digitize Document Assign To User"}, status=status.HTTP_201_CREATED)

class TopologyFileAssignToAgencyUserView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)
    serializer_class = UploadDocumentSerializer  # Use the custom serializer

    def put(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id')
        try:
            user_id = get_object_or_404(User, id=user_id)
        except Http404:
            return Response({"message": f"Agency with ID {user_id} does not exist"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.get('document_id', [])
        total_len = 0

        for file in data:
            assign_date =datetime.now()
            created_input_file = Document.objects.filter(id=file,topology_by__isnull=True).update(topology_by=user_id,topology_assign_date=assign_date)
            if created_input_file > 0:
                total_len += 1

        return Response({"message": f"{total_len} Topology Document Assign To User"}, status=status.HTTP_201_CREATED)

class ShapeFileAssignToAgencyUserView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)
    serializer_class = UploadDocumentSerializer  # Use the custom serializer

    def put(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id')
        try:
            user_id = get_object_or_404(User, id=user_id)
        except Http404:
            return Response({"message": f"Agency with ID {user_id} does not exist"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.get('document_id', [])
        total_len = 0

        for file in data:
            assign_date =datetime.now()
            created_input_file = Document.objects.filter(id=file).update(shape_by=user_id,shape_assign_date=assign_date)
            total_len += 1

        return Response({"message": f"{total_len} Shape Document Assign To User"}, status=status.HTTP_201_CREATED)
class ScanDigitizeListView(ListAPIView):
    queryset = Document.objects.all()
    permission_classes = [IsAuthenticated,]
    authentication_classes = (TokenAuthentication,)
    serializer_class = DigitizeDocumentListSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend,filters.SearchFilter]
    search_fields = []
    filterset_fields = ['taluka_code']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)

        if request.GET.get('is_export') and request.GET.get('is_export') in ['1', 1]:
            for_count = 0
            csv_header = ['Sr.No', 'File Name','District','Taluka','Village','Map Code','Polygon_Count','Current Status','Remark']
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
                        qs.get('file_name'),
                        district_name,
                        taluka_name,
                        village_name,
                        qs.get('map_code'),
                        qs.get('polygon_count'),
                        qs.get('current_status'),
                        qs.get('remarks',''),
                       
                    ]
                )

            csv_data = generate_data_csv(csv_header, csv_body, f"digitize_report_{datetime.now()}_.csv")
            return Response({'csv_path': csv_data.get('csv_path')})

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        queryset = self.queryset
        agency_ids = User.objects.filter(id=self.request.user.id).values_list('agency', flat=True)
        if User.objects.filter(id=self.request.user.id, user_role__role_name="Super Admin"):
            query_set = queryset.filter(current_status=10).order_by('-date_created')
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Agency Admin"):
            query_set = queryset.filter(qc_agency_id__in=agency_ids,current_status=13).exclude(qc_by__isnull=False).order_by('-date_created')
        else:
            current_status_values = [10,13,14,17,21]
            query_set = queryset.filter(qc_agency_id__in=agency_ids,qc_by=self.request.user.id,current_status__in=current_status_values).order_by('-date_created')
        
        village_name = self.request.query_params.get('village_name', None)
        taluka_name = self.request.query_params.get('taluka_name', None)
        district_name = self.request.query_params.get('district_name', None)
        barcode_number = self.request.query_params.get('barcode_number', None)
        file_name = self.request.query_params.get('file_name', None)
        district_code = self.request.query_params.get('district_code', None)
        village_code = self.request.query_params.get('village_code', None)
        map_code = self.request.query_params.get('map_code', None)
        current_status = self.request.query_params.get('current_status', None)
        scan_by_username = self.request.query_params.get('scan_by_username', None)
        rectify_by_username = self.request.query_params.get('rectify_by_username', None)
        digitize_by_username = self.request.query_params.get('digitize_by_username', None)
        qc_by_username = self.request.query_params.get('qc_by_username', None)
        digitize_start_date = self.request.query_params.get('digitize_start_date',None)
        digitize_end_date = self.request.query_params.get('digitize_end_date',None)
        digitize_agency_name = self.request.query_params.get('digitize_agency_name', None)
        polygon_min = self.request.query_params.get('polygon_min', None)
        polygon_max = self.request.query_params.get('polygon_max', None)


        if digitize_start_date and digitize_end_date:
            digitize_start_date = datetime.strptime(digitize_start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
            digitize_end_date = datetime.strptime(digitize_end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query_set = query_set.filter(
                        digitize_completed_date__gte=digitize_start_date.date(),
                        digitize_completed_date__lt=(digitize_end_date.date() + timedelta(days=1)))
        
        if polygon_min and polygon_max:
            try:
                polygon_min = int(polygon_min)
                polygon_max = int(polygon_max)
                query_set = query_set.filter(polygon_count__range=(polygon_min, polygon_max))
            except ValueError:
                query_set = query_set.none()  # Return an empty queryset
            
        if digitize_agency_name:
            query_set = query_set.filter(digitize_agency_id__agency_name__icontains=digitize_agency_name)

        
        if village_name:
            village_names = Village.objects.filter(village_name__icontains=village_name).values_list('village_code',flat=True)
            query_set = query_set.filter(village_code__in=village_names)
            

        if taluka_name:
            taluka_names = Taluka.objects.filter(taluka_name__icontains=taluka_name).values_list('taluka_code',flat=True)
            query_set = query_set.filter(taluka_code__in=taluka_names)


        if district_name:
            district_names = District.objects.filter(district_name__icontains=district_name).values_list('district_code',flat=True)
            query_set = query_set.filter(district_code__in=district_names)
        
        
        if barcode_number:
            query_set = query_set.filter(barcode_number__icontains=barcode_number)
        
        if file_name:
            query_set = query_set.filter(file_name__icontains=file_name)
            
        if district_code:
            query_set = query_set.filter(district_code__icontains=district_code)
        
        if village_code:
            query_set = query_set.filter(village_code__icontains=village_code)
       
        if map_code:
            query_set = query_set.filter(map_code__icontains=map_code)
        
        if scan_by_username:
            query_set = query_set.filter(scan_uploaded_by__username__icontains=scan_by_username)
        
        if rectify_by_username:
            query_set = query_set.filter(rectify_by__username__icontains=rectify_by_username)
            
        if digitize_by_username:
            query_set = query_set.filter(digitize_by__username__icontains=digitize_by_username)
            
        if qc_by_username:
            query_set = query_set.filter(qc_by__username__icontains=qc_by_username)
            
        if current_status:
            query_set = query_set.filter(current_status__status__icontains=current_status)
        
        return query_set
    
class ScanQcListView(ListAPIView):
    queryset = Document.objects.all()
    permission_classes = [IsAuthenticated,]
    authentication_classes = (TokenAuthentication,)
    serializer_class = QcDocumentListSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend,filters.SearchFilter]
    search_fields = []
    filterset_fields = ['taluka_code']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)

        if request.GET.get('is_export') and request.GET.get('is_export') in ['1', 1]:
            for_count = 0
            csv_header = ['Sr.No', 'File Name','District','Taluka','Village','Map Code','Current Status','Remark']
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
                        qs.get('file_name'),
                        district_name,
                        taluka_name,
                        village_name,
                        qs.get('map_code'),
                        qs.get('current_status'),
                        qs.get('remarks',''),
                       
                    ]
                )

            csv_data = generate_data_csv(csv_header, csv_body, f"qc_report_{datetime.now()}_.csv")
            return Response({'csv_path': csv_data.get('csv_path')})

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        queryset = self.queryset
        agency_ids = User.objects.filter(id=self.request.user.id).values_list('agency', flat=True)
        if User.objects.filter(id=self.request.user.id, user_role__role_name="Super Admin"):
            query_set = queryset.filter(current_status=15).order_by('-date_created')
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Agency Admin"):
            query_set = queryset.filter(qc_agency_id__in=agency_ids,current_status=15).order_by('-date_created')
        else:
            current_status_values = [15,18,19,22]
            query_set = queryset.filter(qc_agency_id__in=agency_ids,pdf_by=self.request.user.id,current_status__in=current_status_values).order_by('-date_created')

        village_name = self.request.query_params.get('village_name', None)
        taluka_name = self.request.query_params.get('taluka_name', None)
        district_name = self.request.query_params.get('district_name', None)
        barcode_number = self.request.query_params.get('barcode_number', None)
        file_name = self.request.query_params.get('file_name', None)
        district_code = self.request.query_params.get('district_code', None)
        village_code = self.request.query_params.get('village_code', None)
        map_code = self.request.query_params.get('map_code', None)
        current_status = self.request.query_params.get('current_status', None)
        scan_by_username = self.request.query_params.get('scan_by_username', None)
        rectify_by_username = self.request.query_params.get('rectify_by_username', None)
        digitize_by_username = self.request.query_params.get('digitize_by_username', None)
        qc_by_username = self.request.query_params.get('qc_by_username', None)
        pdf_by_username = self.request.query_params.get('pdf_by_username', None)
        shape_by_username = self.request.query_params.get('shape_by_username', None)
        qc_start_date = self.request.query_params.get('qc_start_date',None)
        qc_end_date = self.request.query_params.get('qc_end_date',None)
        polygon_min = self.request.query_params.get('polygon_min', None)
        polygon_max = self.request.query_params.get('polygon_max', None)

        if qc_start_date and qc_end_date:
            qc_start_date = datetime.strptime(qc_start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
            qc_end_date = datetime.strptime(qc_end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query_set = query_set.filter(
                        qc_completed_date__gte=qc_start_date.date(),
                        qc_completed_date__lt=(qc_end_date.date() + timedelta(days=1)))
            
        if polygon_min and polygon_max:
            try:
                polygon_min = int(polygon_min)
                polygon_max = int(polygon_max)
                query_set = query_set.filter(polygon_count__range=(polygon_min, polygon_max))
            except ValueError:
                query_set = query_set.none()  # Return an empty queryset


        if village_name:
            village_names = Village.objects.filter(village_name__icontains=village_name).values_list('village_code',flat=True)
            query_set = query_set.filter(village_code__in=village_names)
            

        if taluka_name:
            taluka_names = Taluka.objects.filter(taluka_name__icontains=taluka_name).values_list('taluka_code',flat=True)
            query_set = query_set.filter(taluka_code__in=taluka_names)


        if district_name:
            district_names = District.objects.filter(district_name__icontains=district_name).values_list('district_code',flat=True)
            query_set = query_set.filter(district_code__in=district_names)
        
        
        if barcode_number:
            query_set = query_set.filter(barcode_number__icontains=barcode_number)
        
        if file_name:
            query_set = query_set.filter(file_name__icontains=file_name)
            
        if district_code:
            query_set = query_set.filter(district_code__icontains=district_code)
        
        if village_code:
            query_set = query_set.filter(village_code__icontains=village_code)
       
        if map_code:
            query_set = query_set.filter(map_code__icontains=map_code)

        
        if scan_by_username:
            query_set = query_set.filter(scan_uploaded_by__username__icontains=scan_by_username)
        
        if rectify_by_username:
            query_set = query_set.filter(rectify_by__username__icontains=rectify_by_username)
            
        if digitize_by_username:
            query_set = query_set.filter(digitize_by__username__icontains=digitize_by_username)
            
        if qc_by_username:
            query_set = query_set.filter(qc_by__username__icontains=qc_by_username)
            
        if pdf_by_username:
            query_set = query_set.filter(pdf_by__username__icontains=pdf_by_username)
            
        if shape_by_username:
            query_set = query_set.filter(shape_by__username__icontains=shape_by_username)
        
        
        if current_status:
            query_set = query_set.filter(current_status__status__icontains=current_status)

        return query_set
    
class ScanPdfListView(ListAPIView):
    queryset = Document.objects.all()
    permission_classes = [IsAuthenticated,]
    authentication_classes = (TokenAuthentication,)
    serializer_class = PdfDocumentListSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend,filters.SearchFilter]
    search_fields = []
    filterset_fields = ['taluka_code']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)

        if request.GET.get('is_export') and request.GET.get('is_export') in ['1', 1]:
            for_count = 0
            csv_header = ['Sr.No', 'File Name','District','Taluka','Village','Map Code','Current Status','Remark']
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
                        qs.get('file_name'),
                        district_name,
                        taluka_name,
                        village_name,
                        qs.get('map_code'),
                        qs.get('current_status'),
                        qs.get('remarks',''),
                       
                    ]
                )

            csv_data = generate_data_csv(csv_header, csv_body, f"pdf_report_{datetime.now()}_.csv")
            return Response({'csv_path': csv_data.get('csv_path')})

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        queryset = self.queryset
        agency_ids = User.objects.filter(id=self.request.user.id).values_list('agency', flat=True)
        if User.objects.filter(id=self.request.user.id, user_role__role_name="Super Admin"):
            query_set = queryset.filter(current_status=20).order_by('-date_created')
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Agency Admin"):
            query_set = queryset.filter(qc_agency_id__in=agency_ids,current_status=20).order_by('-date_created')
        else:
            current_status_values = [23,24,27]
            query_set = queryset.filter(qc_agency_id__in=agency_ids,shape_by=self.request.user.id,current_status__in=current_status_values).order_by('-date_created')
        
        village_name = self.request.query_params.get('village_name', None)
        taluka_name = self.request.query_params.get('taluka_name', None)
        district_name = self.request.query_params.get('district_name', None)
        barcode_number = self.request.query_params.get('barcode_number', None)
        file_name = self.request.query_params.get('file_name', None)
        district_code = self.request.query_params.get('district_code', None)
        village_code = self.request.query_params.get('village_code', None)
        map_code = self.request.query_params.get('map_code', None)
        current_status = self.request.query_params.get('current_status', None)

        
        if village_name:
            village_names = Village.objects.filter(village_name__icontains=village_name).values_list('village_code',flat=True)
            query_set = query_set.filter(village_code__in=village_names)
            

        if taluka_name:
            taluka_names = Taluka.objects.filter(taluka_name__icontains=taluka_name).values_list('taluka_code',flat=True)
            query_set = query_set.filter(taluka_code__in=taluka_names)


        if district_name:
            district_names = District.objects.filter(district_name__icontains=district_name).values_list('district_code',flat=True)
            query_set = query_set.filter(district_code__in=district_names)
        
        
        if barcode_number:
            query_set = query_set.filter(barcode_number__icontains=barcode_number)
        
        if file_name:
            query_set = query_set.filter(file_name__icontains=file_name)
            
        if district_code:
            query_set = query_set.filter(district_code__icontains=district_code)
        
        if village_code:
            query_set = query_set.filter(village_code__icontains=village_code)
       
        if map_code:
            query_set = query_set.filter(map_code__icontains=map_code)
        
        if current_status:
            query_set = query_set.filter(current_status__status__icontains=current_status)

        return query_set

class UploadPdfView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)
    serializer_class = UploadDocumentSerializer  # Use the custom serializer

    def put(self, request, *args, **kwargs):
        data = request.FILES.getlist('files')
        total_len = 0

        for file in data:
            filename = file.name
            base_filename = splitext(filename)[0]
            code = base_filename.split("_")[0]

            try:
                # Get the existing object based on the barcode
                obj = Document.objects.get(barcode_number=code)

                # Create a SimpleUploadedFile with the file data
                uploaded_file = SimpleUploadedFile(name=filename, content=file.read())

                # Create a dictionary with the data to update
                pdf_obj = self.request.user.id
                completed_date =datetime.now()
                update_data = {
                    'pdf_upload': uploaded_file,  # Pass the uploaded file data
                    "pdf_by":pdf_obj,
                    "pdf_completed_date":completed_date,
                    "current_status":20
                }

                serializer = self.get_serializer(obj, data=update_data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    total_len += 1
                else:
                    print(f"Error validating data for code {code}: {serializer.errors}")

            except Document.DoesNotExist:
                print(f"Object with barcode {code} does not exist.")

        return Response({"message": f"{total_len} Pdf Files Updated"}, status=status.HTTP_200_OK)
    
class UploadShapeView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)
    serializer_class = UploadDocumentSerializer  # Use the custom serializer

    def put(self, request, *args, **kwargs):
        data = request.FILES.getlist('files')
        total_len = 0

        for file in data:
            filename = file.name
            base_filename = splitext(filename)[0]
            code = base_filename.split("_")[0]

            try:
                # Get the existing object based on the barcode
                obj = Document.objects.get(barcode_number=code)

                # Create a SimpleUploadedFile with the file data
                uploaded_file = SimpleUploadedFile(name=filename, content=file.read())

                # Create a dictionary with the data to update
                shape_obj = self.request.user.id
                completed_date =datetime.now()
                update_data = {
                    'shape_upload': uploaded_file,  # Pass the uploaded file data
                    "shape_by":shape_obj,
                    "shape_completed_date":completed_date,
                    "current_status":25
                }

                serializer = self.get_serializer(obj, data=update_data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    total_len += 1
                else:
                    print(f"Error validating data for code {code}: {serializer.errors}")

            except Document.DoesNotExist:
                print(f"Object with barcode {code} does not exist.")

        return Response({"message": f"{total_len} Pdf Files Updated"}, status=status.HTTP_200_OK)

class UserListView(ListAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated,]
    authentication_classes = (TokenAuthentication,)
    serializer_class = UserListSerializer

    def get_queryset(self):
        queryset = self.queryset
        query_set = queryset.all().order_by('-date_created')
        return query_set
    
class AgencyListView(ListAPIView):
    queryset = Agency.objects.all()
    permission_classes = [IsAuthenticated,]
    authentication_classes = (TokenAuthentication,)
    serializer_class = AgencyListSerializer


    @method_decorator(cache_page(600))  # Cache for 10 minutes
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    
    def get_queryset(self):
        queryset = self.queryset
        team_ids = User.objects.filter(id=self.request.user.id).values_list('agency__team', flat=True)
        agencyadmin_list=User.objects.filter(active_status='Active',user_role__role_name="Agency Admin").values_list('agency',flat=True)
        if User.objects.filter(id=self.request.user.id, user_role__role_name="Super Admin"):
            query_set = queryset.filter(id__in=agencyadmin_list).order_by('-date_created')
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Team Admin"):
            query_set = queryset.filter(team__in=team_ids).order_by('-date_created')
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="User"):
            query_set = queryset.filter(team__in=team_ids).order_by('-date_created')
        return query_set
    
class UpdateAgencyListView(ListAPIView):
    queryset = Agency.objects.all()
    permission_classes = [IsAuthenticated,]
    authentication_classes = (TokenAuthentication,)
    serializer_class = AgencyListSerializer

    def get_queryset(self):
        queryset = self.queryset
        team_ids = User.objects.filter(id=self.request.user.id).values_list('agency__team', flat=True)
        if User.objects.filter(id=self.request.user.id, user_role__role_name="Super Admin"):
            query_set = queryset.all().order_by('-date_created')
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Team Admin"):
            query_set = queryset.filter(team__in=team_ids).order_by('-date_created')
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="User"):
            query_set = queryset.filter(team__in=team_ids).order_by('-date_created')
        return query_set
class AgencyWiseListView(ListAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated,]
    authentication_classes = (TokenAuthentication,)
    serializer_class = UserListSerializer
    pagination_class = CustomPageNumberPagination

  

    def get_queryset(self):
        queryset = self.queryset
        agency_ids = User.objects.filter(id=self.request.user.id).values_list('agency', flat=True)
        query_set = queryset.filter(agency__in=agency_ids).exclude(user_role__in=[1,3]).order_by('-date_created')
        return query_set

class DistrictAdminWiseListView(ListAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated,]
    authentication_classes = (TokenAuthentication,)
    serializer_class = DistrictAdminUserListSerializer

    @method_decorator(cache_page(300))  # Cache for 10 minutes
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        queryset = self.queryset
        query_set = queryset.filter(user_role=5).order_by('-date_created')
        return query_set
    
# def scan_download_file(request, document_id):
#     try:
#         download_file = get_object_or_404(Document, id=document_id)
#         file_path = download_file.scan_upload.path
#         content_type, _ = guess_type(file_path)

#         with open(file_path, 'rb') as file:
#             response = HttpResponse(file.read(), content_type=content_type)
            
#             # Get the original filename from the path
#             original_filename = os.path.basename(file_path)
#             modified_filename = original_filename.replace("_O", "")

#             # Set the Content-Disposition header with the original filename
#             response['Content-Disposition'] = f'attachment; filename="{quote(modified_filename)}"'

#             # Update the status here if needed
#             update_status = Document.objects.filter(id=download_file.id).update(current_status=4)
            
#             return response
#     except Document.DoesNotExist:
#         raise Http404("Document does not exist")
#     except Exception:
#         return HttpResponse('Scan Document File Does Not Exist', status=404)

def scan_download_file(request, document_id):
    try:
        download_file = get_object_or_404(Document, id=document_id)
        file_path = download_file.scan_upload.path
        content_type, _ = guess_type(file_path)

        with open(file_path, 'rb') as file:
            response = HttpResponse(file.read(), content_type=content_type)
            
            # Get the original filename from the path
            barcode = download_file.barcode_number
            original_filename = os.path.basename(file_path)
            prefix, extension = os.path.splitext(original_filename)#
            modified_filename = barcode + extension


            # Set the Content-Disposition header with the original filename
            response['Content-Disposition'] = f'attachment; filename="{quote(modified_filename)}"'

            
            return response
    except Document.DoesNotExist:
        raise Http404("Document does not exist")
    except Exception:
        return HttpResponse('Scan Document File Does Not Exist', status=404)
    
def rectify_download_file(request, document_id):
    try:
        download_file = get_object_or_404(Document, id=document_id)
        file_path = download_file.rectify_upload.path
        content_type, _ = guess_type(file_path)

        with open(file_path, 'rb') as file:
            response = HttpResponse(file.read(), content_type=content_type)
            
            # Get the original filename from the path
            barcode = download_file.barcode_number
            original_filename = os.path.basename(file_path)
            prefix, extension = os.path.splitext(original_filename)#
            modified_filename = barcode + extension
            # Set the Content-Disposition header with the original filename
            response['Content-Disposition'] = f'attachment; filename="{quote(modified_filename)}"'

            # Update the status here if needed
            # update_status = Document.objects.filter(id=download_file.id).update(current_status=9)
            
            return response
    except Document.DoesNotExist:
        raise Http404("Document does not exist")
    except Exception:
        return HttpResponse('Rectify Document File Does Not Exist', status=404)

def topology_rectify_download_file(request, document_id):
    try:
        download_file = get_object_or_404(Document, id=document_id)
        file_path = download_file.rectify_upload.path
        content_type, _ = guess_type(file_path)

        with open(file_path, 'rb') as file:
            response = HttpResponse(file.read(), content_type=content_type)
            
            # Get the original filename from the path
            barcode = download_file.barcode_number
            original_filename = os.path.basename(file_path)
            prefix, extension = os.path.splitext(original_filename)#
            modified_filename = barcode + extension         
            # Set the Content-Disposition header with the original filename
            response['Content-Disposition'] = f'attachment; filename="{quote(modified_filename)}"'

            
            return response
    except Document.DoesNotExist:
        raise Http404("Document does not exist")
    except Exception:
        return HttpResponse('Rectify Document File Does Not Exist', status=404)
    
def digitize_download_file(request, document_id):
    try:
        download_file = get_object_or_404(Document, id=document_id)
        file_path = download_file.digitize_upload.path
        content_type, _ = guess_type(file_path)

        with open(file_path, 'rb') as file:
            response = HttpResponse(file.read(), content_type=content_type)
            
            # Get the original filename from the path
            original_filename = os.path.basename(file_path)
            modified_filename = original_filename.replace("_D", "")

            # Set the Content-Disposition header with the original filename
            response['Content-Disposition'] = f'attachment; filename="{quote(modified_filename)}"'

            # Update the status here if needed
            # update_status = Document.objects.filter(id=download_file.id).update(current_status=14)
            
            return response
    except Document.DoesNotExist:
        raise Http404("Digitize does not exist")
    except Exception:
        return HttpResponse('Digitize Document File Does Not Exist', status=404)

def qc_download_file(request, document_id):
    try:
        download_file = get_object_or_404(Document, id=document_id)
        file_path = download_file.qc_upload.path
        content_type, _ = guess_type(file_path)

        with open(file_path, 'rb') as file:
            response = HttpResponse(file.read(), content_type=content_type)
            
            # Get the original filename from the path
            original_filename = os.path.basename(file_path)
            modified_filename = original_filename.replace("_Q", "")

            # Set the Content-Disposition header with the original filename
            response['Content-Disposition'] = f'attachment; filename="{quote(modified_filename)}"'

            # Update the status here if needed
            # update_status = Document.objects.filter(id=download_file.id).update(current_status=19)
            
            return response
    except Document.DoesNotExist:
        raise Http404("Qc does not exist")
    except Exception:
        return HttpResponse('Qc Document File Does Not Exist', status=404)


def pdf_download_file(request, document_id):
    try:
        download_file = get_object_or_404(Document, id=document_id)
        file_path = download_file.pdf_upload.path
        content_type, _ = guess_type(file_path)

        with open(file_path, 'rb') as file:
            response = HttpResponse(file.read(), content_type=content_type)
            
            # Get the original filename from the path
            original_filename = os.path.basename(file_path)
            modified_filename = original_filename.replace("_P", "")

            # Set the Content-Disposition header with the original filename
            response['Content-Disposition'] = f'attachment; filename="{quote(modified_filename)}"'

            # Update the status here if needed
            # update_status = Document.objects.filter(id=download_file.id).update(current_status=24)
            
            return response
    except Document.DoesNotExist:
        raise Http404("Pdf does not exist")
    except Exception:
        return HttpResponse('Pdf Document File Does Not Exist', status=404)
    
def shape_download_file(request, document_id):
    try:
        download_file = get_object_or_404(Document, id=document_id)
        file_path = download_file.shape_upload.path
        content_type, _ = guess_type(file_path)

        with open(file_path, 'rb') as file:
            response = HttpResponse(file.read(), content_type=content_type)
            
            # Get the original filename from the path
            original_filename = os.path.basename(file_path)
            modified_filename = original_filename.replace("_S", "")

            # Set the Content-Disposition header with the original filename
            response['Content-Disposition'] = f'attachment; filename="{quote(modified_filename)}"'
            return response
    except Document.DoesNotExist:
        raise Http404("Shape does not exist")
    except Exception:
        return HttpResponse('Shape Document File Does Not Exist', status=404)
    
def gov_pdf_completed_download_file(request, document_id):
    try:
        download_file = get_object_or_404(Document, id=document_id)
        file_path = download_file.gov_qc_upload.path
        content_type, _ = guess_type(file_path)

        with open(file_path, 'rb') as file:
            response = HttpResponse(file.read(), content_type=content_type)
            barcode = download_file.barcode_number ################
            # Get the original filename from the path
            original_filename = os.path.basename(file_path)
            prefix, extension = os.path.splitext(original_filename)#########
            modified_filename = barcode + extension  ###################
            # Set the Content-Disposition header with the original filename
            response['Content-Disposition'] = f'attachment; filename="{quote(modified_filename)}"'
            return response
    except Document.DoesNotExist:
        raise Http404("Shape does not exist")
    except Exception:
        return HttpResponse('Shape Document File Does Not Exist', status=404)

def qc_user_rectify_download_file(request, document_id):
    try:
        download_file = get_object_or_404(Document, id=document_id)
        file_path = download_file.rectify_upload.path
        content_type, _ = guess_type(file_path)

        with open(file_path, 'rb') as file:
            response = HttpResponse(file.read(), content_type=content_type)
            
            # Get the original filename from the path
            original_filename = os.path.basename(file_path)
            modified_filename = original_filename.replace("_R", "")

            # Set the Content-Disposition header with the original filename
            response['Content-Disposition'] = f'attachment; filename="{quote(modified_filename)}"'
            
            return response
    except Document.DoesNotExist:
        raise Http404("Document does not exist")
    except Exception:
        return HttpResponse('Rectify Document File Does Not Exist', status=404)
    
def topology_completed_download_file(request, document_id):
    try:
        download_file = get_object_or_404(Document, id=document_id)
        file_path = download_file.toplogy_upload.path
        content_type, _ = guess_type(file_path)

        with open(file_path, 'rb') as file:
            response = HttpResponse(file.read(), content_type=content_type)
            barcode = download_file.barcode_number   ###############
            
            # Get the original filename from the path
            original_filename = os.path.basename(file_path)
            prefix, extension = os.path.splitext(original_filename)###################
            modified_filename = barcode + extension ####################
            # Set the Content-Disposition header with the original filename
            response['Content-Disposition'] = f'attachment; filename="{quote(modified_filename)}"'
            return response
    except Document.DoesNotExist:
        raise Http404("Topology does not exist")
    except Exception:
        return HttpResponse('Topology Document File Does Not Exist', status=404)
    
class UploadDocumentRemarkGenericAPI(generics.GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = UploadDocumentSerializer

    def put(self, request, *args, **kwargs):
        data = request.data

        # Assuming you send a list of dictionaries with update data
        update_data_list = data

        for update_data in update_data_list:
            document_id = update_data.get("id")
            try:
                rectify_obj = Document.objects.get(id=document_id)
            except Document.DoesNotExist:
                return Response({"msg": f"Record with ID {document_id} does not exist"})

            # Update the fields specified in the dictionary
            serializer = UploadDocumentSerializer(rectify_obj, data=update_data, partial=True)
            if serializer.is_valid():
                serializer.save()
            else:
                return Response(serializer.errors)

        return Response({"message": "Success", "status": True})
    

class AllDocumentListView(generics.ListAPIView):
    queryset = Document.objects.all()
    permission_classes = [IsAuthenticated,]
    authentication_classes = (TokenAuthentication,)
    serializer_class = AllDocumentListSerialzer
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend,filters.SearchFilter]
    filterset_fields = ['map_code','district_code','village_code','taluka_code','bel_scan_uploaded','bel_draft_uploaded','bel_gov_scan_qc_approved','bel_gov_draft_qc_approved','chk_bel_scan_uploaded','chk_bel_draft_uploaded','chk_bel_gov_scan_qc_approved','chk_bel_gov_draft_qc_approved']
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)

        if request.GET.get('is_export') and request.GET.get('is_export') in ['1', 1]:
            for_count = 0
            csv_header = ['Sr.No','File Name','Barcode Number','District','Taluka','Village','Map Code','Polygon Count','Digitize By','Digi Completed Date','Qc By','QC Completed Date','Current Status','Scan By Username','Scan Uploaded Date']
            
            
            
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
                        qs.get('file_name'),
                        qs.get('barcode_number')+'`',
                        district_name,
                        taluka_name,
                        village_name,
                        qs.get('map_code'),
                        qs.get('polygon_count'),
                        qs.get('digitize_by_username'),
                        format_datetime(qs.get('digitize_completed_date')),
                        qs.get('qc_by_username'),
                        format_datetime(qs.get('qc_completed_date')),
                        qs.get('current_status'),
                        qs.get('scan_by_username'),
                        format_datetime(qs.get('scan_uploaded_date'))

                    ]
                )

            csv_data = generate_data_csv(csv_header, csv_body, f"report_data_{datetime.now()}_.csv")
            return Response({'csv_path': csv_data.get('csv_path')})

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        queryset = self.queryset

        if User.objects.filter(id=self.request.user.id, user_role__role_name="Super Admin"):
            query_set = queryset.all().order_by('-date_created')
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Agency Admin"):
            agency_ids = User.objects.filter(id=self.request.user.id).values_list('agency', flat=True)
            agency_filters = Q(rectify_agency_id__in=agency_ids) | Q(digitize_agency_id__in=agency_ids) | Q(qc_agency_id__in=agency_ids) | Q(topology_agency_id__in=agency_ids) | Q(shape_agency_id__in=agency_ids)
            query_set = queryset.filter(agency_filters).order_by('-date_created')
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="District Admin"):
            team_district_code = DistrictTalukaAdmin.objects.filter(user_id=self.request.user.id).values_list('district_id__district_code', flat=True)
            query_set = queryset.filter(district_code__in=team_district_code).order_by('-date_created')
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Taluka Admin"):
            query_set = queryset.filter(scan_uploaded_by=self.request.user.id).order_by('-date_created')
        else:
            query_set = queryset.none()  # Return an empty queryset for other roles
        
        file_name = self.request.query_params.get('file_name', None)
        barcode_number = self.request.query_params.get('barcode_number', None)
        village_name = self.request.query_params.get('village_name', None)
        taluka_name = self.request.query_params.get('taluka_name', None)
        district_name = self.request.query_params.get('district_name', None)
        scan_by_username = self.request.query_params.get('scan_by_username', None)
        rectify_by_username = self.request.query_params.get('rectify_by_username', None)
        digitize_by_username = self.request.query_params.get('digitize_by_username', None)
        qc_by_username = self.request.query_params.get('qc_by_username', None)
        pdf_by_username = self.request.query_params.get('pdf_by_username', None)
        shape_by_username = self.request.query_params.get('shape_by_username', None)
        current_status = self.request.query_params.get('current_status', None)
        scan_start_date = self.request.query_params.get('scan_start_date',None)
        scan_end_date = self.request.query_params.get('scan_end_date',None)
        rectify_start_date = self.request.query_params.get('rectify_start_date',None)
        rectify_end_date = self.request.query_params.get('rectify_end_date',None)
        digitize_start_date = self.request.query_params.get('digitize_start_date',None)
        digitize_end_date = self.request.query_params.get('digitize_end_date',None)
        qc_start_date = self.request.query_params.get('qc_start_date',None)
        qc_end_date = self.request.query_params.get('qc_end_date',None)
        
        rectify_agency_name=self.request.query_params.get('rectify_agency_name',None)
        digitize_agency_name=self.request.query_params.get('digitize_agency_name',None)
        qc_agency_name=self.request.query_params.get('qc_agency_name',None)
        topology_agency_name=self.request.query_params.get('topology_agency_name',None)
        shape_agency_name=self.request.query_params.get('shape_agency_name',None)

        gov_qc_by_username=self.request.query_params.get('gov_qc_by_username',None)
        topology_by_username=self.request.query_params.get('topology_by_username',None)


        polygon_min = self.request.query_params.get('polygon_min', None)
        polygon_max = self.request.query_params.get('polygon_max', None)
        qc_polygon_min = self.request.query_params.get('qc_polygon_min', None)
        qc_polygon_max = self.request.query_params.get('qc_polygon_max', None)

        rectify_assign_start_date = self.request.query_params.get('rectify_assign_start_date',None)
        rectify_assign_end_date = self.request.query_params.get('rectify_assign_end_date',None)
    
        digitize_assign_start_date = self.request.query_params.get('digitize_assign_start_date',None)
        digitize_assign_end_date = self.request.query_params.get('digitize_assign_end_date',None)
    

        qc_assign_start_date = self.request.query_params.get('qc_assign_start_date',None)
        qc_assign_end_date = self.request.query_params.get('qc_assign_end_date',None)

        gov_qc_assign_start_date = self.request.query_params.get('gov_qc_assign_start_date',None)
        gov_qc_assign_end_date = self.request.query_params.get('gov_qc_assign_end_date',None)
    
        gov_qc_completed_start_date = self.request.query_params.get('gov_qc_completed_start_date',None)
        gov_qc_completed_end_date = self.request.query_params.get('gov_qc_completed_end_date',None)

        topology_assign_start_date = self.request.query_params.get('topology_assign_start_date',None)
        topology_assign_end_date = self.request.query_params.get('topology_assign_end_date',None)
        topology_start_date = self.request.query_params.get('topology_start_date',None)
        topology_end_date = self.request.query_params.get('topology_end_date',None)

        shape_assign_start_date = self.request.query_params.get('shape_assign_start_date',None)
        shape_assign_end_date = self.request.query_params.get('tshape_assign_end_date',None)
        shape_start_date = self.request.query_params.get('shape_start_date',None)
        shape_end_date = self.request.query_params.get('shape_end_date',None)

        if topology_assign_start_date and topology_assign_end_date:
            topology_assign_start_date = datetime.strptime(topology_assign_start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
            topology_assign_end_date = datetime.strptime(topology_assign_end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query_set = query_set.filter(
                        topology_assign_date__gte=topology_assign_start_date.date(),
                        topology_assign_date__lt=(topology_assign_end_date.date() + timedelta(days=1)))
            
        if topology_start_date and topology_end_date:
            topology_start_date = datetime.strptime(topology_start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
            topology_end_date = datetime.strptime(topology_end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query_set = query_set.filter(
                        topology_completed_date__gte=topology_start_date.date(),
                        topology_completed_date__lt=(topology_end_date.date() + timedelta(days=1)))
            
        if shape_assign_start_date and shape_assign_end_date:
            shape_assign_start_date = datetime.strptime(shape_assign_start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
            shape_assign_end_date = datetime.strptime(shape_assign_end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query_set = query_set.filter(
                        shape_assign_date__gte=shape_assign_start_date.date(),
                        shape_assign_date__lt=(shape_assign_end_date.date() + timedelta(days=1)))
            
        if shape_start_date and shape_end_date:
            shape_start_date = datetime.strptime(shape_start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
            shape_end_date = datetime.strptime(shape_end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query_set = query_set.filter(
                        shape_completed_date__gte=shape_start_date.date(),
                        shape_completed_date__lt=(shape_end_date.date() + timedelta(days=1)))
 
        if gov_qc_assign_start_date and gov_qc_assign_end_date:
            gov_qc_assign_start_date = datetime.strptime(gov_qc_assign_start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
            gov_qc_assign_end_date = datetime.strptime(gov_qc_assign_end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query_set = query_set.filter(
                        gov_qc_assign_date__gte=gov_qc_assign_start_date.date(),
                        gov_qc_assign_date__lt=(gov_qc_assign_end_date.date() + timedelta(days=1)))
            
        if gov_qc_completed_start_date and gov_qc_completed_end_date:
            gov_qc_completed_start_date = datetime.strptime(gov_qc_completed_start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
            gov_qc_completed_end_date = datetime.strptime(gov_qc_completed_end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query_set = query_set.filter(
                        gov_qc_completed_date__gte=gov_qc_completed_start_date.date(),
                        gov_qc_completed_date__lt=(gov_qc_completed_end_date.date() + timedelta(days=1)))

        if polygon_min and polygon_max:
            try:
                polygon_min = int(polygon_min)
                polygon_max = int(polygon_max)
                query_set = query_set.filter(polygon_count__range=(polygon_min, polygon_max))
            except ValueError:
                query_set = query_set.none()  # Return an empty queryset

        if qc_polygon_min and qc_polygon_max:
            try:
                qc_polygon_min = int(qc_polygon_min)
                qc_polygon_max = int(qc_polygon_max)
                query_set = query_set.filter(qc_polygon_count__range=(qc_polygon_min, qc_polygon_max))
            except ValueError:
                query_set = query_set.none()  # Return an empty queryset
    
    
        if file_name:
            query_set = query_set.filter(file_name__icontains=file_name)
        

        if rectify_agency_name:
            query_set = query_set.filter(rectify_agency_id__agency_name__icontains=rectify_agency_name)
        
        if digitize_agency_name:
            query_set = query_set.filter(digitize_agency_id__agency_name__icontains=digitize_agency_name)
        
        if qc_agency_name:
            query_set = query_set.filter(qc_agency_id__agency_name__icontains=qc_agency_name)
        
        if topology_agency_name:
            query_set = query_set.filter(topology_agency_id__agency_name__icontains=topology_agency_name)
        
        if shape_agency_name:
            query_set = query_set.filter(shape_agency_id__agency_name__icontains=shape_agency_name)
        
        if gov_qc_by_username:
            query_set = query_set.filter(gov_qc_by__username__icontains=gov_qc_by_username)
        
        if topology_by_username:
            query_set = query_set.filter(topology_by__username__icontains=topology_by_username)

        if barcode_number:
            query_set = query_set.filter(barcode_number__icontains=barcode_number)
        
        if scan_start_date and scan_end_date:
            scan_start_date = datetime.strptime(scan_start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
            scan_end_date = datetime.strptime(scan_end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query_set = query_set.filter(
                        scan_uploaded_date__gte=scan_start_date.date(),
                        scan_uploaded_date__lt=(scan_end_date.date() + timedelta(days=1)))
            
        if rectify_start_date and rectify_end_date:
            rectify_start_date = datetime.strptime(rectify_start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
            rectify_end_date = datetime.strptime(rectify_end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query_set = query_set.filter(
                        rectify_completed_date__gte=rectify_start_date.date(),
                        rectify_completed_date__lt=(rectify_end_date.date() + timedelta(days=1)))
        
        if digitize_start_date and digitize_end_date:
            digitize_start_date = datetime.strptime(digitize_start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
            digitize_end_date = datetime.strptime(digitize_end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query_set = query_set.filter(
                        digitize_completed_date__gte=digitize_start_date.date(),
                        digitize_completed_date__lt=(digitize_end_date.date() + timedelta(days=1)))
        
        if qc_start_date and qc_end_date:
            qc_start_date = datetime.strptime(qc_start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
            qc_end_date = datetime.strptime(qc_end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query_set = query_set.filter(
                        qc_completed_date__gte=qc_start_date.date(),
                        qc_completed_date__lt=(qc_end_date.date() + timedelta(days=1)))
            
        if rectify_assign_start_date and rectify_assign_end_date:
            rectify_assign_start_date = datetime.strptime(rectify_assign_start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
            rectify_assign_end_date = datetime.strptime(rectify_assign_end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query_set = query_set.filter(
                        rectify_assign_date__gte=rectify_assign_start_date.date(),
                        rectify_assign_date__lt=(rectify_assign_end_date.date() + timedelta(days=1)))
        
        if digitize_assign_start_date and digitize_assign_end_date:
            digitize_assign_start_date = datetime.strptime(digitize_assign_start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
            digitize_assign_end_date = datetime.strptime(digitize_assign_end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query_set = query_set.filter(
                        digitize_assign_date__gte=digitize_assign_start_date.date(),
                        digitize_assign_date__lt=(digitize_assign_end_date.date() + timedelta(days=1)))
    
            
        if qc_assign_start_date and qc_assign_end_date:
            qc_assign_start_date = datetime.strptime(qc_assign_start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
            qc_assign_end_date = datetime.strptime(qc_assign_end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query_set = query_set.filter(
                        qc_assign_date__gte=qc_assign_start_date.date(),
                        qc_assign_date__lt=(qc_assign_end_date.date() + timedelta(days=1)))
            
            
        if village_name:
            village_names = Village.objects.filter(village_name__icontains=village_name).values_list('village_code',flat=True)
            query_set = query_set.filter(village_code__in=village_names)
            

        if taluka_name:
            taluka_names = Taluka.objects.filter(taluka_name__icontains=taluka_name).values_list('taluka_code',flat=True)
            query_set = query_set.filter(taluka_code__in=taluka_names)


        if district_name:
            district_names = District.objects.filter(district_name__icontains=district_name).values_list('district_code',flat=True)
            query_set = query_set.filter(district_code__in=district_names)
        
        
        if scan_by_username:
            query_set = query_set.filter(scan_uploaded_by__username__icontains=scan_by_username)
        
        if rectify_by_username:
            query_set = query_set.filter(rectify_by__username__icontains=rectify_by_username)
            
        if digitize_by_username:
            query_set = query_set.filter(digitize_by__username__icontains=digitize_by_username)
            
        if qc_by_username:
            query_set = query_set.filter(qc_by__username__icontains=qc_by_username)
            
        if pdf_by_username:
            query_set = query_set.filter(pdf_by__username__icontains=pdf_by_username)
            
        if shape_by_username:
            query_set = query_set.filter(shape_by__username__icontains=shape_by_username)
        
        if current_status:
            query_set = query_set.filter(current_status__status__icontains=current_status)
            
        return query_set
    

class UpdateRectifyFileCreateView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)
    serializer_class = UploadDocumentSerializer  # Use the custom serializer

    def put(self, request, *args, **kwargs):
        # Extract the action from the URL
        action = kwargs.get('action', None)

        if action == 'approved':
            data = request.FILES.getlist('files')
            total_len = 0

            for file in data:
                filename = file.name
                base_filename,file_extension = os.path.splitext(filename)
                code = base_filename.split("_")[0]

                try:
                    # Get the existing object based on the barcode
                    obj = Document.objects.get(barcode_number=code,scan_uploaded_date__isnull=False,current_status__in=[1,3,4,7,11])
                    new_filename = f"{base_filename}{file_extension}"


                    # Create a SimpleUploadedFile with the file data
                    uploaded_file = SimpleUploadedFile(name=new_filename, content=file.read())

                    # Create a dictionary with the data to update
                    rectify_obj = self.request.user.id
                    rectify_agency_id = self.request.user.agency.id
                    agency_team_id = self.request.user.agency.team.id
                    completed_date = datetime.now()
                    # Check if digitize_agency_id is present
                    if obj.digitize_agency_id is not None:
                        current_status = 8
                    else:
                        current_status = 5

                    update_data = {
                        'rectify_agency_id':rectify_agency_id,
                        'team_id':agency_team_id,
                        'rectify_upload': uploaded_file,  # Pass the uploaded file data
                        "rectify_by": rectify_obj,
                        "rectify_completed_date": completed_date,
                        "current_status": current_status
                    }

                    serializer = self.get_serializer(obj, data=update_data, partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        total_len += 1
                    else:
                        print(f"Error validating data for code {code}: {serializer.errors}")

                except Document.DoesNotExist:
                    print(f"Object with barcode {code} does not exist.")

            return Response({"message": f"{total_len} Rectify Files Updated"}, status=status.HTTP_200_OK)

        elif action == 'rejected':
            data = request.data

            # Assuming you send a list of dictionaries with update data
            update_data_list = data

            for update_data in update_data_list:
                document_id = update_data.get("id")
                try:
                    rectify_obj = Document.objects.get(id=document_id)
                except Document.DoesNotExist:
                    return Response({"msg": f"Record with ID {document_id} does not exist"})

                # Update the fields specified in the dictionary
                serializer = UploadDocumentSerializer(rectify_obj, data=update_data, partial=True)
                if serializer.is_valid():
                    serializer.save(current_status=DocumentStatus.objects.get(id=6))
        
            return Response({"message": "Rectify Files Rejected"})
            # Handle 'rejected' action here
            # Update current_status to 1 for the appropriate documents
            # Add your code for the 'rejected' action here

        elif action == 'onhold':
            data = request.data

            # Assuming you send a list of dictionaries with update data
            update_data_list = data

            for update_data in update_data_list:
                document_id = update_data.get("id")
                try:
                    rectify_obj = Document.objects.get(id=document_id)
                except Document.DoesNotExist:
                    return Response({"msg": f"Record with ID {document_id} does not exist"})

                # Update the fields specified in the dictionary
                serializer = UploadDocumentSerializer(rectify_obj, data=update_data, partial=True)
                if serializer.is_valid():
                    serializer.save(current_status=DocumentStatus.objects.get(id=7))
        
            return Response({"message": "Rectify Files On-Hold"})
            # Handle 'onhold' action here
            # Update current_status to 2 for the appropriate documents
            # Add your code for the 'onhold' action here

        else:
            return Response({"message": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)


class UpdateDigitizeFileCreateView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)
    serializer_class = DigitizeUploadDocumentSerializer  # Use the custom serializer

    def put(self, request, *args, **kwargs):
        # Extract the action from the URL
        action = kwargs.get('action', None)

        if action == 'approved':
            data = request.FILES.getlist('files')
            digi_polygon = request.data.get("polygon_count")
            remark = request.data.get("remarks")
            
            total_len = 0
            errors = []

            for file in data:
                filename = file.name
                base_filename,file_extension = os.path.splitext(filename)
                code = base_filename.split("_")[0]

                
                try:
                    # Get the existing object based on the barcode
                    obj = Document.objects.get(barcode_number=code,rectify_completed_date__isnull=False,current_status__in=[5,8,9,12,16])
                    # new_filename = f"{base_filename}{file_extension}"
                    if file_extension.lower() == ".dwg":
                        new_filename = f"{base_filename}{file_extension}"

                    # Create a SimpleUploadedFile with the file data
                    uploaded_file = SimpleUploadedFile(name=new_filename, content=file.read())

                    # Create a dictionary with the data to update
                    digitize_obj = self.request.user.id
                    digitize_agency_id = self.request.user.agency.id
                    completed_date = datetime.now()

                    if obj.qc_agency_id is not None:
                        current_status = 13
                    else:
                        current_status = 10

                    if file_extension.lower() == ".dwg":
                        update_data = {
                            'digitize_agency_id':digitize_agency_id,
                            'digitize_upload': uploaded_file,  # Pass the uploaded file data
                            "digitize_by": digitize_obj,
                            "polygon_count":digi_polygon,
                            "remarks":remark,
                            "digitize_completed_date": completed_date,
                            "current_status": current_status
                        }

                    serializer = self.get_serializer(obj, data=update_data, partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        total_len += 1
                    else:
                        errors.append(f"Error validating data for code {code}: {serializer.errors}")

                except Document.DoesNotExist:
                    errors.append(f"Object with barcode {code} does not exist.")

            if total_len == 0:
                return Response({"message": "Digitize Polygon Count Is Not Updated"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"message": f"{total_len} Digitize Files Updated"}, status=status.HTTP_200_OK)
            
        elif action == 'rejected':
            data = request.data

            # Assuming you send a list of dictionaries with update data
            update_data_list = data

            for update_data in update_data_list:
                document_id = update_data.get("id")
                digitize_remarks = update_data.get("digitize_remarks")

                if not digitize_remarks or not str(digitize_remarks).strip():
                    return Response(
                        {"message": f"Digitize remarks are required for rejecting."},
                        status=status.HTTP_200_OK
                    )

                try:
                    rectify_obj = Document.objects.get(id=document_id)
                except Document.DoesNotExist:
                    return Response({"msg": f"Record with ID {document_id} does not exist"})

                # Update the fields specified in the dictionary
                serializer = UploadDocumentSerializer(rectify_obj, data=update_data, partial=True)
                if serializer.is_valid():
                    serializer.save(current_status=DocumentStatus.objects.get(id=11))
        
            return Response({"message": "Digitize Files Rejected"})
            # Handle 'rejected' action here
            # Update current_status to 1 for the appropriate documents
            # Add your code for the 'rejected' action here

        elif action == 'onhold':
            data = request.data

            # Assuming you send a list of dictionaries with update data
            update_data_list = data

            for update_data in update_data_list:
                document_id = update_data.get("id")
                try:
                    rectify_obj = Document.objects.get(id=document_id)
                except Document.DoesNotExist:
                    return Response({"msg": f"Record with ID {document_id} does not exist"})

                # Update the fields specified in the dictionary
                serializer = UploadDocumentSerializer(rectify_obj, data=update_data, partial=True)
                if serializer.is_valid():
                    serializer.save(current_status=DocumentStatus.objects.get(id=12))
        
            return Response({"message": "Digitize Files On-Hold"})
            # Handle 'onhold' action here
            # Update current_status to 2 for the appropriate documents
            # Add your code for the 'onhold' action here

        else:
            return Response({"message": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)

class UpdateQCFileCreateView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)
    serializer_class = UploadDocumentSerializer  # Use the custom serializer

    def put(self, request, *args, **kwargs):
        # Extract the action from the URL
        action = kwargs.get('action', None)

        if action == 'approved':
            data = request.FILES.getlist('files')
            qc_polygon = request.data.get("qc_polygon_count")
            remark = request.data.get("remarks")
           

            total_len = 0
            errors = []

            for file in data:     
                filename = file.name
                base_filename,file_extension = os.path.splitext(filename)
                code = base_filename.split("_")[0]

                try:
                    # Get the existing object based on the barcode
                    obj = Document.objects.get(barcode_number=code,digitize_completed_date__isnull=False,current_status__in=[10,13,14,17,21])

                    if file_extension.lower() == ".dwg":
                        new_filename = f"{base_filename}{file_extension}"
                    # elif file_extension.lower() == ".pdf":
                    #     new_filename = f"{base_filename}{file_extension}"

                    # Create a SimpleUploadedFile with the file data
                    uploaded_file = SimpleUploadedFile(name=new_filename, content=file.read())

                    # Create a dictionary with the data to update
                    qc_obj = self.request.user.id
                    qc_agency_id = self.request.user.agency.id
                    completed_date = datetime.now()


                    if file_extension.lower() == ".dwg":
                        update_data = {
                            'qc_agency_id':qc_agency_id,
                            "qc_upload": uploaded_file,  # Pass the uploaded file data
                            "qc_by": qc_obj,
                            "qc_polygon_count":qc_polygon,
                            "remarks":remark,
                            "pdf_by": qc_obj,  # Corrected duplicated key
                            "qc_completed_date": completed_date,
                            "current_status": 15
                        }
                    # else:
                    #     update_data = {
                    #         "pdf_upload": uploaded_file,  # Pass the uploaded file data
                    #         "pdf_by": qc_obj,
                    #         "pdf_completed_date":completed_date,
                    #         "current_status": 20
                    #     }

                    

                    serializer = self.get_serializer(obj, data=update_data, partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        total_len += 1
                    else:
                        errors.append(f"Error validating data for code {code}: {serializer.errors}")

                except Document.DoesNotExist:
                    errors.append(f"Object with barcode {code} does not exist.")

            if total_len == 0:
                return Response({"message": "Qc Polygon Count Is Not Updated"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"message": f"{total_len} Qc Files Updated"}, status=status.HTTP_200_OK)

        elif action == 'rejected':
            data = request.data

            # Assuming you send a list of dictionaries with update data
            update_data_list = data

            for update_data in update_data_list:
                document_id = update_data.get("id")
                try:
                    rectify_obj = Document.objects.get(id=document_id)
                except Document.DoesNotExist:
                    return Response({"msg": f"Record with ID {document_id} does not exist"})

                # Update the fields specified in the dictionary
                serializer = UploadDocumentSerializer(rectify_obj, data=update_data, partial=True)
                if serializer.is_valid():
                    serializer.save(current_status=DocumentStatus.objects.get(id=16))
        
            return Response({"message": "Qc Files Rejected"})
            # Handle 'rejected' action here
            # Update current_status to 1 for the appropriate documents
            # Add your code for the 'rejected' action here

        elif action == 'onhold':
            data = request.data

            # Assuming you send a list of dictionaries with update data
            update_data_list = data

            for update_data in update_data_list:
                document_id = update_data.get("id")
                try:
                    rectify_obj = Document.objects.get(id=document_id)
                except Document.DoesNotExist:
                    return Response({"msg": f"Record with ID {document_id} does not exist"})

                # Update the fields specified in the dictionary
                serializer = UploadDocumentSerializer(rectify_obj, data=update_data, partial=True)
                if serializer.is_valid():
                    serializer.save(current_status=DocumentStatus.objects.get(id=17))
        
            return Response({"message": "Qc Files On-Hold"})
            # Handle 'onhold' action here
            # Update current_status to 2 for the appropriate documents
            # Add your code for the 'onhold' action here

        else:
            return Response({"message": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)
        
class UpdatePdfFileCreateView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)
    serializer_class = UploadDocumentSerializer  # Use the custom serializer

    def put(self, request, *args, **kwargs):
        # Extract the action from the URL
        action = kwargs.get('action', None)

        if action == 'approved':
            data = request.FILES.getlist('files')
            total_len = 0

            for file in data:
                filename = file.name
                base_filename,file_extension = os.path.splitext(filename)
                code = base_filename.split("_")[0]

                try:
                    # Get the existing object based on the barcode
                    obj = Document.objects.get(barcode_number=code,qc_completed_date__isnull=False,current_status__in=[15,18,19,22,26])
                    if file_extension.lower() == ".pdf":
                        new_filename = f"{base_filename}{file_extension}"
                    # Create a SimpleUploadedFile with the file data
                    uploaded_file = SimpleUploadedFile(name=new_filename, content=file.read())

                    # Create a dictionary with the data to update
                    pdf_obj = self.request.user.id
                    completed_date = datetime.now()
                    update_data = {
                        "pdf_upload": uploaded_file,  # Pass the uploaded file data
                        "pdf_by":pdf_obj,
                        "pdf_completed_date":completed_date,
                        "current_status":20
                    }
                    

                    serializer = self.get_serializer(obj, data=update_data, partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        total_len += 1
                    else:
                        print(f"Error validating data for code {code}: {serializer.errors}")

                except Document.DoesNotExist:
                    print(f"Object with barcode {code} does not exist.")

            return Response({"message": f"{total_len} Pdf Files Updated"}, status=status.HTTP_200_OK)

        elif action == 'rejected':
            data = request.data

            # Assuming you send a list of dictionaries with update data
            update_data_list = data

            for update_data in update_data_list:
                document_id = update_data.get("id")
                try:
                    rectify_obj = Document.objects.get(id=document_id)
                except Document.DoesNotExist:
                    return Response({"msg": f"Record with ID {document_id} does not exist"})

                # Update the fields specified in the dictionary
                serializer = UploadDocumentSerializer(rectify_obj, data=update_data, partial=True)
                if serializer.is_valid():
                    serializer.save(current_status=DocumentStatus.objects.get(id=21))
        
            return Response({"message": "Pdf Files Rejected"})
            # Handle 'rejected' action here
            # Update current_status to 1 for the appropriate documents
            # Add your code for the 'rejected' action here

        elif action == 'onhold':
            data = request.data

            # Assuming you send a list of dictionaries with update data
            update_data_list = data

            for update_data in update_data_list:
                document_id = update_data.get("id")
                try:
                    rectify_obj = Document.objects.get(id=document_id)
                except Document.DoesNotExist:
                    return Response({"msg": f"Record with ID {document_id} does not exist"})

                # Update the fields specified in the dictionary
                serializer = UploadDocumentSerializer(rectify_obj, data=update_data, partial=True)
                if serializer.is_valid():
                    serializer.save(current_status=DocumentStatus.objects.get(id=22))
        
            return Response({"message": "Pdf Files On-Hold"})
            # Handle 'onhold' action here
            # Update current_status to 2 for the appropriate documents
            # Add your code for the 'onhold' action here

        else:
            return Response({"message": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)
        
class UpdateShapeFileCreateView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)
    serializer_class = UploadDocumentSerializer  # Use the custom serializer

    def put(self, request, *args, **kwargs):
        # Extract the action from the URL
        action = kwargs.get('action', None)

        if action == 'approved':
            data = request.FILES.getlist('files')
            total_len = 0

            for file in data:
                filename = file.name
                base_filename,file_extension = os.path.splitext(filename)

                if file_extension.lower() != ".zip":
                    print(f"Skipping file {filename}: Only .zip files are allowed.")
                    continue

                code = base_filename.split("_")[0]

                try:
                    obj = Document.objects.get(barcode_number=code,topology_completed_date__isnull=False,current_status__in=[23,24,27,33])
                    new_filename = f"{base_filename}{file_extension}"

                   
                    uploaded_file = SimpleUploadedFile(name=new_filename, content=file.read())

                    shape_obj = self.request.user.id
                    completed_date = datetime.now()
                    update_data = {
                        "shape_upload": uploaded_file,
                        "shape_by":shape_obj,
                        "shape_completed_date":completed_date,
                        "current_status":25
                    }   

                    serializer = self.get_serializer(obj, data=update_data, partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        total_len += 1
                    else:
                        print(f"Error validating data for code {code}: {serializer.errors}")

                except Document.DoesNotExist:
                    print(f"Object with barcode {code} does not exist.")

            return Response({"message": f"{total_len} Shape Files Updated"}, status=status.HTTP_200_OK)

        elif action == 'rejected':
            data = request.data

            update_data_list = data

            for update_data in update_data_list:
                document_id = update_data.get("id")
                try:
                    rectify_obj = Document.objects.get(id=document_id)
                except Document.DoesNotExist:
                    return Response({"msg": f"Record with ID {document_id} does not exist"})

                serializer = UploadDocumentSerializer(rectify_obj, data=update_data, partial=True)
                if serializer.is_valid():
                    serializer.save(current_status=DocumentStatus.objects.get(id=26))
        
            return Response({"message": "Shape Files Rejected"})
          

        elif action == 'onhold':
            data = request.data

            update_data_list = data

            for update_data in update_data_list:
                document_id = update_data.get("id")
                try:
                    rectify_obj = Document.objects.get(id=document_id)
                except Document.DoesNotExist:
                    return Response({"msg": f"Record with ID {document_id} does not exist"})

                serializer = UploadDocumentSerializer(rectify_obj, data=update_data, partial=True)
                if serializer.is_valid():
                    serializer.save(current_status=DocumentStatus.objects.get(id=27))
        
            return Response({"message": "Shape Files On-Hold"})
      

        else:
            return Response({"message": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)


class ReuploadScanFileCreateView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)
    serializer_class = UploadDocumentSerializer  # Use the custom serializer

    def put(self, request, *args, **kwargs):
        data = request.FILES.getlist('files')
        total_len = 0

        for file in data:
            filename = file.name
            base_filename,file_extension = os.path.splitext(filename)
            code = base_filename.split("_")[0]

            try:
                # Get the existing object based on the barcode
                obj = Document.objects.get(barcode_number=code,current_status__in=[1,6,28])
                new_filename = f"{base_filename}{file_extension}"

                # Create a SimpleUploadedFile with the file data
                uploaded_file = SimpleUploadedFile(name=new_filename, content=file.read())

                # Create a dictionary with the data to update
                scan_upload_by = self.request.user.id
                completed_date =datetime.now()
                update_data = {
                    'scan_upload': uploaded_file,  # Pass the uploaded file data
                    "scan_uploaded_by":scan_upload_by,
                    "scan_uploaded_date":completed_date,
                    "current_status":1,
                    "rectify_agency_id":None,
                    "rectify_upload":None,
                    "rectify_by":None,
                    "rectify_assign_date":None,
                    "rectify_completed_date":None,
                    "digitize_agency_id":None,
                    "digitize_upload":None,
                    "digitize_by":None,
                    "polygon_count":0,
                    "qc_polygon_count":0,
                    "digitize_assign_date":None,
                    "digitize_completed_date":None,
                    "qc_agency_id":None,
                    "qc_upload":None,
                    "qc_by":None,
                    "qc_assign_date":None,
                    "qc_completed_date":None,
                    "remarks":None,
                    "digitize_remarks":None,
                    "qc_remarks":None,
                }

                serializer = self.get_serializer(obj, data=update_data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    total_len += 1
                else:
                    print(f"Error validating data for code {code}: {serializer.errors}")

            except Document.DoesNotExist:
                print(f"Object with barcode {code} does not exist.")

        return Response({"message": f"{total_len} Scan Files Updated"}, status=status.HTTP_200_OK)
    

class NotFoundScanDocumentListView(ListAPIView):
    queryset = Document.objects.all()
    permission_classes = [IsAuthenticated,]
    authentication_classes = (TokenAuthentication,)
    serializer_class = NotScanDocumentListSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend,filters.SearchFilter]
    search_fields = []
    filterset_fields = ['taluka_code']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)

        if request.GET.get('is_export') and request.GET.get('is_export') in ['1', 1]:
            for_count = 0
            csv_header = ['Sr.No','Barcode Number','File Name','District','Taluka','Village','Map Code','Current Status','Remark']
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
                        qs.get('barcode_number')+'_',
                        qs.get('file_name'),
                        district_name,
                        taluka_name,
                        village_name,
                        qs.get('map_code'),
                        qs.get('current_status'),
                        qs.get('remarks',''),
                       
                    ]
                )

            csv_data = generate_data_csv(csv_header, csv_body, f"notfound_report_{datetime.now()}_.csv")
            return Response({'csv_path': csv_data.get('csv_path')})

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        queryset = self.queryset
        if User.objects.filter(id=self.request.user.id, user_role__role_name="Super Admin"):
            query_set = queryset.filter(current_status=28).order_by('-date_created')
       
        
        village_name = self.request.query_params.get('village_name', None)
        taluka_name = self.request.query_params.get('taluka_name', None)
        district_name = self.request.query_params.get('district_name', None)
        barcode_number = self.request.query_params.get('barcode_number', None)
        file_name = self.request.query_params.get('file_name', None)
        district_code = self.request.query_params.get('district_code', None)
        village_code = self.request.query_params.get('village_code', None)
        map_code = self.request.query_params.get('map_code', None)
        current_status = self.request.query_params.get('current_status', None)

        
        if village_name:
            village_names = Village.objects.filter(village_name__icontains=village_name).values_list('village_code',flat=True)
            query_set = query_set.filter(village_code__in=village_names)
            

        if taluka_name:
            taluka_names = Taluka.objects.filter(taluka_name__icontains=taluka_name).values_list('taluka_code',flat=True)
            query_set = query_set.filter(taluka_code__in=taluka_names)


        if district_name:
            district_names = District.objects.filter(district_name__icontains=district_name).values_list('district_code',flat=True)
            query_set = query_set.filter(district_code__in=district_names)
        
        
        if barcode_number:
            query_set = query_set.filter(barcode_number__icontains=barcode_number)
        
        if file_name:
            query_set = query_set.filter(file_name__icontains=file_name)
            
        if district_code:
            query_set = query_set.filter(district_code__icontains=district_code)
        
        if village_code:
            query_set = query_set.filter(village_code__icontains=village_code)
       
        if map_code:
            query_set = query_set.filter(map_code__icontains=map_code)
        
        if current_status:
            query_set = query_set.filter(current_status__status__icontains=current_status)
        

        return query_set
    
class AutoUploadDigitizeFileCreateView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)
    serializer_class = UploadDocumentSerializer  # Use the custom serializer

    def put(self, request, *args, **kwargs):
        # Extract the action from the URL
        action = kwargs.get('action', None)

        if action == 'approved':
            data = request.FILES.getlist('files')
            total_len = 0

            for file in data:
                filename = file.name
                base_filename,file_extension = os.path.splitext(filename)
                code = base_filename.split("_")[0]

                
                try:
                    # Get the existing object based on the barcode
                    obj = Document.objects.get(barcode_number=code,rectify_completed_date__isnull=False)
                    new_filename = f"{base_filename}{file_extension}"

                    # Create a SimpleUploadedFile with the file data
                    uploaded_file = SimpleUploadedFile(name=new_filename, content=file.read())

                    # Create a dictionary with the data to update
                    digitize_obj = self.request.user.id
                    completed_date = datetime.now()
                    
                    if file_extension.lower() == ".dwg":
                        update_data = {
                            'digitize_upload': uploaded_file,  # Pass the uploaded file data
                            "digitize_by": digitize_obj,
                            "digitize_assign_date":completed_date,
                            "digitize_completed_date": completed_date,
                            "remarks":"Auto Uploaded",
                            "current_status": 10
                        }

                    serializer = self.get_serializer(obj, data=update_data, partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        total_len += 1
                    else:
                        print(f"Error validating data for code {code}: {serializer.errors}")

                except Document.DoesNotExist:
                    print(f"Object with barcode {code} does not exist. Or Rectify Not Completed")

            return Response({"message": f"{total_len} Digitize Files Updated"}, status=status.HTTP_200_OK)

        elif action == 'rejected':
            data = request.data

            # Assuming you send a list of dictionaries with update data
            update_data_list = data

            for update_data in update_data_list:
                document_id = update_data.get("id")
                try:
                    rectify_obj = Document.objects.get(id=document_id)
                except Document.DoesNotExist:
                    return Response({"msg": f"Record with ID {document_id} does not exist"})

                # Update the fields specified in the dictionary
                serializer = UploadDocumentSerializer(rectify_obj, data=update_data, partial=True)
                if serializer.is_valid():
                    serializer.save(current_status=DocumentStatus.objects.get(id=11))
        
            return Response({"message": "Digitize Files Rejected"})
            # Handle 'rejected' action here
            # Update current_status to 1 for the appropriate documents
            # Add your code for the 'rejected' action here

        elif action == 'onhold':
            data = request.data

            # Assuming you send a list of dictionaries with update data
            update_data_list = data

            for update_data in update_data_list:
                document_id = update_data.get("id")
                try:
                    rectify_obj = Document.objects.get(id=document_id)
                except Document.DoesNotExist:
                    return Response({"msg": f"Record with ID {document_id} does not exist"})

                # Update the fields specified in the dictionary
                serializer = UploadDocumentSerializer(rectify_obj, data=update_data, partial=True)
                if serializer.is_valid():
                    serializer.save(current_status=DocumentStatus.objects.get(id=12))
        
            return Response({"message": "Digitize Files On-Hold"})
            # Handle 'onhold' action here
            # Update current_status to 2 for the appropriate documents
            # Add your code for the 'onhold' action here

        else:
            return Response({"message": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)
        

class AutoUploadQCFileCreateView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)
    serializer_class = UploadDocumentSerializer  # Use the custom serializer

    def put(self, request, *args, **kwargs):
        # Extract the action from the URL
        action = kwargs.get('action', None)

        if action == 'approved':
            data = request.FILES.getlist('files')
            total_len = 0

            for file in data:     
                filename = file.name
                base_filename,file_extension = os.path.splitext(filename)
                code = base_filename.split("_")[0]

                try:
                    # Get the existing object based on the barcode
                    obj = Document.objects.get(barcode_number=code,digitize_completed_date__isnull=False)

                    if file_extension.lower() == ".dwg":
                        new_filename = f"{base_filename}{file_extension}"
                    elif file_extension.lower() == ".pdf":
                        new_filename = f"{base_filename}{file_extension}"

                    # Create a SimpleUploadedFile with the file data
                    uploaded_file = SimpleUploadedFile(name=new_filename, content=file.read())

                    # Create a dictionary with the data to update
                    qc_obj = self.request.user.id
                    completed_date = datetime.now()


                    if file_extension.lower() == ".dwg":
                        update_data = {
                            "qc_upload": uploaded_file,  # Pass the uploaded file data
                            "qc_by": qc_obj,
                            "pdf_by": qc_obj,  # Corrected duplicated key
                            "qc_completed_date": completed_date,
                            "remarks":"Auto Uploaded",
                            "current_status": 15
                        }
                    else:
                        update_data = {
                            "pdf_upload": uploaded_file,  # Pass the uploaded file data
                            "pdf_by": qc_obj,
                            "pdf_completed_date":completed_date,
                            "remarks":"Auto Uploaded",
                            "current_status": 20
                        }

                    

                    serializer = self.get_serializer(obj, data=update_data, partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        total_len += 1
                    else:
                        print(f"Error validating data for code {code}: {serializer.errors}")

                except Document.DoesNotExist:
                    print(f"Object with barcode {code} does not exist.")

            return Response({"message": f"{total_len} Qc Files Updated"}, status=status.HTTP_200_OK)

        elif action == 'rejected':
            data = request.data

            # Assuming you send a list of dictionaries with update data
            update_data_list = data

            for update_data in update_data_list:
                document_id = update_data.get("id")
                try:
                    rectify_obj = Document.objects.get(id=document_id)
                except Document.DoesNotExist:
                    return Response({"msg": f"Record with ID {document_id} does not exist"})

                # Update the fields specified in the dictionary
                serializer = UploadDocumentSerializer(rectify_obj, data=update_data, partial=True)
                if serializer.is_valid():
                    serializer.save(current_status=DocumentStatus.objects.get(id=16))
        
            return Response({"message": "Qc Files Rejected"})
            # Handle 'rejected' action here
            # Update current_status to 1 for the appropriate documents
            # Add your code for the 'rejected' action here

        elif action == 'onhold':
            data = request.data

            # Assuming you send a list of dictionaries with update data
            update_data_list = data

            for update_data in update_data_list:
                document_id = update_data.get("id")
                try:
                    rectify_obj = Document.objects.get(id=document_id)
                except Document.DoesNotExist:
                    return Response({"msg": f"Record with ID {document_id} does not exist"})

                # Update the fields specified in the dictionary
                serializer = UploadDocumentSerializer(rectify_obj, data=update_data, partial=True)
                if serializer.is_valid():
                    serializer.save(current_status=DocumentStatus.objects.get(id=17))
        
            return Response({"message": "Qc Files On-Hold"})
            # Handle 'onhold' action here
            # Update current_status to 2 for the appropriate documents
            # Add your code for the 'onhold' action here

        else:
            return Response({"message": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)


class AgencyWiseWiseDashboardView(APIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    # This API User Base Count Display
    def get(self, request):
       
        if User.objects.filter(id=self.request.user.id, user_role__role_name="Super Admin"):
            agency_list = Agency.objects.all().order_by('-date_created')
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Agency Admin"):
            agency_list = Agency.objects.all().order_by('-date_created')

        else:
            agency_list = []

        counts_by_agency = []

        for agency_list_obj in agency_list:
            agency_id = agency_list_obj.id
            agency_name = agency_list_obj.agency_name


       
            counts = {
                'polygon_count':0,
                'total_scan_uploaded':0,
                'scan_uploaded':0,
                'rectify_allocated': 0,
                'rectify_completed': 0,
                'digitize_allocated': 0,
                'digitize_completed': 0,
                'qc_allocated': 0,
                'qc_completed': 0,
                'pdf_allocated': 0,
                'pdf_completed': 0,
                'shape_allocated': 0,
                'shape_completed': 0,
            }
           

            if User.objects.filter(id=self.request.user.id, user_role__role_name="Super Admin"):
                counts['scan_uploaded'] = Document.objects.filter(rectify_agency_id=agency_id, current_status=1).count()
                counts['polygon_count'] = Document.objects.filter(rectify_agency_id=agency_id).aggregate(total_amount=Sum('polygon_count'))['total_amount']
                counts['rectify_allocated'] = Document.objects.filter(rectify_agency_id=agency_id, current_status=3).count()
                counts['digitize_allocated'] = Document.objects.filter(map_code=agency_id, current_status=8).count()
                
                
                counts['total_scan_uploaded'] = Document.objects.filter(map_code=agency_id).count()
                counts['rectify_completed'] = Document.objects.filter(rectify_agency_id=agency_id, rectify_completed_date__isnull=False).count()
                counts['digitize_completed'] = Document.objects.filter(digitize_agency_id=agency_id, digitize_completed_date__isnull=False).count()
                counts['qc_completed'] = Document.objects.filter(qc_agency_id=agency_id, qc_completed_date__isnull=False).count()
                counts['pdf_completed'] = Document.objects.filter(qc_agency_id=agency_id, pdf_completed_date__isnull=False).count()
                counts['shape_completed'] = Document.objects.filter(qc_agency_id=agency_id, shape_completed_date__isnull=False).count()


                counts['qc_allocated'] = Document.objects.filter(qc_agency_id=agency_id, current_status=13).count()
                counts['pdf_allocated'] = Document.objects.filter(qc_agency_id=agency_id, current_status=18).count()
                counts['shape_allocated'] = Document.objects.filter(qc_agency_id=agency_id, current_status=23).count()
            
            elif User.objects.filter(id=self.request.user.id, user_role__role_name="Agency Admin"):
                counts['scan_uploaded'] = Document.objects.filter(rectify_agency_id=agency_id, current_status=1).count()
                counts['polygon_count'] = Document.objects.filter(digitize_agency_id=agency_id).aggregate(total_amount=Sum('polygon_count'))['total_amount']
                
                
                counts['total_scan_uploaded'] = Document.objects.filter(rectify_agency_id=agency_id).count()
                counts['rectify_completed'] = Document.objects.filter(rectify_agency_id=agency_id,rectify_completed_date__isnull=False).count()
                counts['digitize_completed'] = Document.objects.filter(digitize_agency_id=agency_id, digitize_completed_date__isnull=False).count()
                counts['qc_completed'] = Document.objects.filter(qc_agency_id=agency_id, qc_completed_date__isnull=False).count()
                counts['pdf_completed'] = Document.objects.filter(qc_agency_id=agency_id, pdf_completed_date__isnull=False).count()
                counts['shape_completed'] = Document.objects.filter(qc_agency_id=agency_id, shape_completed_date__isnull=False).count()

                counts['rectify_allocated'] = Document.objects.filter(rectify_agency_id=agency_id, current_status=3).count()
                counts['digitize_allocated'] = Document.objects.filter(digitize_agency_id=agency_id, current_status=8).count()
                counts['qc_allocated'] = Document.objects.filter(qc_agency_id=agency_id, current_status=13).count()
                counts['pdf_allocated'] = Document.objects.filter(qc_agency_id=agency_id, current_status=18).count()
                counts['shape_allocated'] = Document.objects.filter(qc_agency_id=agency_id, current_status=23).count()
            
          


            counts_by_agency.append({
                'agency_name': agency_name,
                **counts,
            })

        response_data = {
            'counts_by_maptype': counts_by_agency,
            'status': True
        }

        return Response(data=response_data, status=status.HTTP_200_OK)
    


class CorrectNotFoundScanFileCreateView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)
    serializer_class = UploadDocumentSerializer  # Use the custom serializer

    def put(self, request, *args, **kwargs):
        document_id = request.data.get('id')
        barcode_name = request.data.get('barcode_number')

        try:
            # Get the existing object based on the barcode
            obj = Document.objects.get(id=document_id)
            file_path = obj.scan_upload.path
            with open(file_path, 'rb') as file:                
                # Get the original filename from the path
                original_filename = os.path.basename(file_path)
                new_file_path = os.path.join(os.path.dirname(file_path), barcode_name + os.path.splitext(original_filename)[1])
                os.rename(file_path, new_file_path)

                # Update the database record with the new file path
                obj.scan_upload.name = os.path.relpath(new_file_path, settings.MEDIA_ROOT)
                obj.barcode_number=barcode_name
                obj.save()
                
                obj = Document.objects.get(id=document_id)
                file_path = obj.scan_upload.path

                # Get the original filename from the path
                original_filenames = os.path.basename(file_path)
                base_filename, file_extension = os.path.splitext(original_filenames)
                code = base_filename.split("_")[0]

                # Check if the barcode exists
                try:
                    barcode_obj = Document.objects.get(barcode_number=barcode_name)
                except Document.DoesNotExist:
                    return Response({"message": f"Document with barcode {code} does not exist."}, status=status.HTTP_404_NOT_FOUND)

                new_filename = f"{base_filename}{file_extension}"
                new_file_path = os.path.join(os.path.dirname(file_path), barcode_name + file_extension)

                # Read the content from the new file path
                uploaded_file = SimpleUploadedFile(name=new_filename, content=file.read())
                district_code = base_filename[:3]
                taluka_code = base_filename[3:7]
                village_code = base_filename[7:13]
                maptype_code = base_filename[13:15]
                try:
                # Get the district name from the District model
                    district = District.objects.get(district_code=district_code)
                    taluka = Taluka.objects.get(taluka_code=taluka_code)
                    village = Village.objects.get(village_code=village_code)
                    maptype = MapType.objects.get(map_code=maptype_code)
                    status_code = 1
                except Exception:
                    status_code = 28

                # Create a dictionary with the data to update
                scan_upload_by = self.request.user.id
                completed_date = datetime.now()
                update_data = {
                    'district_code':district.district_code,
                    'taluka_code':taluka.taluka_code,
                    'village_code':village.village_code,
                    'map_code':maptype.map_code,
                    'scan_upload': uploaded_file,
                    "scan_uploaded_by": scan_upload_by,
                    "scan_uploaded_date": completed_date,
                    "current_status": status_code
                }

                serializer = self.get_serializer(barcode_obj, data=update_data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    os.remove(file_path)
                    return Response({"message": f"Scan Files Updated"}, status=status.HTTP_200_OK)
                else:
                    return Response({"message": f"Error validating data for code {code}: {serializer.errors}"}, status=status.HTTP_400_BAD_REQUEST)

        except Document.DoesNotExist:
            print(f"Object with barcode does not exist.")

        return Response({"message": f" Scan Files Updated"}, status=status.HTTP_200_OK)
    
from unicodedata import normalize
import string

def clean_string(input_string):
    """Function to remove hidden characters from a string."""
    # Remove all characters except printable ASCII characters
    printable = set(string.printable)
    cleaned_string = ''.join(filter(lambda x: x in printable, input_string))
    return cleaned_string

class BelScanUploadedAPIVIew(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)
    serializer_class = UploadDocumentSerializer 

    def put(self, request, *args, **kwargs):
        # Get the uploaded file from the request
        action = kwargs.get('action', None)
        try:
            if action == 'bel_scan_uploaded':
                uploaded_file = request.FILES['file']  # Assuming 'file' is the key for the uploaded Excel file

                try:
                    # Read the Excel file using pandas
                    df = pd.read_excel(uploaded_file)
                except pd.errors.EmptyDataError:
                    return Response({"error": "The uploaded file is empty."}, status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
                
                df_filtered = df[df['Scan'] == 'C'].copy()
                df_filtered.loc[:, 'DOCID'] = df_filtered['DOCID'].apply(clean_string)

                # Extract cleaned barcode numbers from the Excel file
                excel_barcodes = df_filtered['DOCID'].tolist()

                # Iterate through barcode numbers
                for barcode in excel_barcodes:
                    try:
                        # Find documents with matching barcode numbers in the database
                        matching_documents = Document.objects.filter(barcode_number=barcode, rectify_completed_date__isnull=False)
                        if matching_documents.exists():
                            # Update bel_scan_uploaded for matching documents
                            matching_documents.update(bel_scan_uploaded=True, chk_bel_scan_uploaded="0")
                        else:
                            if Document.objects.filter(barcode_number=barcode).exists():
                                Document.objects.filter(barcode_number=barcode).update(chk_bel_scan_uploaded="2")
                            else:
                                MissingDocument.objects.update_or_create(barcode_number=barcode)
                    except Exception as e:
                        return Response({"error": f"Error processing barcode {barcode}: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    

                # Return response or perform additional actions as needed
                return Response({'message': 'Bel Scan Uploaded successfully'})

            elif action == 'bel_gov_scan_qc_approved':
                uploaded_file = request.FILES['file']  # Assuming 'file' is the key for the uploaded Excel file

                try:
                    # Read the Excel file using pandas
                    df = pd.read_excel(uploaded_file)
                except pd.errors.EmptyDataError:
                    return Response({"error": "The uploaded file is empty."}, status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

                # Clean the 'DOCID' column to remove hidden characters
                # df['DOCID'] = df['DOCID'].apply(clean_string)
                # df_filtered = df[df['QCSCAN'] == 'C']
                df_filtered = df[df['DeptQc Scan'] == 'C']
                df_filtered.loc[:, 'DOCID'] = df_filtered['DOCID'].apply(clean_string)

                # Extract cleaned barcode numbers from the Excel file
                excel_barcodes = df_filtered['DOCID'].tolist()

                # uploaded_file = request.FILES['file']  # Assuming 'file' is the key for the uploaded Excel file
                
                # # Read the Excel file using pandas
                # df = pd.read_excel(uploaded_file)
                
                # # Extract barcode numbers from the Excel file and remove backticks
                # excel_barcodes = df['DOCID'].tolist()  # Replace 'Barcode Column Name' with the actual column name
                # excel_barcodes = [barcode.replace('`', '') for barcode in excel_barcodes]

                # Iterate through barcode numbers
                
                for barcode in excel_barcodes:
                    try:
                        # Find documents with matching barcode numbers in the database
                        matching_documents = Document.objects.filter(barcode_number=barcode,rectify_completed_date__isnull=False,bel_scan_uploaded=True)
                        if matching_documents.exists():
                            # Update bel_scan_uploaded for matching documents
                            matching_documents.update(bel_gov_scan_qc_approved=True,bel_scan_uploaded=True,chk_bel_gov_scan_qc_approved="0")
                        else:
                            if Document.objects.filter(barcode_number=barcode).exists():
                                Document.objects.filter(barcode_number=barcode).update(chk_bel_gov_scan_qc_approved="2")
                            else:
                                MissingDocument.objects.update_or_create(barcode_number=barcode)
                    except Exception as e:
                        return Response({"error": f"Error processing barcode {barcode}: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    


                
                # Return response or perform additional actions as needed
                return Response({'message': 'Bel Government Scan Qc Approved successfully'})
            
            elif action == 'bel_draft_uploaded':
                uploaded_file = request.FILES['file']  # Assuming 'file' is the key for the uploaded Excel file

                try:
                    # Read the Excel file using pandas
                    df = pd.read_excel(uploaded_file)
                except pd.errors.EmptyDataError:
                    return Response({"error": "The uploaded file is empty."}, status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

                # Clean the 'DOCID' column to remove hidden characters
                # df['DOCID'] = df['DOCID'].apply(clean_string)
                df_filtered = df[df['Draft'] == 'C']
                df_filtered.loc[:, 'DOCID'] = df_filtered['DOCID'].apply(clean_string)


                # Extract cleaned barcode numbers from the Excel file
                excel_barcodes = df_filtered['DOCID'].tolist()

                # uploaded_file = request.FILES['file']  # Assuming 'file' is the key for the uploaded Excel file
                
                # # Read the Excel file using pandas
                # df = pd.read_excel(uploaded_file)
                
                # # Extract barcode numbers from the Excel file and remove backticks
                # excel_barcodes = df['DOCID'].tolist()  # Replace 'Barcode Column Name' with the actual column name
                # excel_barcodes = [barcode.replace('`', '') for barcode in excel_barcodes]

                # Iterate through barcode numbers
            

                for barcode in excel_barcodes:
                    try:
                        # Find documents with matching barcode numbers in the database
                        matching_documents = Document.objects.filter(barcode_number=barcode,pdf_completed_date__isnull=False)
                        if matching_documents.exists():
                            # Update bel_scan_uploaded for matching documents
                            matching_documents.update(bel_draft_uploaded=True,bel_scan_uploaded=True,bel_gov_scan_qc_approved=True,chk_bel_draft_uploaded="0")
                        else:
                            if Document.objects.filter(barcode_number=barcode).exists():
                                Document.objects.filter(barcode_number=barcode).update(chk_bel_draft_uploaded="2")
                            else:
                                MissingDocument.objects.update_or_create(barcode_number=barcode)
                    except Exception as e:
                        return Response({"error": f"Error processing barcode {barcode}: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    

                
                # Return response or perform additional actions as needed
                return Response({'message': 'Bel Draft Uploaded  successfully'})
            
            
            elif action == 'bel_gov_draft_qc_approved':
                uploaded_file = request.FILES['file']  # Assuming 'file' is the key for the uploaded Excel file

                try:
                    # Read the Excel file using pandas
                    df = pd.read_excel(uploaded_file)
                except pd.errors.EmptyDataError:
                    return Response({"error": "The uploaded file is empty."}, status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

                # Clean the 'DOCID' column to remove hidden characters
                # df['DOCID'] = df['DOCID'].apply(clean_string)
                # df_filtered = df[df['QCDraft'] == 'C']
                df_filtered = df[df['DeptQc Draft'] == 'C']
                df_filtered.loc[:, 'DOCID'] = df_filtered['DOCID'].apply(clean_string)

                # Extract cleaned barcode numbers from the Excel file
                excel_barcodes = df_filtered['DOCID'].tolist()

                # uploaded_file = request.FILES['file']  # Assuming 'file' is the key for the uploaded Excel file
                
                # # Read the Excel file using pandas
                # df = pd.read_excel(uploaded_file)
                
                # # Extract barcode numbers from the Excel file and remove backticks
                # excel_barcodes = df['DOCID'].tolist()  # Replace 'Barcode Column Name' with the actual column name
                # excel_barcodes = [barcode.replace('`', '') for barcode in excel_barcodes]

                # Iterate through barcode numbers
               
                for barcode in excel_barcodes:
                    try:
                        # Find documents with matching barcode numbers in the database
                        matching_documents = Document.objects.filter(barcode_number=barcode,pdf_completed_date__isnull=False,bel_draft_uploaded=True)
                        if matching_documents.exists():
                            # Update bel_scan_uploaded for matching documents
                            matching_documents.update(bel_gov_draft_qc_approved=True,bel_draft_uploaded=True,bel_scan_uploaded=True,bel_gov_scan_qc_approved=True,chk_bel_gov_draft_qc_approved="0")
                        else:
                            if Document.objects.filter(barcode_number=barcode).exists():
                                Document.objects.filter(barcode_number=barcode).update(chk_bel_gov_draft_qc_approved="2")
                            else:
                                MissingDocument.objects.update_or_create(barcode_number=barcode)
                    except Exception as e:
                        return Response({"error": f"Error processing barcode {barcode}: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    

                
                
                
                # Return response or perform additional actions as needed
                return Response({'message': 'Bel Government Draft Qc Approved successfully'})
            
            else:
                return Response({"message": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({'message':'Excle Column Name is Incorrect'})
        

class ReAssignDocumentListView(generics.ListAPIView):
    queryset = Document.objects.all()
    permission_classes = [IsAuthenticated,]
    authentication_classes = (TokenAuthentication,)
    serializer_class = AllDocumentListSerialzer
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend,filters.SearchFilter]
    search_fields = ["map_code"]
    filterset_fields = ['map_code','file_name','district_code','village_code','taluka_code']
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)

        if request.GET.get('is_export') and request.GET.get('is_export') in ['1', 1]:
            for_count = 0
            csv_header = ['Sr.No', 'File Name','Barcode Number','District','Taluka','Village','Map Code','Current Status','Remark',
                        'Scan By Username','Scan Uploaded Date','Rectify Agency Name','Rectify By Username','Rectify Assign Date','Rectify Completed Date',
                        'Digitize Agency Name','Digitize By Username','Digitize Assign Date','Digitize Completed Date','Polygon Count','QC Agency name','QC By Username',
                        'QC Assign Date','QC Completed Date','PDF By Username','PDF Assign Date','PDF Completed Date','Shape By Username',
                        'Shape Assign Date','Shape Completed Date']
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
                        qs.get('file_name'),
                        qs.get('barcode_number')+'`',
                        district_name,
                        taluka_name,
                        village_name,
                        qs.get('map_code'),
                        qs.get('current_status'),
                        qs.get('remarks',''),
                        qs.get('scan_by_username'),
                        format_datetime(qs.get('scan_uploaded_date')),
                        qs.get('rectify_agency_name'),
                        qs.get('rectify_by_username'),
                        format_datetime(qs.get('rectify_assign_date')),
                        format_datetime(qs.get('rectify_completed_date')),
                        qs.get('digitize_agency_name'),
                        qs.get('digitize_by_username'),
                        format_datetime(qs.get('digitize_assign_date')),
                        format_datetime(qs.get('digitize_completed_date')),
                        qs.get('polygon_count'),
                        qs.get('qc_agency_name'),
                        qs.get('qc_by_username'),
                        format_datetime(qs.get('qc_assign_date')),
                        format_datetime(qs.get('qc_completed_date')),
                        qs.get('pdf_by_username'),
                        format_datetime(qs.get('pdf_assign_date')),
                        format_datetime(qs.get('pdf_completed_date')),
                        qs.get('shape_by_username'),
                        format_datetime(qs.get('shape_assign_date')),
                        format_datetime(qs.get('shape_completed_date'))

                    ]
                )

            csv_data = generate_data_csv(csv_header, csv_body, f"report_data_{datetime.now()}_.csv")
            return Response({'csv_path': csv_data.get('csv_path')})

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        queryset = self.queryset
        agency_ids = User.objects.filter(id=self.request.user.id).values_list('agency', flat=True)
        team_ids = User.objects.filter(id=self.request.user.id).values_list('agency__team', flat=True)   
        if User.objects.filter(id=self.request.user.id, user_role__role_name="Super Admin"):
            query_set = queryset.all().exclude(current_status__in=[5,10,15,20,25]).order_by('-date_created')
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Team Admin"):
            query_set = queryset.filter(team_id__in=team_ids).exclude(current_status__in=[5,10,15,20,25]).order_by('-date_created')
       
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Agency Admin"):
            agency_filters = Q(rectify_agency_id__in=agency_ids) | Q(digitize_agency_id__in=agency_ids) | Q(qc_agency_id__in=agency_ids)
            query_set = queryset.filter(agency_filters).exclude(current_status__in=[5,10,15,20,25]).order_by('-date_created')
        else:
            query_set = queryset.none()  # Return an empty queryset for other roles
       
        barcode_number = self.request.query_params.get('barcode_number', None)
        village_name = self.request.query_params.get('village_name', None)
        taluka_name = self.request.query_params.get('taluka_name', None)
        district_name = self.request.query_params.get('district_name', None)
        scan_by_username = self.request.query_params.get('scan_by_username', None)
        rectify_by_username = self.request.query_params.get('rectify_by_username', None)
        digitize_by_username = self.request.query_params.get('digitize_by_username', None)
        qc_by_username = self.request.query_params.get('qc_by_username', None)
        pdf_by_username = self.request.query_params.get('pdf_by_username', None)
        shape_by_username = self.request.query_params.get('shape_by_username', None)
        current_status = self.request.query_params.get('current_status', None)
        scan_start_date = self.request.query_params.get('scan_start_date',None)
        scan_end_date = self.request.query_params.get('scan_end_date',None)
        rectify_start_date = self.request.query_params.get('rectify_start_date',None)
        rectify_end_date = self.request.query_params.get('rectify_end_date',None)
        digitize_start_date = self.request.query_params.get('digitize_start_date',None)
        digitize_end_date = self.request.query_params.get('digitize_end_date',None)
        qc_start_date = self.request.query_params.get('qc_start_date',None)
        qc_end_date = self.request.query_params.get('qc_end_date',None)

        if barcode_number:
            query_set = query_set.filter(barcode_number__icontains=barcode_number)

        if scan_start_date and scan_end_date:
            scan_start_date = datetime.strptime(scan_start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
            scan_end_date = datetime.strptime(scan_end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query_set = query_set.filter(
                        scan_uploaded_date__gte=scan_start_date.date(),
                        scan_uploaded_date__lt=(scan_end_date.date() + timedelta(days=1)))
            
        if rectify_start_date and rectify_end_date:
            rectify_start_date = datetime.strptime(rectify_start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
            rectify_end_date = datetime.strptime(rectify_end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query_set = query_set.filter(
                        rectify_completed_date__gte=rectify_start_date.date(),
                        rectify_completed_date__lt=(rectify_end_date.date() + timedelta(days=1)))
        
        if digitize_start_date and digitize_end_date:
            digitize_start_date = datetime.strptime(digitize_start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
            digitize_end_date = datetime.strptime(digitize_end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query_set = query_set.filter(
                        digitize_completed_date__gte=digitize_start_date.date(),
                        digitize_completed_date__lt=(digitize_end_date.date() + timedelta(days=1)))
        
        if qc_start_date and qc_end_date:
            qc_start_date = datetime.strptime(qc_start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
            qc_end_date = datetime.strptime(qc_end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query_set = query_set.filter(
                        qc_completed_date__gte=qc_start_date.date(),
                        qc_completed_date__lt=(qc_end_date.date() + timedelta(days=1)))

        if village_name:
            village_names = Village.objects.filter(village_name__icontains=village_name).values_list('village_code',flat=True)
            query_set = query_set.filter(village_code__in=village_names)
            

        if taluka_name:
            taluka_names = Taluka.objects.filter(taluka_name__icontains=taluka_name).values_list('taluka_code',flat=True)
            query_set = query_set.filter(taluka_code__in=taluka_names)


        if district_name:
            district_names = District.objects.filter(district_name__icontains=district_name).values_list('district_code',flat=True)
            query_set = query_set.filter(district_code__in=district_names)
        
        
        if scan_by_username:
            query_set = query_set.filter(scan_uploaded_by__username__icontains=scan_by_username)
        
        if rectify_by_username:
            query_set = query_set.filter(rectify_by__username__icontains=rectify_by_username)
            
        if digitize_by_username:
            query_set = query_set.filter(digitize_by__username__icontains=digitize_by_username)
            
        if qc_by_username:
            query_set = query_set.filter(qc_by__username__icontains=qc_by_username)
            
        if pdf_by_username:
            query_set = query_set.filter(pdf_by__username__icontains=pdf_by_username)
            
        if shape_by_username:
            query_set = query_set.filter(shape_by__username__icontains=shape_by_username)
        
        if current_status:
            query_set = query_set.filter(current_status__status__icontains=current_status)
            
        return query_set
    

class RectifyAgencyIdFillUpDocumentListView(generics.ListAPIView):
    queryset = Document.objects.all()
    permission_classes = [IsAuthenticated,]
    authentication_classes = (TokenAuthentication,)
    serializer_class = AllSerializer
 

    def get_queryset(self):
        queryset = self.queryset
        doci_id = queryset.all().exclude(taluka_code__in=[4284])
        assign_date =datetime.now()
        doci_id.update(rectify_agency_id=1,rectify_assign_date=assign_date)       
            
        return doci_id


def rectify_download_multiple_files(request,**kwargs):

    action = kwargs.get('action', None)
    try:
        document_ids_param = request.GET.get('document_ids', '')
        document_ids = document_ids_param.split(',') if document_ids_param else []

        if not document_ids:
            raise Http404("No document IDs provided")

        download_files = Document.objects.filter(id__in=document_ids)
        if not download_files.exists():
            raise Http404("No documents found for the provided IDs")

        in_memory_zip = io.BytesIO()

        with zipfile.ZipFile(in_memory_zip, mode='w') as zipf:
            for download_file in download_files:
                if action == 'scan':
                    barcode = download_file.barcode_number
                    file_path = download_file.scan_upload.path
                    # Get the original filename from the path
                    original_filename = os.path.basename(file_path)
                    prefix, extension = os.path.splitext(original_filename)#
                    modified_filename = barcode + extension#

                    # modified_filename = original_filename.replace("_O", "")
                elif action == 'rectify':
                    barcode = download_file.barcode_number
                    file_path = download_file.rectify_upload.path
                    
                    # Get the original filename from the path
                    original_filename = os.path.basename(file_path)

                    # Extract the part of the filename before "_R" (assuming "_R" is the marker)
                    prefix, extension = os.path.splitext(original_filename)
                    
                    # Replace the part before "_R" with the barcode
                    modified_filename = barcode + extension
                elif action == 'digitize':
                    barcode = download_file.barcode_number
                    file_path = download_file.digitize_upload.path
                    # Get the original filename from the path
                    original_filename = os.path.basename(file_path)
                    prefix, extension = os.path.splitext(original_filename)
                    modified_filename = barcode + extension
                elif action == 'qc':
                    barcode = download_file.barcode_number
                    file_path = download_file.qc_upload.path
                    # Get the original filename from the path
                    original_filename = os.path.basename(file_path)

                    prefix, extension = os.path.splitext(original_filename)
                    modified_filename = barcode + extension

                elif action == 'pdf':
                    barcode = download_file.barcode_number
                    file_path = download_file.pdf_upload.path

                    # Get the original filename from the path
                    original_filename = os.path.basename(file_path)

                    prefix, extension = os.path.splitext(original_filename)
                    modified_filename = barcode + extension
                
                elif action == 'gov_qc':
                    # file_path = download_file.gov_qc_upload.path

                    # # Get the original filename from the path
                    # original_filename = os.path.basename(file_path)
                    # modified_filename = original_filename

                    barcode = download_file.barcode_number
                    file_path = download_file.gov_qc_upload.path
                    # Get the original filename from the path
                    original_filename = os.path.basename(file_path)
                    prefix, extension = os.path.splitext(original_filename)
                    modified_filename = barcode + extension
                
                elif action == 'gov_pdf':
                    # file_path = download_file.gov_pdf_upload.path

                    # # Get the original filename from the path
                    # original_filename = os.path.basename(file_path)
                    # modified_filename = original_filename
                    

                    barcode = download_file.barcode_number
                    file_path = download_file.gov_pdf_upload.path
                    # Get the original filename from the path
                    original_filename = os.path.basename(file_path)
                    prefix, extension = os.path.splitext(original_filename)
                    modified_filename = barcode + extension

                elif action == 'not-found':
                    file_path = download_file.scan_upload.path
                    # Get the original filename from the path
                    original_filename = os.path.basename(file_path)
                    modified_filename = original_filename

                elif action == 'topology':
                    barcode = download_file.barcode_number
                    file_path = download_file.toplogy_upload.path
                    # Get the original filename from the path
                    original_filename = os.path.basename(file_path)
                    prefix, extension = os.path.splitext(original_filename)
                    modified_filename = barcode + extension
                
                elif action == 'shape':
                    barcode = download_file.barcode_number
                    file_path = download_file.shape_upload.path
                    # Get the original filename from the path
                    original_filename = os.path.basename(file_path)
                    prefix, extension = os.path.splitext(original_filename)
                    modified_filename = barcode + extension
                else:
                    return Response({"message": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)

                # Add the file to the zip archive
                zipf.write(file_path, arcname=modified_filename)
                

        in_memory_zip.seek(0)
        # Create the HTTP response with the zip file as an attachment
        response =  StreamingHttpResponse(in_memory_zip,content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="{action}_multiple_files.zip"'
        return response
    
   
    except Document.DoesNotExist:
        raise Http404("One or more documents do not exist")
    except Exception:
        return HttpResponse('Error creating zip file because document is not exits', status=404)


def download_exe_file(request):
    # Path to your exe file in the utility folder
    exe_file_path = os.path.join(settings.BASE_DIR, 'utility', 'compress_rectified_rename_move.exe')

    # Check if the file exists
    if os.path.exists(exe_file_path):
        # Open the file for reading in binary mode
        with open(exe_file_path, 'rb') as exe_file:
            response = HttpResponse(exe_file.read(), content_type='application/octet-stream')
            # Set the content-disposition header for the browser to treat as an attachment
            response['Content-Disposition'] = 'attachment; filename="compress_rectified_rename_move.exe"'
            return response
    else:
        return HttpResponse("File not found", status=404)
    


class BarcodeScanUploadAPIView(APIView):
    permission_classes = [IsAuthenticated,]
    authentication_classes = (TokenAuthentication,)

    def get(self, request, document_id):
        try:
            document = Document.objects.get(id=document_id)
        except Document.DoesNotExist:
            return JsonResponse({"message": "Document not found"}, status=404)

        if not document.scan_upload:
            return JsonResponse({"message": "No file uploaded for this document"}, status=400)

        # Get the path to the uploaded file
        uploaded_file_path = document.scan_upload.path

        # Read the uploaded image using OpenCV and decode the barcode
        img = cv2.imread(uploaded_file_path)
        detected_barcodes = decode(img)

        # Process the detected barcodes
        barcode_data = []
        if not detected_barcodes:
            barcode_data.append({"message": "Barcode Not Detected or your barcode is blank/corrupted!"})
        else:
            for barcode in detected_barcodes:
                if barcode.data != "":
                    barcode_data.append(barcode.data.decode('utf-8'))

        return JsonResponse({"barcodes": barcode_data})
    

class DeleteDocumentAPIView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = UploadDocumentSerializer

    
    def delete(self,*args,**kwargs):
        try:
            map_obj = Document.objects.get(id=kwargs.get("pk"))
            
            # Delete the files from the storage
            file_fields = [
                map_obj.scan_upload,
                map_obj.rectify_upload,
                map_obj.digitize_upload,
                map_obj.qc_upload,
                map_obj.pdf_upload,
                map_obj.shape_upload,
                map_obj.gov_qc_upload,
                map_obj.gov_pdf_upload
            ]
            
            for file_field in file_fields:
                if file_field and os.path.exists(file_field.path):
                    file_field.delete(save=False)
            
            map_obj.delete()
            return Response({"message": "Record deleted successfully", "status": True}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({"message": "Record not found", "status": False}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": str(e), "status": False}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ExchangeScanAssignToAgencyView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)
    serializer_class = UploadDocumentSerializer  # Use the custom serializer

    def put(self, request, *args, **kwargs):

        action = kwargs.get('action', None)
        try:
            if action == 'rectify':
                data = request.data.get('document_id', [])
                total_len = 0
                for file in data:
                    assign_date =datetime.now()
                    created_input_file = Document.objects.filter(id=file).update(rectify_agency_id=None,rectify_assign_date=None,rectify_by=None,digitize_agency_id=None,digitize_assign_date=None,digitize_by=None,qc_agency_id=None,qc_assign_date=None,qc_by=None,current_status=1)
                    total_len += 1
                return Response({"message": f"{total_len} Back To Rectify Allocated Files"}, status=status.HTTP_201_CREATED)
            elif action == 'digitize':
                data = request.data.get('document_id', [])
                total_len = 0
                for file in data:
                    assign_date =datetime.now()
                    created_input_file = Document.objects.filter(id=file).update(digitize_agency_id=None,digitize_assign_date=None,digitize_by=None,qc_agency_id=None,qc_assign_date=None,qc_by=None,current_status=5)
                    total_len += 1
                return Response({"message": f"{total_len} Back To Digitize Allocated Files"}, status=status.HTTP_201_CREATED)
            elif action == 'qc':                      
                data = request.data.get('document_id', [])
                total_len = 0
                for file in data:
                    assign_date =datetime.now()
                    created_input_file = Document.objects.filter(id=file).update(qc_agency_id=None,qc_assign_date=None,qc_by=None,current_status=10)
                    total_len += 1
                return Response({"message": f"{total_len} Back To QC Allocated Files"}, status=status.HTTP_201_CREATED)
            elif action == 'topology':                      
                data = request.data.get('document_id', [])
                total_len = 0
                for file in data:
                    assign_date =datetime.now()
                    created_input_file = Document.objects.filter(id=file).update(topology_agency_id=None,topology_assign_date=None,topology_by=None,current_status=30)
                    total_len += 1

                return Response({"message": f"{total_len} Back To QC Allocated Files"}, status=status.HTTP_201_CREATED)
            else:
                return Response({"message": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({'message':'Invalid Document ID'})

     
    



class ExchangeAssignAgencyDocumentListView(generics.ListAPIView):
    queryset = Document.objects.all()
    permission_classes = [IsAuthenticated,]
    authentication_classes = (TokenAuthentication,)
    serializer_class = ScanDocumentListSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend,filters.SearchFilter]
    search_fields = ["map_code"]
    filterset_fields = ['map_code','file_name','district_code','village_code','taluka_code']
    
 
    def get_queryset(self):
        queryset = self.queryset
        agency_ids = User.objects.filter(id=self.request.user.id).values_list('agency', flat=True)
        team_ids = User.objects.filter(id=self.request.user.id).values_list('agency__team', flat=True)   
        if User.objects.filter(id=self.request.user.id, user_role__role_name="Super Admin"):
            query_set = queryset.all().exclude(current_status__in=[5,10,15,20,25,23,24,25,26,27,33]).order_by('-date_created')
        
        else:
            query_set = queryset.none()  # Return an empty queryset for other roles
       
        barcode_number = self.request.query_params.get('barcode_number', None)
        village_name = self.request.query_params.get('village_name', None)
        taluka_name = self.request.query_params.get('taluka_name', None)
        district_name = self.request.query_params.get('district_name', None)
        scan_by_username = self.request.query_params.get('scan_by_username', None)
        rectify_by_username = self.request.query_params.get('rectify_by_username', None)
        digitize_by_username = self.request.query_params.get('digitize_by_username', None)
        qc_by_username = self.request.query_params.get('qc_by_username', None)
        pdf_by_username = self.request.query_params.get('pdf_by_username', None)
        shape_by_username = self.request.query_params.get('shape_by_username', None)
        current_status = self.request.query_params.get('current_status', None)
        scan_start_date = self.request.query_params.get('scan_start_date',None)
        scan_end_date = self.request.query_params.get('scan_end_date',None)
        rectify_start_date = self.request.query_params.get('rectify_start_date',None)
        rectify_end_date = self.request.query_params.get('rectify_end_date',None)
        digitize_start_date = self.request.query_params.get('digitize_start_date',None)
        digitize_end_date = self.request.query_params.get('digitize_end_date',None)
        qc_start_date = self.request.query_params.get('qc_start_date',None)
        qc_end_date = self.request.query_params.get('qc_end_date',None)
        rectify_agency_name=self.request.query_params.get('rectify_agency_name',None)
        digitize_agency_name=self.request.query_params.get('digitize_agency_name',None)
        qc_agency_name=self.request.query_params.get('qc_agency_name',None)
        topology_agency_name=self.request.query_params.get('topology_agency_name',None)


        if barcode_number:
            query_set = query_set.filter(barcode_number__icontains=barcode_number)
        
        if rectify_agency_name:
            query_set = query_set.filter(rectify_agency_id__agency_name__icontains=rectify_agency_name)
        
        if digitize_agency_name:
            query_set = query_set.filter(digitize_agency_id__agency_name__icontains=digitize_agency_name)
        
        if qc_agency_name:
            query_set = query_set.filter(qc_agency_id__agency_name__icontains=qc_agency_name)

        if topology_agency_name:
            query_set = query_set.filter(topology_agency_id__agency_name__icontains=topology_agency_name)

        if scan_start_date and scan_end_date:
            scan_start_date = datetime.strptime(scan_start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
            scan_end_date = datetime.strptime(scan_end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query_set = query_set.filter(
                        scan_uploaded_date__gte=scan_start_date.date(),
                        scan_uploaded_date__lt=(scan_end_date.date() + timedelta(days=1)))
            
        if rectify_start_date and rectify_end_date:
            rectify_start_date = datetime.strptime(rectify_start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
            rectify_end_date = datetime.strptime(rectify_end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query_set = query_set.filter(
                        rectify_completed_date__gte=rectify_start_date.date(),
                        rectify_completed_date__lt=(rectify_end_date.date() + timedelta(days=1)))
        
        if digitize_start_date and digitize_end_date:
            digitize_start_date = datetime.strptime(digitize_start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
            digitize_end_date = datetime.strptime(digitize_end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query_set = query_set.filter(
                        digitize_completed_date__gte=digitize_start_date.date(),
                        digitize_completed_date__lt=(digitize_end_date.date() + timedelta(days=1)))
        
        if qc_start_date and qc_end_date:
            qc_start_date = datetime.strptime(qc_start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
            qc_end_date = datetime.strptime(qc_end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query_set = query_set.filter(
                        qc_completed_date__gte=qc_start_date.date(),
                        qc_completed_date__lt=(qc_end_date.date() + timedelta(days=1)))

        if village_name:
            village_names = Village.objects.filter(village_name__icontains=village_name).values_list('village_code',flat=True)
            query_set = query_set.filter(village_code__in=village_names)
            

        if taluka_name:
            taluka_names = Taluka.objects.filter(taluka_name__icontains=taluka_name).values_list('taluka_code',flat=True)
            query_set = query_set.filter(taluka_code__in=taluka_names)


        if district_name:
            district_names = District.objects.filter(district_name__icontains=district_name).values_list('district_code',flat=True)
            query_set = query_set.filter(district_code__in=district_names)
        
        
        if scan_by_username:
            query_set = query_set.filter(scan_uploaded_by__username__icontains=scan_by_username)
        
        if rectify_by_username:
            query_set = query_set.filter(rectify_by__username__icontains=rectify_by_username)
            
        if digitize_by_username:
            query_set = query_set.filter(digitize_by__username__icontains=digitize_by_username)
            
        if qc_by_username:
            query_set = query_set.filter(qc_by__username__icontains=qc_by_username)
            
        if pdf_by_username:
            query_set = query_set.filter(pdf_by__username__icontains=pdf_by_username)
            
        if shape_by_username:
            query_set = query_set.filter(shape_by__username__icontains=shape_by_username)
        
        if current_status:
            query_set = query_set.filter(current_status__status__icontains=current_status)
            
            
        return query_set
    

from unicodedata import normalize
import string

def clean_string(input_string):
    """Function to remove hidden characters from a string."""
    # Remove all characters except printable ASCII characters
    printable = set(string.printable)
    cleaned_string = ''.join(filter(lambda x: x in printable, input_string))
    return cleaned_string

class CompareBarcodeView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    authentication_classes = (TokenAuthentication,)

    def get(self, request, *args, **kwargs):
        # Get the uploaded file from the request
        uploaded_file = request.FILES['file']  # Assuming 'file' is the key for the uploaded Excel file

        try:
            # Read the Excel file using pandas
            df = pd.read_excel(uploaded_file)
        except pd.errors.EmptyDataError:
            return Response({"error": "The uploaded file is empty."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Clean the 'DOCID' column to remove hidden characters
        df['DOCID'] = df['DOCID'].apply(clean_string)

        # Extract cleaned barcode numbers from the Excel file
        excel_barcodes = df['DOCID'].tolist()

        # Initialize a list to store unmatched barcode data
        unmatched_data = []

        # Iterate through barcode numbers
        for barcode in excel_barcodes:
            # Find documents with matching barcode numbers in the database
            matching_documents = Document.objects.filter(barcode_number=barcode)
            
            # If there are no matching documents, add the data to the unmatched_data list
            if not matching_documents.exists():
                unmatched_data.append(df[df['DOCID'] == barcode])

        # Concatenate the unmatched data into a new DataFrame
        if unmatched_data:
            unmatched_df = pd.concat(unmatched_data)
        else:
            unmatched_df = pd.DataFrame()  # Create an empty DataFrame if no unmatched data found

        # Save the unmatched data to a new Excel file
        media_path = os.path.join(settings.MEDIA_ROOT, 'unmatched_data.xlsx')
        unmatched_df.to_excel(media_path, index=False)

        # Get the relative path of the file
        relative_path = os.path.relpath(media_path, settings.MEDIA_ROOT)

        # Prepare the response with the relative file path
        response_data = {
            'message': 'Unmatched data saved to {}'.format(relative_path),
            'file_path': relative_path,
        }

        return Response(response_data, status=status.HTTP_200_OK)

    # def get(self, request, *args, **kwargs):
    #     # Get the uploaded file from the request
    #     uploaded_file = request.FILES['file']  # Assuming 'file' is the key for the uploaded Excel file

    #     try:
    #         # Read the Excel file using pandas
    #         df = pd.read_excel(uploaded_file)
    #     except pd.errors.EmptyDataError:
    #         return Response({"error": "The uploaded file is empty."}, status=status.HTTP_400_BAD_REQUEST)
    #     except Exception as e:
    #         return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    #     # Extract barcode numbers from the Excel file and remove backticks
    #     excel_barcodes = df['DOCID'].tolist()  # Replace 'Barcode Column Name' with the actual column name
    #     excel_barcodes = [barcode.replace('`', '') for barcode in excel_barcodes]

    #     # Initialize a list to store unmatched barcode data
    #     unmatched_data = []

    #     # Iterate through barcode numbers
    #     for barcode in excel_barcodes:
    #         # Find documents with matching barcode numbers in the database
    #         matching_documents = Document.objects.filter(barcode_number=barcode)
            
    #         # If there are no matching documents, add the data to the unmatched_data list
    #         if not matching_documents.exists():
    #             # Assuming 'Barcode Column Name' is the column containing barcode numbers in the Excel file
    #             unmatched_data.append(df[df['DOCID'] == barcode])

    #     # Concatenate the unmatched data into a new DataFrame
    #     unmatched_df = pd.concat(unmatched_data)

    #     # Save the unmatched data to a new Excel file
    #     media_path = os.path.join(settings.MEDIA_ROOT, 'unmatched_data.xlsx')
    #     unmatched_df.to_excel(media_path, index=False)

    #     # Get the relative path of the file
    #     relative_path = os.path.relpath(media_path, settings.MEDIA_ROOT)

    #     # Prepare the response with the relative file path
    #     response_data = {
    #         'message': 'Unmatched data saved to {}'.format(relative_path),
    #         'file_path': relative_path,
    #     }

    #     return Response(response_data, status=status.HTTP_200_OK)

# class CompareBarcodeView(generics.GenericAPIView):
#     permission_classes = [AllowAny]
#     authentication_classes = (TokenAuthentication,)

#     def get(self, request, *args, **kwargs):
#         # Get the uploaded file from the request
#         uploaded_file = request.FILES['file']  # Assuming 'file' is the key for the uploaded Excel file

#         try:
#             # Read the Excel file using pandas
#             df = pd.read_excel(uploaded_file)
#         except pd.errors.EmptyDataError:
#             return Response({"error": "The uploaded file is empty."}, status=status.HTTP_400_BAD_REQUEST)
#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

#         # Extract barcode numbers from the Excel file and remove backticks
#         excel_barcodes = df['DOCID'].tolist()  # Replace 'Barcode Column Name' with the actual column name
#         excel_barcodes = [barcode.replace('`', '') for barcode in excel_barcodes]

#         # Initialize a list to store unmatched barcode data
#         unmatched_data = []

#         # Iterate through barcode numbers
#         for barcode in excel_barcodes:
#             # Find documents with matching barcode numbers in the database
#             matching_documents = Document.objects.filter(barcode_number=barcode)
            
#             # If there are no matching documents, add the data to the unmatched_data list
#             if not matching_documents.exists():
#                 # Assuming 'Barcode Column Name' is the column containing barcode numbers in the Excel file
#                 unmatched_data.append(df[df['DOCID'] == barcode])

#         # Concatenate the unmatched data into a new DataFrame
#         unmatched_df = pd.concat(unmatched_data)

#         # Save the unmatched data to a new Excel file
#         media_path = os.path.join(settings.MEDIA_ROOT, 'unmatched_data.xlsx')
#         unmatched_df.to_excel(media_path, index=False)

#         # Get the relative path of the file
#         relative_path = os.path.relpath(media_path, settings.MEDIA_ROOT)

#         # Prepare the response with the relative file path
#         response_data = {
#             'message': 'Unmatched data saved to {}'.format(relative_path),
#             'file_path': relative_path,
#         }

#         return Response(response_data, status=status.HTTP_200_OK)


class CompareRectifyBarcodeView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    authentication_classes = (TokenAuthentication,)

    def get(self, request, *args, **kwargs):
        # Get the uploaded file from the request
        uploaded_file = request.FILES['file']  # Assuming 'file' is the key for the uploaded Excel file

        try:
            # Read the Excel file using pandas
            df = pd.read_excel(uploaded_file)
        except pd.errors.EmptyDataError:
            return Response({"error": "The uploaded file is empty."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Extract barcode numbers from the Excel file and remove backticks
        excel_barcodes = df['DOCID'].tolist()  # Replace 'Barcode Column Name' with the actual column name
        excel_barcodes = [barcode.replace('`', '') for barcode in excel_barcodes]

        # Initialize a list to store unmatched barcode data
        unmatched_data = []

        # Iterate through barcode numbers
        for barcode in excel_barcodes:
            # Find documents with matching barcode numbers in the database
            matching_documents = Document.objects.filter(barcode_number=barcode,rectify_completed_date__isnull=False)
            
            # If there are no matching documents, add the data to the unmatched_data list
            if not matching_documents.exists():
                # Assuming 'Barcode Column Name' is the column containing barcode numbers in the Excel file
                unmatched_data.append(df[df['DOCID'] == barcode])

        # Concatenate the unmatched data into a new DataFrame
        unmatched_df = pd.concat(unmatched_data)

        # Save the unmatched data to a new Excel file
        media_path = os.path.join(settings.MEDIA_ROOT, 'unmatched_data.xlsx')
        unmatched_df.to_excel(media_path, index=False)

        # Get the relative path of the file
        relative_path = os.path.relpath(media_path, settings.MEDIA_ROOT)

        # Prepare the response with the relative file path
        response_data = {
            'message': 'Unmatched data saved to {}'.format(relative_path),
            'file_path': relative_path,
        }

        return Response(response_data, status=status.HTTP_200_OK)


class CompareDigitzeBarcodeView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    authentication_classes = (TokenAuthentication,)

    def get(self, request, *args, **kwargs):
        # Get the uploaded file from the request
        uploaded_file = request.FILES['file']  # Assuming 'file' is the key for the uploaded Excel file

        try:
            # Read the Excel file using pandas
            df = pd.read_excel(uploaded_file)
        except pd.errors.EmptyDataError:
            return Response({"error": "The uploaded file is empty."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Extract barcode numbers from the Excel file and remove backticks
        excel_barcodes = df['DOCID'].tolist()  # Replace 'Barcode Column Name' with the actual column name
        excel_barcodes = [barcode.replace('`', '') for barcode in excel_barcodes]

        # Initialize a list to store unmatched barcode data
        unmatched_data = []

        # Iterate through barcode numbers
        for barcode in excel_barcodes:
            # Find documents with matching barcode numbers in the database
            matching_documents = Document.objects.filter(barcode_number=barcode,digitize_completed_date__isnull=False)
            
            # If there are no matching documents, add the data to the unmatched_data list
            if not matching_documents.exists():
                # Assuming 'Barcode Column Name' is the column containing barcode numbers in the Excel file
                unmatched_data.append(df[df['DOCID'] == barcode])

        # Concatenate the unmatched data into a new DataFrame
        unmatched_df = pd.concat(unmatched_data)

        # Save the unmatched data to a new Excel file
        media_path = os.path.join(settings.MEDIA_ROOT, 'unmatched_data.xlsx')
        unmatched_df.to_excel(media_path, index=False)

        # Get the relative path of the file
        relative_path = os.path.relpath(media_path, settings.MEDIA_ROOT)

        # Prepare the response with the relative file path
        response_data = {
            'message': 'Unmatched data saved to {}'.format(relative_path),
            'file_path': relative_path,
        }

        return Response(response_data, status=status.HTTP_200_OK)


class CompareQCBarcodeView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    authentication_classes = (TokenAuthentication,)

    def get(self, request, *args, **kwargs):
        # Get the uploaded file from the request
        uploaded_file = request.FILES['file']  # Assuming 'file' is the key for the uploaded Excel file

        try:
            # Read the Excel file using pandas
            df = pd.read_excel(uploaded_file)
        except pd.errors.EmptyDataError:
            return Response({"error": "The uploaded file is empty."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Extract barcode numbers from the Excel file and remove backticks
        excel_barcodes = df['DOCID'].tolist()  # Replace 'Barcode Column Name' with the actual column name
        excel_barcodes = [barcode.replace('`', '') for barcode in excel_barcodes]

        # Initialize a list to store unmatched barcode data
        unmatched_data = []

        # Iterate through barcode numbers
        for barcode in excel_barcodes:
            # Find documents with matching barcode numbers in the database
            matching_documents = Document.objects.filter(barcode_number=barcode,qc_completed_date__isnull=False)
            
            # If there are no matching documents, add the data to the unmatched_data list
            if not matching_documents.exists():
                # Assuming 'Barcode Column Name' is the column containing barcode numbers in the Excel file
                unmatched_data.append(df[df['DOCID'] == barcode])

        # Concatenate the unmatched data into a new DataFrame
        unmatched_df = pd.concat(unmatched_data)

        # Save the unmatched data to a new Excel file
        media_path = os.path.join(settings.MEDIA_ROOT, 'unmatched_data.xlsx')
        unmatched_df.to_excel(media_path, index=False)

        # Get the relative path of the file
        relative_path = os.path.relpath(media_path, settings.MEDIA_ROOT)

        # Prepare the response with the relative file path
        response_data = {
            'message': 'Unmatched data saved to {}'.format(relative_path),
            'file_path': relative_path,
        }

        return Response(response_data, status=status.HTTP_200_OK)





class GetDocumentIDView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    authentication_classes = (TokenAuthentication,)

    def get(self, request, *args, **kwargs):
        # Get the uploaded file from the request
        uploaded_file = request.FILES['file']  # Assuming 'file' is the key for the uploaded Excel file

        try:
            # Read the Excel file using pandas
            df = pd.read_excel(uploaded_file)
        except pd.errors.EmptyDataError:
            return Response({"error": "The uploaded file is empty."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Extract barcode numbers from the Excel file and remove backticks
        excel_barcodes = df['DOCID'].tolist()  # Replace 'Barcode Column Name' with the actual column name
        excel_barcodes = [barcode.replace('`', '') for barcode in excel_barcodes]

        # Initialize a list to store unmatched barcode data
        unmatched_data = []

        # Iterate through barcode numbers
        for barcode in excel_barcodes:
            # Find documents with matching barcode numbers in the database
            matching_documents = Document.objects.filter(barcode_number=barcode).values('id','barcode_number','scan_upload','rectify_upload','digitize_upload','current_status__status')
            unmatched_data.extend(matching_documents)


        return Response(unmatched_data, status=status.HTTP_200_OK)
    

class GovtQCFileCreateView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)
    serializer_class = UploadDocumentSerializer  # Use the custom serializer

    def put(self, request, *args, **kwargs):
        # Extract the action from the URL

        data = request.FILES.getlist('files')
        total_len = 0

        for file in data:     
            filename = file.name
            base_filename,file_extension = os.path.splitext(filename)
            code = base_filename.split("_")[0]

            try:
                # Get the existing object based on the barcode
                obj = Document.objects.get(barcode_number=code,qc_completed_date__isnull=False,current_status__in=[20,29])

                if file_extension.lower() == ".dwg":
                    new_filename = f"{base_filename}{file_extension}"
               
                # Create a SimpleUploadedFile with the file data
                uploaded_file = SimpleUploadedFile(name=new_filename, content=file.read())

                # Create a dictionary with the data to update
                qc_obj = self.request.user.id
                qc_agency_id = self.request.user.agency.id
                completed_date = datetime.now()


                if file_extension.lower() == ".dwg":
                    update_data = {
                        'gov_approve_agency_id':qc_agency_id,
                        "gov_qc_upload": uploaded_file,  # Pass the uploaded file data
                        "gov_qc_by": qc_obj,
                        "gov_qc_completed_date": completed_date,
                        "current_status": 30
                    }

                serializer = self.get_serializer(obj, data=update_data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    total_len += 1
                else:
                    print(f"Error validating data for code {code}: {serializer.errors}")

            except Document.DoesNotExist:
                print(f"Object with barcode {code} does not exist.")

        return Response({"message": f"{total_len} Qc Files Updated"}, status=status.HTTP_200_OK)
    

class GovtPdfFileCreateView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)
    serializer_class = UploadDocumentSerializer  # Use the custom serializer

    def put(self, request, *args, **kwargs):
        # Extract the action from the URL

        data = request.FILES.getlist('files')
        total_len = 0

        for file in data:     
            filename = file.name
            base_filename,file_extension = os.path.splitext(filename)
            code = base_filename.split("_")[0]

            try:
                # Get the existing object based on the barcode
                obj = Document.objects.get(barcode_number=code,gov_qc_completed_date__isnull=False,current_status__in=[30])

                if file_extension.lower() == ".pdf":
                    new_filename = f"{base_filename}{file_extension}"
               
                # Create a SimpleUploadedFile with the file data
                uploaded_file = SimpleUploadedFile(name=new_filename, content=file.read())

                # Create a dictionary with the data to update

                completed_date = datetime.now()

                if file_extension.lower() == ".pdf":
                    update_data = {
                        "gov_pdf_upload": uploaded_file,
                        "gov_pdf_completed_date":completed_date
                    }

                serializer = self.get_serializer(obj, data=update_data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    total_len += 1
                else:
                    print(f"Error validating data for code {code}: {serializer.errors}")

            except Document.DoesNotExist:
                print(f"Object with barcode {code} does not exist.")

        return Response({"message": f"{total_len} Qc Files Updated"}, status=status.HTTP_200_OK)
    
class TopoDwgFileUploadView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)
    serializer_class = UploadDocumentSerializer  # Use the custom serializer

    def put(self, request, *args, **kwargs):
        # Extract the action from the URL
        action = kwargs.get('action', None)
           

        if action == 'approved':
            data = request.FILES.getlist('files')
            total_len = 0

            for file in data:
                filename = file.name
                base_filename,file_extension = os.path.splitext(filename)
                code = base_filename.split("_")[0]

                try:
                    # Get the existing object based on the barcode
                    obj = Document.objects.get(barcode_number=code,gov_pdf_completed_date__isnull=False,current_status__in=[31,32,35,26])
                    if file_extension.lower() == ".dwg":
                        new_filename = f"{base_filename}{file_extension}"
                    # Create a SimpleUploadedFile with the file data
                    uploaded_file = SimpleUploadedFile(name=new_filename, content=file.read())

                    # Create a dictionary with the data to update
                    topo_user_obj = self.request.user.id
                    completed_date = datetime.now()
                    update_data = {
                        "toplogy_upload": uploaded_file,
                        "topology_by":topo_user_obj,
                        "shape_by":topo_user_obj,
                        "topology_completed_date":completed_date,
                        "shape_assign_date":completed_date,
                        "current_status": 23
                    }
                    

                    serializer = self.get_serializer(obj, data=update_data, partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        total_len += 1
                    else:
                        print(f"Error validating data for code {code}: {serializer.errors}")

                except Document.DoesNotExist:
                    print(f"Object with barcode {code} does not exist.")

            return Response({"message": f"{total_len} Topology Files Updated"}, status=status.HTTP_200_OK)

        elif action == 'rejected':
            data = request.data

            # Assuming you send a list of dictionaries with update data
            update_data_list = data

            for update_data in update_data_list:
                document_id = update_data.get("id")
                try:
                    rectify_obj = Document.objects.get(id=document_id)
                except Document.DoesNotExist:
                    return Response({"msg": f"Record with ID {document_id} does not exist"})

                # Update the fields specified in the dictionary
                serializer = UploadDocumentSerializer(rectify_obj, data=update_data, partial=True)
                if serializer.is_valid():
                    serializer.save(current_status=DocumentStatus.objects.get(id=34))
        
            return Response({"message": "Topology Files Rejected"})
            # Handle 'rejected' action here
            # Update current_status to 1 for the appropriate documents
            # Add your code for the 'rejected' action here

        elif action == 'onhold':
            data = request.data

            # Assuming you send a list of dictionaries with update data
            update_data_list = data

            for update_data in update_data_list:
                document_id = update_data.get("id")
                try:
                    rectify_obj = Document.objects.get(id=document_id)
                except Document.DoesNotExist:
                    return Response({"msg": f"Record with ID {document_id} does not exist"})

                # Update the fields specified in the dictionary
                serializer = UploadDocumentSerializer(rectify_obj, data=update_data, partial=True)
                if serializer.is_valid():
                    serializer.save(current_status=DocumentStatus.objects.get(id=35))
        
            return Response({"message": "Topology Files On-Hold"})
            # Handle 'onhold' action here
            # Update current_status to 2 for the appropriate documents
            # Add your code for the 'onhold' action here

        else:
            return Response({"message": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)
        

class GovtPendingListView(ListAPIView):
    queryset = Document.objects.all()
    permission_classes = [IsAuthenticated,]
    authentication_classes = (TokenAuthentication,)
    serializer_class = PdfDocumentListSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend,filters.SearchFilter]
    search_fields = []
    filterset_fields = ['taluka_code']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)

        if request.GET.get('is_export') and request.GET.get('is_export') in ['1', 1]:
            for_count = 0
            csv_header = ['Sr.No', 'File Name','District','Taluka','Village','Map Code','Digitize Polygon','QC Polygon','Current Status','Remark']
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
                        qs.get('file_name'),
                        district_name,
                        taluka_name,
                        village_name,
                        qs.get('map_code'),
                        qs.get('polygon_count'),
                        qs.get('qc_polygon_count'),
                        qs.get('current_status'),
                        qs.get('remarks',''),
                       
                    ]
                )

            csv_data = generate_data_csv(csv_header, csv_body, f"pdf_report_{datetime.now()}_.csv")
            return Response({'csv_path': csv_data.get('csv_path')})

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        queryset = self.queryset
        agency_ids = User.objects.filter(id=self.request.user.id).values_list('agency', flat=True)
        if User.objects.filter(id=self.request.user.id, user_role__role_name="Super Admin"):
            query_set = queryset.filter(current_status=20).order_by('-date_created')
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Agency Admin"):
            query_set = queryset.filter(qc_agency_id__in=agency_ids,current_status=20).order_by('-date_created')
        else:
            query_set = queryset.filter(gov_qc_by=self.request.user.id,current_status=29).order_by('-date_created')
        
        village_name = self.request.query_params.get('village_name', None)
        taluka_name = self.request.query_params.get('taluka_name', None)
        district_name = self.request.query_params.get('district_name', None)
        barcode_number = self.request.query_params.get('barcode_number', None)
        file_name = self.request.query_params.get('file_name', None)
        district_code = self.request.query_params.get('district_code', None)
        village_code = self.request.query_params.get('village_code', None)
        map_code = self.request.query_params.get('map_code', None)
        current_status = self.request.query_params.get('current_status', None)

        
        if village_name:
            village_names = Village.objects.filter(village_name__icontains=village_name).values_list('village_code',flat=True)
            query_set = query_set.filter(village_code__in=village_names)
            

        if taluka_name:
            taluka_names = Taluka.objects.filter(taluka_name__icontains=taluka_name).values_list('taluka_code',flat=True)
            query_set = query_set.filter(taluka_code__in=taluka_names)


        if district_name:
            district_names = District.objects.filter(district_name__icontains=district_name).values_list('district_code',flat=True)
            query_set = query_set.filter(district_code__in=district_names)
        
        
        if barcode_number:
            query_set = query_set.filter(barcode_number__icontains=barcode_number)
        
        if file_name:
            query_set = query_set.filter(file_name__icontains=file_name)
            
        if district_code:
            query_set = query_set.filter(district_code__icontains=district_code)
        
        if village_code:
            query_set = query_set.filter(village_code__icontains=village_code)
       
        if map_code:
            query_set = query_set.filter(map_code__icontains=map_code)
        
        if current_status:
            query_set = query_set.filter(current_status__status__icontains=current_status)

        return query_set

class GovtQcAssignDistrictAdmin(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)
    serializer_class = UploadDocumentSerializer  # Use the custom serializer

    def put(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id')
        try:
            user_id = get_object_or_404(User, id=user_id)
        except Http404:
            return Response({"message": f"Agency with ID {user_id} does not exist"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.get('document_id', [])
        total_len = 0

        for file in data:
            assign_date =datetime.now()
            created_input_file = Document.objects.filter(id=file,gov_qc_by__isnull=True).update(gov_qc_by=user_id,gov_qc_assign_date=assign_date,current_status=29)
            if created_input_file > 0:
                total_len += 1
        return Response({"message": f"{total_len} Govt Qc Document Assign To User"}, status=status.HTTP_201_CREATED)
    


class Read_Barcode_Details_Api(generics.GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        data = str(kwargs.get('barcode'))          
        try:
            district_code = data[:3]
            taluka_code = data[3:7]
            village_code = data[7:13]
            maptype_code = data[13:15]

            district = District.objects.get(district_code=district_code)
            taluka = Taluka.objects.get(taluka_code=taluka_code)
            village = Village.objects.get(village_code=village_code)
            maptype = MapType.objects.get(map_code=maptype_code)

            update_data = {
                'district_name': district.district_name if district else None,
                'taluka_name': taluka.taluka_name if taluka else None,
                'village_name': village.village_name if village else None,
                'maptype_name': maptype.mapname_english if maptype else None
            }
            
            return Response({"data": update_data})
        
        except (District.DoesNotExist, Taluka.DoesNotExist, Village.DoesNotExist, MapType.DoesNotExist) as e:
            return Response({"error": "One or more items not found."})
        

class GovtPDFPendingListView(ListAPIView):
    queryset = Document.objects.all()
    permission_classes = [IsAuthenticated,]
    authentication_classes = (TokenAuthentication,)
    serializer_class = PdfDocumentListSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend,filters.SearchFilter]
    search_fields = []
    filterset_fields = ['taluka_code']

    def get_queryset(self):
        queryset = self.queryset
        agency_ids = User.objects.filter(id=self.request.user.id).values_list('agency', flat=True)
        if User.objects.filter(id=self.request.user.id, user_role__role_name="Super Admin"):
            query_set = queryset.filter(current_status=30).order_by('-date_created')
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Agency Admin"):
            query_set = queryset.filter(qc_agency_id__in=agency_ids,current_status=30).order_by('-date_created')
        else:
            query_set = queryset.filter(gov_qc_by=self.request.user.id,current_status=30,gov_pdf_completed_date__isnull=True).order_by('-date_created')
        
        village_name = self.request.query_params.get('village_name', None)
        taluka_name = self.request.query_params.get('taluka_name', None)
        district_name = self.request.query_params.get('district_name', None)
        barcode_number = self.request.query_params.get('barcode_number', None)
        file_name = self.request.query_params.get('file_name', None)
        district_code = self.request.query_params.get('district_code', None)
        village_code = self.request.query_params.get('village_code', None)
        map_code = self.request.query_params.get('map_code', None)
        current_status = self.request.query_params.get('current_status', None)

        
        if village_name:
            village_names = Village.objects.filter(village_name__icontains=village_name).values_list('village_code',flat=True)
            query_set = query_set.filter(village_code__in=village_names)
            

        if taluka_name:
            taluka_names = Taluka.objects.filter(taluka_name__icontains=taluka_name).values_list('taluka_code',flat=True)
            query_set = query_set.filter(taluka_code__in=taluka_names)


        if district_name:
            district_names = District.objects.filter(district_name__icontains=district_name).values_list('district_code',flat=True)
            query_set = query_set.filter(district_code__in=district_names)
        
        
        if barcode_number:
            query_set = query_set.filter(barcode_number__icontains=barcode_number)
        
        if file_name:
            query_set = query_set.filter(file_name__icontains=file_name)
            
        if district_code:
            query_set = query_set.filter(district_code__icontains=district_code)
        
        if village_code:
            query_set = query_set.filter(village_code__icontains=village_code)
       
        if map_code:
            query_set = query_set.filter(map_code__icontains=map_code)
        
        if current_status:
            query_set = query_set.filter(current_status__status__icontains=current_status)

        return query_set




class MissingPolygonCountDocumentListView(generics.ListAPIView):
    queryset = Document.objects.all()
    permission_classes = [IsAuthenticated,]
    authentication_classes = (TokenAuthentication,)
    serializer_class = AllDocumentListSerialzer
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend,filters.SearchFilter]
    filterset_fields = ['map_code','file_name','polygon_count','qc_polygon_count','district_code','village_code','taluka_code','bel_scan_uploaded','bel_draft_uploaded','bel_gov_scan_qc_approved','bel_gov_draft_qc_approved']
    

    def get_queryset(self):
        queryset = self.queryset

        if User.objects.filter(id=self.request.user.id, user_role__role_name="Super Admin"):
            query_set = queryset.filter(Q(qc_completed_date__isnull=False) & (Q(polygon_count=0) | Q(qc_polygon_count=0))).order_by('-date_created')
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Agency Admin"):
            agency_ids = User.objects.filter(id=self.request.user.id).values_list('agency', flat=True)
            agency_filters = Q(qc_completed_date__isnull=False) & Q(qc_agency_id__in=agency_ids) | Q(polygon_count=0) | Q(qc_polygon_count=0)
            query_set = queryset.filter(agency_filters).order_by('-date_created')
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="User"):
            current_status_values = [15,18,20]
            agency_filters =Q(qc_completed_date__isnull=False) & Q(polygon_count=0) | Q(qc_polygon_count=0)
            query_set = queryset.filter(agency_filters,qc_by=self.request.user.id,current_status__in=current_status_values).order_by('-date_created')
        
        else:
            query_set = queryset.none()  # Return an empty queryset for other roles
        
        barcode_number = self.request.query_params.get('barcode_number', None)
        village_name = self.request.query_params.get('village_name', None)
        taluka_name = self.request.query_params.get('taluka_name', None)
        district_name = self.request.query_params.get('district_name', None)
        scan_by_username = self.request.query_params.get('scan_by_username', None)
        rectify_by_username = self.request.query_params.get('rectify_by_username', None)
        digitize_by_username = self.request.query_params.get('digitize_by_username', None)
        qc_by_username = self.request.query_params.get('qc_by_username', None)
        pdf_by_username = self.request.query_params.get('pdf_by_username', None)
        shape_by_username = self.request.query_params.get('shape_by_username', None)
        current_status = self.request.query_params.get('current_status', None)
        scan_start_date = self.request.query_params.get('scan_start_date',None)
        scan_end_date = self.request.query_params.get('scan_end_date',None)
        rectify_start_date = self.request.query_params.get('rectify_start_date',None)
        rectify_end_date = self.request.query_params.get('rectify_end_date',None)
        digitize_start_date = self.request.query_params.get('digitize_start_date',None)
        digitize_end_date = self.request.query_params.get('digitize_end_date',None)
        qc_start_date = self.request.query_params.get('qc_start_date',None)
        qc_end_date = self.request.query_params.get('qc_end_date',None)
        
        rectify_agency_name=self.request.query_params.get('rectify_agency_name',None)
        digitize_agency_name=self.request.query_params.get('digitize_agency_name',None)
        qc_agency_name=self.request.query_params.get('qc_agency_name',None)
        gov_qc_by_username=self.request.query_params.get('gov_qc_by_username',None)

        polygon_min = self.request.query_params.get('polygon_min', None)
        polygon_max = self.request.query_params.get('polygon_max', None)

        rectify_assign_start_date = self.request.query_params.get('rectify_assign_start_date',None)
        rectify_assign_end_date = self.request.query_params.get('rectify_assign_end_date',None)
    
        digitize_assign_start_date = self.request.query_params.get('digitize_assign_start_date',None)
        digitize_assign_end_date = self.request.query_params.get('digitize_assign_end_date',None)
    

        qc_assign_start_date = self.request.query_params.get('qc_assign_start_date',None)
        qc_assign_end_date = self.request.query_params.get('qc_assign_end_date',None)

        gov_qc_assign_start_date = self.request.query_params.get('gov_qc_assign_start_date',None)
        gov_qc_assign_end_date = self.request.query_params.get('gov_qc_assign_end_date',None)
    
        gov_qc_completed_start_date = self.request.query_params.get('gov_qc_completed_start_date',None)
        gov_qc_completed_end_date = self.request.query_params.get('gov_qc_completed_end_date',None)

        if gov_qc_assign_start_date and gov_qc_assign_end_date:
            gov_qc_assign_start_date = datetime.strptime(gov_qc_assign_start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
            gov_qc_assign_end_date = datetime.strptime(gov_qc_assign_end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query_set = query_set.filter(
                        gov_qc_assign_date__gte=gov_qc_assign_start_date.date(),
                        gov_qc_assign_date__lt=(gov_qc_assign_end_date.date() + timedelta(days=1)))
            
        if gov_qc_completed_start_date and gov_qc_completed_end_date:
            gov_qc_completed_start_date = datetime.strptime(gov_qc_completed_start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
            gov_qc_completed_end_date = datetime.strptime(gov_qc_completed_end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query_set = query_set.filter(
                        gov_qc_completed_date__gte=gov_qc_completed_start_date.date(),
                        gov_qc_completed_date__lt=(gov_qc_completed_end_date.date() + timedelta(days=1)))

        if polygon_min and polygon_max:
            try:
                polygon_min = int(polygon_min)
                polygon_max = int(polygon_max)
                query_set = query_set.filter(polygon_count__range=(polygon_min, polygon_max))
            except ValueError:
                query_set = query_set.none()  # Return an empty queryset
    

        if rectify_agency_name:
            query_set = query_set.filter(rectify_agency_id__agency_name__icontains=rectify_agency_name)
        
        if digitize_agency_name:
            query_set = query_set.filter(digitize_agency_id__agency_name__icontains=digitize_agency_name)
        
        if qc_agency_name:
            query_set = query_set.filter(qc_agency_id__agency_name__icontains=qc_agency_name)
        
        if gov_qc_by_username:
            query_set = query_set.filter(gov_qc_by__username__icontains=gov_qc_by_username)

        if barcode_number:
            query_set = query_set.filter(barcode_number__icontains=barcode_number)
        
        if scan_start_date and scan_end_date:
            scan_start_date = datetime.strptime(scan_start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
            scan_end_date = datetime.strptime(scan_end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query_set = query_set.filter(
                        scan_uploaded_date__gte=scan_start_date.date(),
                        scan_uploaded_date__lt=(scan_end_date.date() + timedelta(days=1)))
            
        if rectify_start_date and rectify_end_date:
            rectify_start_date = datetime.strptime(rectify_start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
            rectify_end_date = datetime.strptime(rectify_end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query_set = query_set.filter(
                        rectify_completed_date__gte=rectify_start_date.date(),
                        rectify_completed_date__lt=(rectify_end_date.date() + timedelta(days=1)))
        
        if digitize_start_date and digitize_end_date:
            digitize_start_date = datetime.strptime(digitize_start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
            digitize_end_date = datetime.strptime(digitize_end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query_set = query_set.filter(
                        digitize_completed_date__gte=digitize_start_date.date(),
                        digitize_completed_date__lt=(digitize_end_date.date() + timedelta(days=1)))
        
        if qc_start_date and qc_end_date:
            qc_start_date = datetime.strptime(qc_start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
            qc_end_date = datetime.strptime(qc_end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query_set = query_set.filter(
                        qc_completed_date__gte=qc_start_date.date(),
                        qc_completed_date__lt=(qc_end_date.date() + timedelta(days=1)))
            
        if rectify_assign_start_date and rectify_assign_end_date:
            rectify_assign_start_date = datetime.strptime(rectify_assign_start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
            rectify_assign_end_date = datetime.strptime(rectify_assign_end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query_set = query_set.filter(
                        rectify_assign_date__gte=rectify_assign_start_date.date(),
                        rectify_assign_date__lt=(rectify_assign_end_date.date() + timedelta(days=1)))
        
        if digitize_assign_start_date and digitize_assign_end_date:
            digitize_assign_start_date = datetime.strptime(digitize_assign_start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
            digitize_assign_end_date = datetime.strptime(digitize_assign_end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query_set = query_set.filter(
                        digitize_assign_date__gte=digitize_assign_start_date.date(),
                        digitize_assign_date__lt=(digitize_assign_end_date.date() + timedelta(days=1)))
    
            
        if qc_assign_start_date and qc_assign_end_date:
            qc_assign_start_date = datetime.strptime(qc_assign_start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
            qc_assign_end_date = datetime.strptime(qc_assign_end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query_set = query_set.filter(
                        qc_assign_date__gte=qc_assign_start_date.date(),
                        qc_assign_date__lt=(qc_assign_end_date.date() + timedelta(days=1)))
            
            
        if village_name:
            village_names = Village.objects.filter(village_name__icontains=village_name).values_list('village_code',flat=True)
            query_set = query_set.filter(village_code__in=village_names)
            

        if taluka_name:
            taluka_names = Taluka.objects.filter(taluka_name__icontains=taluka_name).values_list('taluka_code',flat=True)
            query_set = query_set.filter(taluka_code__in=taluka_names)


        if district_name:
            district_names = District.objects.filter(district_name__icontains=district_name).values_list('district_code',flat=True)
            query_set = query_set.filter(district_code__in=district_names)
        
        
        if scan_by_username:
            query_set = query_set.filter(scan_uploaded_by__username__icontains=scan_by_username)
        
        if rectify_by_username:
            query_set = query_set.filter(rectify_by__username__icontains=rectify_by_username)
            
        if digitize_by_username:
            query_set = query_set.filter(digitize_by__username__icontains=digitize_by_username)
            
        if qc_by_username:
            query_set = query_set.filter(qc_by__username__icontains=qc_by_username)
            
        if pdf_by_username:
            query_set = query_set.filter(pdf_by__username__icontains=pdf_by_username)
            
        if shape_by_username:
            query_set = query_set.filter(shape_by__username__icontains=shape_by_username)
        
        if current_status:
            query_set = query_set.filter(current_status__status__icontains=current_status)
            
        return query_set
    
class MissingDocumentListView(ListAPIView):
    queryset = MissingDocument.objects.all()
    permission_classes = [IsAuthenticated,]
    authentication_classes = (TokenAuthentication,)
    serializer_class = MissingDocumentSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend,filters.SearchFilter]
    search_fields = []
    filterset_fields = ['barcode_number']

    def get_queryset(self):
        queryset = self.queryset
        if User.objects.filter(id=self.request.user.id, user_role__role_name="Super Admin"):
            query_set = queryset.all().order_by('-date_created')
        else:
            query_set = queryset.none()  # Return an empty queryset for other roles
        
        return query_set


class GetDocumentPath(generics.GenericAPIView):
    permission_classes = [AllowAny]
    authentication_classes = (TokenAuthentication,)

    def get(self, request, *args, **kwargs):
        data = request.data
        action = kwargs.get('action', None)
        barcode_number = data.get("barcode")

        try:
            barcode = Document.objects.get(barcode_number=barcode_number)

            if action == 'scan':
                file_path = barcode.scan_upload.path
            elif action == 'rectify':
                file_path = barcode.rectify_upload.path
            elif action == 'digitize':
                file_path = barcode.digitize_upload.path
            elif action == 'qc':
                file_path = barcode.qc_upload.path
            elif action == 'pdf':
                file_path = barcode.pdf_upload.path
            elif action == 'gov_qc':
                file_path = barcode.gov_qc_upload.path
            elif action == 'gov_pdf':
                file_path = barcode.gov_pdf_upload.path
            else:
                return Response({"message": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)

            response_data = {
                "file_path": file_path,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Document.DoesNotExist:
            raise Http404("Document with this barcode number does not exist")
        except Exception as e:
            # Handle unexpected exceptions gracefully
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
       



class NewGetDocumentPath(generics.GenericAPIView):
    permission_classes = [AllowAny]
    authentication_classes = (TokenAuthentication,)

    def get(self, request, *args, **kwargs):
        data = request.data
        action = kwargs.get('action', None)
        taluka_code = data.get("taluka_code")

        try:
            if action == 'BEL_SCAN':
                taluka_files = Document.objects.filter(taluka_code=taluka_code, bel_scan_uploaded=False,rectify_completed_date__isnull=False)
                
                if taluka_files.exists():
                    file_paths = [self.prepend_base_url(taluka_file.rectify_upload.url) for taluka_file in taluka_files]
                    
                    response_data = {
                        "file_paths": file_paths,
                    }
                    return Response(response_data, status=status.HTTP_200_OK)
                else:
                    return Response({"message": "No documents found matching the criteria"}, status=status.HTTP_404_NOT_FOUND)
                
            if action == 'BEL_SCAN_QC':
                taluka_files = Document.objects.filter(taluka_code=taluka_code, bel_gov_scan_qc_approved=False,rectify_completed_date__isnull=False)
                
                if taluka_files.exists():
                    file_paths = [self.prepend_base_url(taluka_file.rectify_upload.url) for taluka_file in taluka_files]
                    
                    response_data = {
                        "file_paths": file_paths,
                    }
                    return Response(response_data, status=status.HTTP_200_OK)
                else:
                    return Response({"message": "No documents found matching the criteria"}, status=status.HTTP_404_NOT_FOUND)
            
            if action == 'BEL_DRAFT':
                taluka_files = Document.objects.filter(taluka_code=taluka_code, bel_draft_uploaded=False,qc_completed_date__isnull=False)
                
                if taluka_files.exists():
                    file_paths = [self.prepend_base_url(taluka_file.qc_upload.url) for taluka_file in taluka_files]
                    
                    response_data = {
                        "file_paths": file_paths,
                    }
                    return Response(response_data, status=status.HTTP_200_OK)
                else:
                    return Response({"message": "No documents found matching the criteria"}, status=status.HTTP_404_NOT_FOUND)
            
            if action == 'BEL_DRAFT_QC':
                taluka_files = Document.objects.filter(taluka_code=taluka_code, bel_gov_draft_qc_approved=False,qc_completed_date__isnull=False)
                
                if taluka_files.exists():
                    file_paths = [self.prepend_base_url(taluka_file.qc_upload.url) for taluka_file in taluka_files]
                    
                    response_data = {
                        "file_paths": file_paths,
                    }
                    return Response(response_data, status=status.HTTP_200_OK)
                else:
                    return Response({"message": "No documents found matching the criteria"}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({"message": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)
            
        except Document.DoesNotExist:
            raise Http404("Document with this barcode number does not exist")
        except Exception as e:
            # Handle unexpected exceptions gracefully
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def prepend_base_url(self, file_path):
        base_url = "http://filemanagement.metaxpay.in:8001"
        return f"{base_url}{file_path}"


from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authentication import TokenAuthentication
import pandas as pd
import os
from django.conf import settings

class TwoCSVFileCompareBarcodeView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    authentication_classes = (TokenAuthentication,)

    def get(self, request, *args, **kwargs):
        uploaded_file = request.FILES['file']

        try:
            # Read the CSV file using pandas
            df = pd.read_csv(uploaded_file)
        except pd.errors.EmptyDataError:
            return Response({"error": "The uploaded file is empty."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        excel_barcodes = df['Filename'].tolist()
        excel_barcodes = [barcode for barcode in excel_barcodes]

        unmatched_data = []
        matched_data = []

        for barcode in excel_barcodes:
            matching_documents = Document.objects.filter(file_name=barcode)
            
            if not matching_documents.exists():
                unmatched_data.append(df[df['Filename'] == barcode])
            else:
                matched_df = df[df['Filename'] == barcode].copy()
                matched_df['current_status'] = matching_documents.first().current_status.status
                matched_data.append(matched_df)

        unmatched_df = pd.concat(unmatched_data)
        matched_df = pd.concat(matched_data)

        unmatched_file_path = os.path.join(settings.MEDIA_ROOT, 'unmatched_data.csv')
        matched_file_path = os.path.join(settings.MEDIA_ROOT, 'matched_data.csv')
        zip_file_path = os.path.join(settings.MEDIA_ROOT, 'barcode_data.zip')

        # Save CSV files
        unmatched_df.to_csv(unmatched_file_path, index=False)
        matched_df.to_csv(matched_file_path, index=False)

        # Create a zip file
        with zipfile.ZipFile(zip_file_path, 'w') as zip_file:
            zip_file.write(unmatched_file_path, os.path.basename(unmatched_file_path))
            zip_file.write(matched_file_path, os.path.basename(matched_file_path))

        # Remove the individual CSV files to clean up
        os.remove(unmatched_file_path)
        os.remove(matched_file_path)

        with open(zip_file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename={os.path.basename(zip_file_path)}'
        
        # Remove the zip file after sending it to the client
        os.remove(zip_file_path)
        
        return response

        # Prepare the response with the path to the zip file
        # zip_relative_path = os.path.relpath(zip_file_path, settings.MEDIA_ROOT)

        # response_data = {
        #     'zip_file_path': zip_relative_path,
        # }

        # return Response(response_data, status=status.HTTP_200_OK)

class CompareNineThirtyBarcodearcodeView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    authentication_classes = (TokenAuthentication,)

    def get(self, request, *args, **kwargs):
        uploaded_file = request.FILES['file']  # Assuming 'file' is the key for the uploaded Excel file

        try:
            df = pd.read_excel(uploaded_file)
        except pd.errors.EmptyDataError:
            return Response({"error": "The uploaded file is empty."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        df['DOCID'] = df['DOCID'].apply(clean_string)

        excel_barcodes = df['DOCID'].tolist()

        unmatched_data = []

        for barcode in excel_barcodes:
            code = barcode.split("_")[0]
            maptype_code = code[13:15]


            if maptype_code == "09" or maptype_code == "13":
                print("Selected maptype_code:", maptype_code)
                
                matching_documents = Document.objects.filter(barcode_number=barcode, map_code=maptype_code)
                
                if not matching_documents.exists():
                    unmatched_data.append(df[df['DOCID'] == barcode])

            
        if unmatched_data:
            unmatched_df = pd.concat(unmatched_data)
        else:
            unmatched_df = pd.DataFrame() 

        # Save the unmatched data to a new Excel file
        media_path = os.path.join(settings.MEDIA_ROOT, 'unmatched_data.xlsx')
        unmatched_df.to_excel(media_path, index=False)

        # Get the relative path of the file
        relative_path = os.path.relpath(media_path, settings.MEDIA_ROOT)

        # Prepare the response with the relative file path
        response_data = {
            'message': 'Unmatched data saved to {}'.format(relative_path),
            'file_path': relative_path,
        }

        return Response(response_data, status=status.HTTP_200_OK)
    


class GovtQcCompleteListView(ListAPIView):
    queryset = Document.objects.all()
    permission_classes = [IsAuthenticated,]
    authentication_classes = (TokenAuthentication,)
    serializer_class = GovQcDocumentListSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend,filters.SearchFilter]
    search_fields = []
    filterset_fields = ['taluka_code']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)

        if request.GET.get('is_export') and request.GET.get('is_export') in ['1', 1]:
            for_count = 0
            csv_header = ['Sr.No', 'File Name','District','Taluka','Village','Map Code','Digitize Polygon_Count','QC Polygon Count','Current Status','Remark']
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
                        qs.get('file_name'),
                        district_name,
                        taluka_name,
                        village_name,
                        qs.get('map_code'),
                        qs.get('polygon_count'),
                        qs.get('qc_polygon_count'),
                        qs.get('current_status'),
                        qs.get('remarks',''),
                       
                    ]
                )

            csv_data = generate_data_csv(csv_header, csv_body, f"digitize_report_{datetime.now()}_.csv")
            return Response({'csv_path': csv_data.get('csv_path')})

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)




    def get_queryset(self):
        queryset = self.queryset
        agency_ids = User.objects.filter(id=self.request.user.id).values_list('agency', flat=True)
        if User.objects.filter(id=self.request.user.id, user_role__role_name="Super Admin"):
            query_set = queryset.filter(current_status=30,gov_pdf_completed_date__isnull=False).order_by('-date_created')
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Agency Admin"):
            query_set = queryset.filter(topology_agency_id__in=agency_ids,current_status=31).exclude(topology_by__isnull=False).order_by('-date_created')
        else:
            current_status_values = [26,31,32,34,35]
            query_set = queryset.filter(topology_by=self.request.user.id,current_status__in=current_status_values).order_by('-date_created')

        village_name = self.request.query_params.get('village_name', None)
        taluka_name = self.request.query_params.get('taluka_name', None)
        district_name = self.request.query_params.get('district_name', None)
        barcode_number = self.request.query_params.get('barcode_number', None)
        file_name = self.request.query_params.get('file_name', None)
        district_code = self.request.query_params.get('district_code', None)
        village_code = self.request.query_params.get('village_code', None)
        map_code = self.request.query_params.get('map_code', None)
        current_status = self.request.query_params.get('current_status', None)
        scan_by_username = self.request.query_params.get('scan_by_username', None)
        rectify_by_username = self.request.query_params.get('rectify_by_username', None)
        digitize_by_username = self.request.query_params.get('digitize_by_username', None)
        qc_by_username = self.request.query_params.get('qc_by_username', None)
        pdf_by_username = self.request.query_params.get('pdf_by_username', None)
        shape_by_username = self.request.query_params.get('shape_by_username', None)
        qc_start_date = self.request.query_params.get('qc_start_date',None)
        qc_end_date = self.request.query_params.get('qc_end_date',None)

        if qc_start_date and qc_end_date:
            qc_start_date = datetime.strptime(qc_start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
            qc_end_date = datetime.strptime(qc_end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query_set = query_set.filter(
                        qc_completed_date__gte=qc_start_date.date(),
                        qc_completed_date__lt=(qc_end_date.date() + timedelta(days=1)))

        if village_name:
            village_names = Village.objects.filter(village_name__icontains=village_name).values_list('village_code',flat=True)
            query_set = query_set.filter(village_code__in=village_names)
            

        if taluka_name:
            taluka_names = Taluka.objects.filter(taluka_name__icontains=taluka_name).values_list('taluka_code',flat=True)
            query_set = query_set.filter(taluka_code__in=taluka_names)


        if district_name:
            district_names = District.objects.filter(district_name__icontains=district_name).values_list('district_code',flat=True)
            query_set = query_set.filter(district_code__in=district_names)
        
        
        if barcode_number:
            query_set = query_set.filter(barcode_number__icontains=barcode_number)
        
        if file_name:
            query_set = query_set.filter(file_name__icontains=file_name)
            
        if district_code:
            query_set = query_set.filter(district_code__icontains=district_code)
        
        if village_code:
            query_set = query_set.filter(village_code__icontains=village_code)
       
        if map_code:
            query_set = query_set.filter(map_code__icontains=map_code)

        
        if scan_by_username:
            query_set = query_set.filter(scan_uploaded_by__username__icontains=scan_by_username)
        
        if rectify_by_username:
            query_set = query_set.filter(rectify_by__username__icontains=rectify_by_username)
            
        if digitize_by_username:
            query_set = query_set.filter(digitize_by__username__icontains=digitize_by_username)
            
        if qc_by_username:
            query_set = query_set.filter(qc_by__username__icontains=qc_by_username)
            
        if pdf_by_username:
            query_set = query_set.filter(pdf_by__username__icontains=pdf_by_username)
            
        if shape_by_username:
            query_set = query_set.filter(shape_by__username__icontains=shape_by_username)
        
        
        if current_status:
            query_set = query_set.filter(current_status__status__icontains=current_status)

        return query_set
    

class TopologyCompleteListView(ListAPIView):
    queryset = Document.objects.all()
    permission_classes = [IsAuthenticated,]
    authentication_classes = (TokenAuthentication,)
    serializer_class = GovQcDocumentListSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend,filters.SearchFilter]
    search_fields = []
    filterset_fields = ['taluka_code']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)

        if request.GET.get('is_export') and request.GET.get('is_export') in ['1', 1]:
            for_count = 0
            csv_header = ['Sr.No', 'File Name','District','Taluka','Village','Map Code','Digitize Polygon_Count','QC Polygon Count','Current Status','Remark']
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
                        qs.get('file_name'),
                        district_name,
                        taluka_name,
                        village_name,
                        qs.get('map_code'),
                        qs.get('polygon_count'),
                        qs.get('qc_polygon_count'),
                        qs.get('current_status'),
                        qs.get('remarks',''),
                       
                    ]
                )

            csv_data = generate_data_csv(csv_header, csv_body, f"digitize_report_{datetime.now()}_.csv")
            return Response({'csv_path': csv_data.get('csv_path')})

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)




    def get_queryset(self):
        queryset = self.queryset
        agency_ids = User.objects.filter(id=self.request.user.id).values_list('agency', flat=True)
        if User.objects.filter(id=self.request.user.id, user_role__role_name="Super Admin"):
            query_set = queryset.filter(current_status=33,topology_completed_date__isnull=False).order_by('-date_created')
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Agency Admin"):
            query_set = queryset.filter(shape_agency_id__in=agency_ids,current_status=23).exclude(shape_by__isnull=False).order_by('-date_created')
        else:
            current_status_values = [23,24,27,33]
            query_set = queryset.filter(shape_by=self.request.user.id,current_status__in=current_status_values).order_by('-date_created')

        village_name = self.request.query_params.get('village_name', None)
        taluka_name = self.request.query_params.get('taluka_name', None)
        district_name = self.request.query_params.get('district_name', None)
        barcode_number = self.request.query_params.get('barcode_number', None)
        file_name = self.request.query_params.get('file_name', None)
        district_code = self.request.query_params.get('district_code', None)
        village_code = self.request.query_params.get('village_code', None)
        map_code = self.request.query_params.get('map_code', None)
        current_status = self.request.query_params.get('current_status', None)
        scan_by_username = self.request.query_params.get('scan_by_username', None)
        rectify_by_username = self.request.query_params.get('rectify_by_username', None)
        digitize_by_username = self.request.query_params.get('digitize_by_username', None)
        qc_by_username = self.request.query_params.get('qc_by_username', None)
        pdf_by_username = self.request.query_params.get('pdf_by_username', None)
        shape_by_username = self.request.query_params.get('shape_by_username', None)
        qc_start_date = self.request.query_params.get('qc_start_date',None)
        qc_end_date = self.request.query_params.get('qc_end_date',None)

        if qc_start_date and qc_end_date:
            qc_start_date = datetime.strptime(qc_start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
            qc_end_date = datetime.strptime(qc_end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query_set = query_set.filter(
                        qc_completed_date__gte=qc_start_date.date(),
                        qc_completed_date__lt=(qc_end_date.date() + timedelta(days=1)))

        if village_name:
            village_names = Village.objects.filter(village_name__icontains=village_name).values_list('village_code',flat=True)
            query_set = query_set.filter(village_code__in=village_names)
            

        if taluka_name:
            taluka_names = Taluka.objects.filter(taluka_name__icontains=taluka_name).values_list('taluka_code',flat=True)
            query_set = query_set.filter(taluka_code__in=taluka_names)


        if district_name:
            district_names = District.objects.filter(district_name__icontains=district_name).values_list('district_code',flat=True)
            query_set = query_set.filter(district_code__in=district_names)
        
        
        if barcode_number:
            query_set = query_set.filter(barcode_number__icontains=barcode_number)
        
        if file_name:
            query_set = query_set.filter(file_name__icontains=file_name)
            
        if district_code:
            query_set = query_set.filter(district_code__icontains=district_code)
        
        if village_code:
            query_set = query_set.filter(village_code__icontains=village_code)
       
        if map_code:
            query_set = query_set.filter(map_code__icontains=map_code)

        
        if scan_by_username:
            query_set = query_set.filter(scan_uploaded_by__username__icontains=scan_by_username)
        
        if rectify_by_username:
            query_set = query_set.filter(rectify_by__username__icontains=rectify_by_username)
            
        if digitize_by_username:
            query_set = query_set.filter(digitize_by__username__icontains=digitize_by_username)
            
        if qc_by_username:
            query_set = query_set.filter(qc_by__username__icontains=qc_by_username)
            
        if pdf_by_username:
            query_set = query_set.filter(pdf_by__username__icontains=pdf_by_username)
            
        if shape_by_username:
            query_set = query_set.filter(shape_by__username__icontains=shape_by_username)
        
        
        if current_status:
            query_set = query_set.filter(current_status__status__icontains=current_status)

        return query_set
class GetDocumentDownloadURL(generics.GenericAPIView):
    permission_classes = [AllowAny]
    authentication_classes = (TokenAuthentication,)

    def get(self, request, *args, **kwargs):
        data = request.data
        action = kwargs.get('action', None)
        barcode_number = data.get("barcode")
        

        try:
            barcode = Document.objects.get(barcode_number=barcode_number)

            if action == 'scan':
                file_path = barcode.scan_upload.url
            elif action == 'rectify':
                file_path = barcode.rectify_upload.url
            elif action == 'digitize':
                file_path = barcode.digitize_upload.url
            elif action == 'qc':
                file_path = barcode.qc_upload.url
            elif action == 'pdf':
                file_path = barcode.pdf_upload.url
            elif action == 'gov_qc':
                file_path = barcode.gov_qc_upload.url
            elif action == 'gov_pdf':
                file_path = barcode.gov_pdf_upload.url
            else:
                return Response({"message": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)

            absolute_file_path = request.build_absolute_uri(file_path)
            response_data = {
                "file_path": absolute_file_path,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Document.DoesNotExist:
            raise Http404("Document with this barcode number does not exist")
        except Exception as e:
            # Handle unexpected exceptions gracefully
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

###############################



# if action == 'bel_scan_uploaded':
            #     uploaded_file = request.FILES['file']  # Assuming 'file' is the key for the uploaded Excel file

            #     try:
            #         # Read the Excel file using pandas
            #         df = pd.read_excel(uploaded_file)
            #     except pd.errors.EmptyDataError:
            #         return Response({"error": "The uploaded file is empty."}, status=status.HTTP_400_BAD_REQUEST)
            #     except Exception as e:
            #         return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
                
            #     df_filtered = df[df['Scan'] == 'C']
            #     df_filtered['DOCID'] = df_filtered['DOCID'].apply(clean_string)

            #     # Clean the 'DOCID' column to remove hidden characters
            #     # df['DOCID'] = df['DOCID'].apply(clean_string)

            #     # Extract cleaned barcode numbers from the Excel file
            #     excel_barcodes = df_filtered['DOCID'].tolist()



            #     # uploaded_file = request.FILES['file']  # Assuming 'file' is the key for the uploaded Excel file
                
            #     # # Read the Excel file using pandas
            #     # df = pd.read_excel(uploaded_file)
                
            #     # # Extract barcode numbers from the Excel file and remove backticks
            #     # excel_barcodes = df['DOCID'].tolist()  # Replace 'Barcode Column Name' with the actual column name
            #     # excel_barcodes = [barcode.replace('`', '') for barcode in excel_barcodes]

            #     # Iterate through barcode numbers
            #     for barcode in excel_barcodes:
                    
            #         # Find documents with matching barcode numbers in the database
            #         matching_documents = Document.objects.filter(barcode_number=barcode,rectify_completed_date__isnull=False)
            #         if matching_documents.exists():
            #             # Update bel_scan_uploaded for matching documents
            #             matching_documents.update(bel_scan_uploaded=True,chk_bel_scan_uploaded="0")
            #         else:
            #             if Document.objects.filter(barcode_number=barcode):
            #                Document.objects.filter(barcode_number=barcode).update(chk_bel_scan_uploaded="2")
            #             else:
            #                 MissingDocument.objects.update_or_create(barcode_number=barcode)
            

            #     # Return response or perform additional actions as needed
            #     return Response({'message': 'Bel Scan Uploaded  successfully'})

#########################################################################################


class UpdateGovtUserGenericAPI(generics.GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = UploadDocumentSerializer
    
    def put(self,request,*args,**kwargs):
        try:
            govt_qc_obj = Document.objects.get(barcode_number=kwargs.get("barcode_number"))
        except govt_qc_obj.DoesNotExist:
            return Response({"msg":"record does not exist"})
        serializer = UploadDocumentSerializer(govt_qc_obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data,"message":"Success","status":True})
        


class VillageWiseNineThirteenCountView(APIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    # This API User Base Count Display
    def get(self, request,village_code=None):
        village_code_obj = Village.objects.get(village_code=village_code)
        map_09_count = Document.objects.filter(village_code=village_code,map_code="09").count()
        map_13_count = Document.objects.filter(village_code=village_code,map_code="13").count()
    

        response_data = {
            'village_name': village_code_obj.village_name,
            'village_code': village_code_obj.village_code,
            'map_09_count'  : map_09_count,
            'map_13_count' : map_13_count,
            'status': True
        }

        return Response(data=response_data, status=status.HTTP_200_OK)
    

class TalukaVillageWiseNineThirteenCountView(APIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    # This API User Base Count Display
    def get(self, request,taluka_code=None):
        taluka_code = self.kwargs.get('taluka_code')
        
        if User.objects.filter(id=self.request.user.id, user_role__role_name__in=["Super Admin", "Agency Admin"]):
            doc_village_code = Document.objects.filter(taluka_code=taluka_code).values_list('village_code', flat=True).distinct()
            village = Village.objects.filter(village_code__in=doc_village_code).order_by('-date_created')

        else:
            village = []

        counts_by_village = []

        for village_obj in village:
            village_code = village_obj.village_code
            village_name = village_obj.village_name
            taluka_name = village_obj.taluka.taluka_name
  
  
            counts = {
                'map_09_count': 0,
                'map_13_count': 0,
               
            }

            counts['map_09_count'] = Document.objects.filter(village_code=village_code,map_code="09").count()
            counts['map_13_count'] = Document.objects.filter(village_code=village_code,map_code="13").count()
                            


            counts_by_village.append({
                'village_code':village_code,
                'village_name':village_name,
                'taluka_name':taluka_name,
                **counts,
            })

        response_data = {
            'counts_by_village': counts_by_village,
            'status': True
        }

        return Response(data=response_data, status=status.HTTP_200_OK)
    


class DownloadQCFilesAPIView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = [TokenAuthentication]

    def get(self, request, *args, **kwargs):
        documents = Document.objects.filter(map_code__in=['09', '13'], qc_completed_date__isnull=False)

        # Generator function to yield zip file chunks
        def generate_zip():
            with BytesIO() as zip_buffer:
                with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                    for document in documents:
                        file_path = document.qc_upload.path
                        if os.path.exists(file_path):
                            folder_name = f"map_{document.map_code}"
                            file_name = os.path.basename(file_path)
                            zip_file.write(file_path, os.path.join(folder_name, file_name))

                        # Yield chunks of the zip file to avoid memory issues
                        zip_buffer.seek(0)
                        yield zip_buffer.read()
                        zip_buffer.seek(0)
                        zip_buffer.truncate()

        # Return a StreamingHttpResponse that streams the file to the user
        response = StreamingHttpResponse(generate_zip(), content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="qc_documents.zip"'
        return response


class RectifyDigitizeUploadFileView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)
    serializer_class = UploadDocumentSerializer  # Use the custom serializer

    def put(self, request, *args, **kwargs):
        # Extract the action from the URL
        action = kwargs.get('action', None)


        if action == 'scan':
            data = request.FILES.getlist('files')
            total_len = 0

            for file in data:
                filename = file.name
                base_filename,file_extension = os.path.splitext(filename)
                code = base_filename.split("_")[0]

                try:
                    # Get the existing object based on the barcode
                    obj = Document.objects.get(barcode_number=code)
                    new_filename = f"{base_filename}{file_extension}"

                    # Create a SimpleUploadedFile with the file data
                    uploaded_file = SimpleUploadedFile(name=new_filename, content=file.read())

                    # Create a dictionary with the data to update
                    update_data = {
                        'scan_upload': uploaded_file,  # Pass the uploaded file data
                    }

                    serializer = self.get_serializer(obj, data=update_data, partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        total_len += 1
                    else:
                        print(f"Error validating data for code {code}: {serializer.errors}")

                except Document.DoesNotExist:
                    print(f"Object with barcode {code} does not exist.")

            return Response({"message": f"{total_len} Scan Files Updated"}, status=status.HTTP_200_OK)
        

        if action == 'rectify':
            data = request.FILES.getlist('files')
            total_len = 0

            for file in data:
                filename = file.name
                base_filename,file_extension = os.path.splitext(filename)
                code = base_filename.split("_")[0]

                try:
                    # Get the existing object based on the barcode
                    obj = Document.objects.get(barcode_number=code)
                    new_filename = f"{base_filename}{file_extension}"

                    # Create a SimpleUploadedFile with the file data
                    uploaded_file = SimpleUploadedFile(name=new_filename, content=file.read())

                    # Create a dictionary with the data to update
                    update_data = {
                        'rectify_upload': uploaded_file,  # Pass the uploaded file data
                    }

                    serializer = self.get_serializer(obj, data=update_data, partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        total_len += 1
                    else:
                        print(f"Error validating data for code {code}: {serializer.errors}")

                except Document.DoesNotExist:
                    print(f"Object with barcode {code} does not exist.")

            return Response({"message": f"{total_len} Rectify Files Updated"}, status=status.HTTP_200_OK)
        
        if action == 'digitize':
            data = request.FILES.getlist('files')
            total_len = 0

            for file in data:
                filename = file.name
                base_filename,file_extension = os.path.splitext(filename)
                code = base_filename.split("_")[0]

                try:
                    # Get the existing object based on the barcode
                    obj = Document.objects.get(barcode_number=code)
                    new_filename = f"{base_filename}{file_extension}"

                    # Create a SimpleUploadedFile with the file data
                    uploaded_file = SimpleUploadedFile(name=new_filename, content=file.read())

                    # Create a dictionary with the data to update
                    update_data = {
                        'digitize_upload': uploaded_file,  # Pass the uploaded file data
                    }

                    serializer = self.get_serializer(obj, data=update_data, partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        total_len += 1
                    else:
                        print(f"Error validating data for code {code}: {serializer.errors}")

                except Document.DoesNotExist:
                    print(f"Object with barcode {code} does not exist.")

            return Response({"message": f"{total_len} Digitize Files Updated"}, status=status.HTTP_200_OK)
        
        if action == 'qc':
            data = request.FILES.getlist('files')
            total_len = 0

            for file in data:
                filename = file.name
                base_filename,file_extension = os.path.splitext(filename)
                code = base_filename.split("_")[0]

                try:
                    # Get the existing object based on the barcode
                    obj = Document.objects.get(barcode_number=code)
                    new_filename = f"{base_filename}{file_extension}"

                    # Create a SimpleUploadedFile with the file data
                    uploaded_file = SimpleUploadedFile(name=new_filename, content=file.read())

                    # Create a dictionary with the data to update
                    update_data = {
                        'qc_upload': uploaded_file,  # Pass the uploaded file data
                    }

                    serializer = self.get_serializer(obj, data=update_data, partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        total_len += 1
                    else:
                        print(f"Error validating data for code {code}: {serializer.errors}")

                except Document.DoesNotExist:
                    print(f"Object with barcode {code} does not exist.")

            return Response({"message": f"{total_len} QC Files Updated"}, status=status.HTTP_200_OK)
        

def delete_bulk_document(request, **kwargs):
    try:
        # Retrieve document IDs from the request (GET parameter 'document_ids')
        document_ids_param = request.GET.get('document_ids', '')
        document_ids = document_ids_param.split(',') if document_ids_param else []

        # If no document IDs are provided, raise a 404 error
        if not document_ids:
            raise Http404("No document IDs provided")

        # Fetch documents with the given IDs
        documents_to_delete = Document.objects.filter(id__in=document_ids)

        # If no documents match the provided IDs, raise a 404 error
        if not documents_to_delete.exists():
            raise Http404("No documents found for the provided IDs")

        # Delete the matched documents
        deleted_count, _ = documents_to_delete.delete()

        # Return success response
        return JsonResponse({
            'status': 'success',
            'message': f'{deleted_count} document(s) deleted successfully'
        })

    except Exception as e:
        # Handle any other exceptions
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)
        
    
def delete_bulk_barcode(request, **kwargs):
    try:
        # Retrieve document IDs from the request (GET parameter 'document_ids')
        barcode_param = request.GET.get('barcode', '')
        barcode = barcode_param.split(',') if barcode_param else []

        # If no document IDs are provided, raise a 404 error
        if not barcode:
            raise Http404("No document IDs provided")

        # Fetch documents with the given IDs
        documents_to_delete = Document.objects.filter(barcode_number__in=barcode)

        # If no documents match the provided IDs, raise a 404 error
        if not documents_to_delete.exists():
            raise Http404("No documents found for the provided IDs")

        # Delete the matched documents
        deleted_count, _ = documents_to_delete.delete()

        # Return success response
        return JsonResponse({
            'status': 'success',
            'message': f'{deleted_count} document(s) deleted successfully'
        })

    except Exception as e:
        # Handle any other exceptions
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

class FilePathDocumentDownloadURL(generics.GenericAPIView):
    permission_classes = [AllowAny]
    authentication_classes = (TokenAuthentication,)

    def get(self, request, *args, **kwargs):
        action = kwargs.get('action', None)
        barcode_number = request.query_params.get("barcode")  # Access barcode from URL parameters

        try:
            barcode = Document.objects.get(barcode_number=barcode_number)

            if action == 'scan':
                file_path = barcode.scan_upload.url
            elif action == 'rectify':
                file_path = barcode.rectify_upload.url
            elif action == 'digitize':
                file_path = barcode.digitize_upload.url
            elif action == 'qc':
                file_path = barcode.qc_upload.url
            elif action == 'pdf':
                file_path = barcode.pdf_upload.url
            elif action == 'gov_qc':
                file_path = barcode.gov_qc_upload.url
            elif action == 'gov_pdf':
                file_path = barcode.gov_pdf_upload.url
            elif action == 'topology':
                file_path = barcode.toplogy_upload.url
            elif action == 'shape':
                file_path = barcode.shape_upload.url
            else:
                return Response({"message": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)

            absolute_file_path = request.build_absolute_uri(file_path)
            response_data = {
                "file_path": absolute_file_path,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Document.DoesNotExist:
            raise Http404("Document with this barcode number does not exist")
        except Exception as e:
            # Handle unexpected exceptions gracefully
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NewDeleteDocumentAPIView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def delete(self, request, *args, **kwargs):
        try:
            barcode_string = request.query_params.get("barcodes")  # Get barcodes from query params
            print("Received barcodes:", barcode_string)  # Debugging log

            if not barcode_string:
                return Response({"message": "Barcodes are required", "status": False}, status=status.HTTP_400_BAD_REQUEST)

            # Convert the comma-separated string into a list and remove empty spaces
            barcodes = [b.strip() for b in barcode_string.split(",") if b.strip()]

            if not barcodes:
                return Response({"message": "Invalid barcode format", "status": False}, status=status.HTTP_400_BAD_REQUEST)

            # Fetch only existing documents
            documents = Document.objects.filter(barcode_number__in=barcodes)
            print("AAAAAAAAAAAAAAAAAAA",documents)

            if not documents.exists():
                return Response({"message": "No matching records found", "status": False}, status=status.HTTP_404_NOT_FOUND)

            deleted_count = 0  # Track how many records were deleted

            for doc in documents:
                file_fields = [
                    doc.scan_upload,
                    doc.rectify_upload,
                    doc.digitize_upload,
                    doc.qc_upload,
                    doc.pdf_upload,
                    doc.shape_upload,
                    doc.gov_qc_upload,
                    doc.gov_pdf_upload
                ]

                # Delete associated files
                for file_field in file_fields:
                    if file_field and file_field.path and os.path.exists(file_field.path):
                        print(f"Deleting file: {file_field.path}")  # Debugging log
                        file_field.delete(save=False)

                doc.delete()  # Delete the document record
                deleted_count += 1

            return Response({"message": f"{deleted_count} record(s) deleted successfully", "status": True}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"message": str(e), "status": False}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        

class UpdateBarcodeFilenameGenericAPI(APIView):
    permission_classes = [AllowAny]
    authentication_classes = (TokenAuthentication,)


    def get(self, request, *args, **kwargs):
        try:
            barcode = Document.objects.get(barcode_number=kwargs.get('barcode_number'))
            barcode_no = barcode.barcode_number
            file_path = barcode.scan_upload.path
            # Get the original filename from the path
            original_filename = os.path.basename(file_path)

            # Extract the part of the filename before "_R" (assuming "_R" is the marker)
            prefix, extension = os.path.splitext(original_filename)
            
            # Replace the part before "_R" with the barcode
            modified_filename = barcode_no + extension
            Document.objects.filter(barcode_number=barcode_no).update(file_name=modified_filename)

            return Response({"data1":modified_filename,"message": "Success"},status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"data": {"message": str(e)}, "status": status.HTTP_204_NO_CONTENT})
       




    

class MisMatchDigitizeDocument(generics.ListAPIView):
    queryset = Document.objects.all()
    permission_classes = [AllowAny]
    authentication_classes = (TokenAuthentication,)
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

            csv_data = generate_data_csv(csv_header, csv_body, f"report_data_{datetime.now()}_.csv")
            return Response({'csv_path': csv_data.get('csv_path')})

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        queryset = self.queryset


        agency_id = self.kwargs.get('agency')
        agency_users = User.objects.filter(agency=agency_id).values_list('id', flat=True)

        # Get documents where digitize_agency_id is the given agency but digitize_by is NOT in agency_users
        query_set = queryset.filter(digitize_agency_id=agency_id)\
                                            .exclude(digitize_by__in=agency_users)\
                                            .exclude(digitize_by__isnull=True)

        # Serialize the data
    
        return query_set
    
class MisMatchQCDocument(generics.ListAPIView):
    queryset = Document.objects.all()
    permission_classes = [AllowAny]
    authentication_classes = (TokenAuthentication,)
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

            csv_data = generate_data_csv(csv_header, csv_body, f"report_data_{datetime.now()}_.csv")
            return Response({'csv_path': csv_data.get('csv_path')})

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        queryset = self.queryset


        agency_id = self.kwargs.get('agency')
        agency_users = User.objects.filter(agency=agency_id).values_list('id', flat=True)

        # Get documents where digitize_agency_id is the given agency but digitize_by is NOT in agency_users
        query_set = queryset.filter(qc_agency_id=agency_id)\
                                            .exclude(qc_by__in=agency_users)\
                                            .exclude(qc_by__isnull=True)

        # Serialize the data
    
        return query_set

class MisMatchRectifyDocument(generics.ListAPIView):
    queryset = Document.objects.all()
    permission_classes = [AllowAny]
    authentication_classes = (TokenAuthentication,)
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

            csv_data = generate_data_csv(csv_header, csv_body, f"report_data_{datetime.now()}_.csv")
            return Response({'csv_path': csv_data.get('csv_path')})

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        queryset = self.queryset


        agency_id = self.kwargs.get('agency')
        agency_users = User.objects.filter(agency=agency_id).values_list('id', flat=True)

        # Get documents where digitize_agency_id is the given agency but digitize_by is NOT in agency_users
        query_set = queryset.filter(rectify_agency_id=agency_id)\
                                            .exclude(rectify_by__in=agency_users)\
                                            .exclude(rectify_by__isnull=True)

        # Serialize the data
    
        return query_set


class WronghFileName(generics.ListAPIView):
    queryset = Document.objects.all()
    permission_classes = [IsAuthenticated,]
    authentication_classes = (TokenAuthentication,)
    serializer_class = WrongDocumentFileName
    pagination_class = CustomPageNumberPagination
    
  

    def get_queryset(self):
        queryset = self.queryset.order_by('-date_created')

        # Filter documents where barcode_number does NOT match file_name (excluding extension)
        mismatched_docs = [
            doc for doc in queryset
            if doc.file_name and str(doc.barcode_number) != doc.file_name.rsplit('.', 1)[0]
        ]

        return mismatched_docs
    

class DuplicateBarcodeAPIView(generics.ListAPIView):
    queryset = Document.objects.all()
    permission_classes = [IsAuthenticated,]
    authentication_classes = (TokenAuthentication,)
    serializer_class = WrongDocumentFileName
    pagination_class = CustomPageNumberPagination
   
    
    def get_queryset(self):
        queryset = self.queryset.order_by('-date_created')


        duplicate_barcodes = (
            Document.objects.values('barcode_number')
            .annotate(count=Count('id'))
            .filter(count__gt=1)
            .values_list('barcode_number', flat=True)
        )


        return duplicate_barcodes


class TwentyNoBarcodeAPIView(generics.ListAPIView):
    queryset = Document.objects.all()
    permission_classes = [IsAuthenticated,]
    authentication_classes = (TokenAuthentication,)
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

            csv_data = generate_data_csv(csv_header, csv_body, f"report_data_{datetime.now()}_.csv")
            return Response({'csv_path': csv_data.get('csv_path')})

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

   
    
    def get_queryset(self):
        return self.queryset.extra(
            where=["LENGTH(barcode_number) = 20"]
        ).order_by('-date_created')
    


class TwentyTwoNoBarcodeAPIView(generics.ListAPIView):
    queryset = Document.objects.all()
    permission_classes = [IsAuthenticated,]
    authentication_classes = (TokenAuthentication,)
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

            csv_data = generate_data_csv(csv_header, csv_body, f"report_data_{datetime.now()}_.csv")
            return Response({'csv_path': csv_data.get('csv_path')})

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

   
    
    def get_queryset(self):
        return self.queryset.extra(
            where=["LENGTH(barcode_number) = 22"]
        ).order_by('-date_created')
        
###############################################################################

class TippenScanDocumentListView(ListAPIView):
    queryset = TippenDocument.objects.all()
    permission_classes = [IsAuthenticated,]
    authentication_classes = (TokenAuthentication,)
    serializer_class = TippenScanDocumentListSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend,filters.SearchFilter]
    search_fields = []
    filterset_fields = ['taluka_code']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)

        if request.GET.get('is_export') and request.GET.get('is_export') in ['1', 1]:
            for_count = 0
            csv_header = ['Sr.No', 'File Name','District','Taluka','Village','Map Code','Current Status','Remark']
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
                        qs.get('file_name'),
                        district_name,
                        taluka_name,
                        village_name,
                        qs.get('map_code'),
                        qs.get('current_status'),
                        qs.get('tippen_digitize_remarks',''),
                       
                    ]
                )

            csv_data = generate_data_csv(csv_header, csv_body, f"scan_report_{datetime.now()}_.csv")
            return Response({'csv_path': csv_data.get('csv_path')})

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        queryset = self.queryset
        agency_ids = User.objects.filter(id=self.request.user.id).values_list('agency', flat=True)
        if User.objects.filter(id=self.request.user.id, user_role__role_name="Super Admin"):
            query_set = queryset.filter(current_status=36).order_by('-date_created')
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Agency Admin"):
            query_set = queryset.filter(tippen_digitize_agency_id__in=agency_ids,current_status=37).exclude(tippen_digitize_by__isnull=False).order_by('-date_created')
        else:
            current_status_values = [37,39,40]
            query_set = queryset.filter(tippen_digitize_agency_id__in=agency_ids,tippen_digitize_by=self.request.user.id,current_status__in=current_status_values).order_by('-date_created')
        
        village_name = self.request.query_params.get('village_name', None)
        taluka_name = self.request.query_params.get('taluka_name', None)
        district_name = self.request.query_params.get('district_name', None)
        barcode_number = self.request.query_params.get('barcode_number', None)
        file_name = self.request.query_params.get('file_name', None)
        district_code = self.request.query_params.get('district_code', None)
        village_code = self.request.query_params.get('village_code', None)
        map_code = self.request.query_params.get('map_code', None)
        current_status = self.request.query_params.get('current_status', None)
        
        
       
        
        if village_name:
            village_names = Village.objects.filter(village_name__icontains=village_name).values_list('village_code',flat=True)
            query_set = query_set.filter(village_code__in=village_names)
            

        if taluka_name:
            taluka_names = Taluka.objects.filter(taluka_name__icontains=taluka_name).values_list('taluka_code',flat=True)
            query_set = query_set.filter(taluka_code__in=taluka_names)


        if district_name:
            district_names = District.objects.filter(district_name__icontains=district_name).values_list('district_code',flat=True)
            query_set = query_set.filter(district_code__in=district_names)
        
        if barcode_number:
            query_set = query_set.filter(barcode_number__icontains=barcode_number)
        
        if file_name:
            query_set = query_set.filter(file_name__icontains=file_name)
            
        if district_code:
            query_set = query_set.filter(district_code__icontains=district_code)
        
        if village_code:
            query_set = query_set.filter(village_code__icontains=village_code)
       
        if map_code:
            query_set = query_set.filter(map_code__icontains=map_code)

        
        
        if current_status:
            query_set = query_set.filter(current_status__status__icontains=current_status)
        

        return query_set
        
class TippenScanUploadDocumentView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)
    serializer_class = UploadTippenScanDocumentSerializer
    # Use the custom serializer

    def post(self, request, *args, **kwargs):
        data = request.FILES.getlist('files')
        total_len = 0
        validation_errors = []
        uploaded_files = [] 
        allowed_extensions = ['.JPG','.JPEG','.jpeg','.jpg']  ###
    
        for file in data:
            filename = file.name
            base_filename,file_extension = os.path.splitext(filename)

          
            if file_extension.lower() not in allowed_extensions:  ###
                print(f"Skipping file {filename}: Only .JPEG files are allowed.")  ###
                continue                                                           ###
            code = base_filename.split("_")[0]

            try:
                # Create a SimpleUploadedFile with the file data
                new_filename = f"{base_filename}{file_extension}"
                uploaded_file = SimpleUploadedFile(name=new_filename, content=file.read())
                district_code = base_filename[:3]
                taluka_code = base_filename[3:7]
                village_code = base_filename[7:13]
                maptype_code = base_filename[13:15]

                try:
                    # Get the district name from the District model
                    district = District.objects.get(district_code=district_code)
                    taluka = Taluka.objects.get(taluka_code=taluka_code)
                    village = Village.objects.get(village_code=village_code)
                    maptype = MapType.objects.get(map_code=maptype_code)
                    status_code = 36
                except Exception:
                    status_code = 28


                # Create a dictionary with the data to update
                scan_upload_by = self.request.user.id
                completed_date =datetime.now()
                update_data = {
                    'tippen_scan_upload': uploaded_file,  # Pass the uploaded file data
                    "tippen_uploaded_by":scan_upload_by,
                    "tippen_uploaded_date":completed_date,
                    "current_status":status_code
                }

                serializer = self.get_serializer(data=update_data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    uploaded_files.append(new_filename)  # Add the uploaded file name to the list
                    total_len += 1
                else:
                    validation_errors.extend(serializer.errors.get('scan_upload', []))


            except Document.DoesNotExist:
                print(f"Object with barcode {code} does not exist.")
        if validation_errors:
            return Response({"message": f"{total_len} Tippen Scan Files Uploaded","Uploaded Files": uploaded_files, "errors": validation_errors}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": f"{total_len} Tippen Scan Files Uploaded","Uploaded Files": uploaded_files,}, status=status.HTTP_200_OK)
    
class UpdateTippenDigitizeFileCreateView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)
    serializer_class = TippenUploadDocumentSerializer  # Use the custom serializer

    def put(self, request, *args, **kwargs):
        # Extract the action from the URL
        action = kwargs.get('action', None)

        if action == 'approved':
            data = request.FILES.getlist('files')
            total_len = 0

            for file in data:
                filename = file.name
                base_filename,file_extension = os.path.splitext(filename)
                code = base_filename.split("_")[0]

                try:
                    # Get the existing object based on the barcode
                    obj = TippenDocument.objects.get(barcode_number=code,tippen_uploaded_date__isnull=False,current_status__in=[37,39,40])
                    new_filename = f"{base_filename}{file_extension}"


                    # Create a SimpleUploadedFile with the file data
                    uploaded_file = SimpleUploadedFile(name=new_filename, content=file.read())

                    # Create a dictionary with the data to update
                    tippen_digitize_by = self.request.user.id
                    tippen_digitize_agency_id = self.request.user.agency.id
                    agency_team_id = self.request.user.agency.team.id
                    completed_date = datetime.now()
                    # Check if digitize_agency_id is present
                    
                   

                    update_data = {
                        'tippen_digitize_agency_id':tippen_digitize_agency_id,
                        'team_id':agency_team_id,
                        'tippen_digitize_upload': uploaded_file,  # Pass the uploaded file data
                        "tippen_digitize_by": tippen_digitize_by,
                        "tippen_digitize_completed_date": completed_date,
                        "current_status": 38
                    }

                    serializer = self.get_serializer(obj, data=update_data, partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        total_len += 1
                    else:
                        print(f"Error validating data for code {code}: {serializer.errors}")

                except Document.DoesNotExist:
                    print(f"Object with barcode {code} does not exist.")

            return Response({"message": f"{total_len} Tippen Digitize Files Updated"}, status=status.HTTP_200_OK)

        elif action == 'rejected':
            data = request.data

            # Assuming you send a list of dictionaries with update data
            update_data_list = data

            for update_data in update_data_list:
                document_id = update_data.get("id")
                try:
                    rectify_obj = TippenDocument.objects.get(id=document_id)
                except Document.DoesNotExist:
                    return Response({"msg": f"Record with ID {document_id} does not exist"})

                # Update the fields specified in the dictionary
                serializer = TippenUploadDocumentSerializer(rectify_obj, data=update_data, partial=True)
                if serializer.is_valid():
                    serializer.save(current_status=DocumentStatus.objects.get(id=38))
        
            return Response({"message": "Tippen Digitize Files Rejected"})
            # Handle 'rejected' action here
            # Update current_status to 1 for the appropriate documents
            # Add your code for the 'rejected' action here

        else:
            return Response({"message": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)
        
        
class UpdateTippenQCFileCreateView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)
    serializer_class = TippenUploadDocumentSerializer  # Use the custom serializer

    def put(self, request, *args, **kwargs):
        # Extract the action from the URL
        action = kwargs.get('action', None)

        if action == 'approved':
            data = request.FILES.getlist('files')
            tippen_polygon_count = request.data.get("polygon_count")
            tippen_qc_remarks = request.data.get("tippen_qc_remarks")
            
            total_len = 0
            errors = []

            for file in data:
                filename = file.name
                base_filename,file_extension = os.path.splitext(filename)
                code = base_filename.split("_")[0]

                
                try:
                    # Get the existing object based on the barcode
                    obj = TippenDocument.objects.get(barcode_number=code,tippen_digitize_completed_date__isnull=False,current_status__in=[41,43,44])
                    # new_filename = f"{base_filename}{file_extension}"
                    if file_extension.lower() == ".pdf":
                        new_filename = f"{base_filename}{file_extension}"

                    # Create a SimpleUploadedFile with the file data
                    tippen_qc_upload = SimpleUploadedFile(name=new_filename, content=file.read())

                    # Create a dictionary with the data to update
                    tippen_qc_by = self.request.user.id
                    tippen_qc_agency_id = self.request.user.agency.id
                    completed_date = datetime.now()

                  

                    if file_extension.lower() == ".pdf":
                        update_data = {
                            'tippen_qc_agency_id':tippen_qc_agency_id,
                            'tippen_qc_upload': tippen_qc_upload,  # Pass the uploaded file data
                            "tippen_qc_by": tippen_qc_by,
                            "tippen_polygon_count":tippen_polygon_count,
                            "tippen_qc_remarks":tippen_qc_remarks,
                            "tippen_qc_completed_date": completed_date,
                            "current_status": 42
                        }

                    serializer = self.get_serializer(obj, data=update_data, partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        total_len += 1
                    else:
                        errors.append(f"Error validating data for code {code}: {serializer.errors}")

                except Document.DoesNotExist:
                    errors.append(f"Object with barcode {code} does not exist.")

            if total_len == 0:
                return Response({"message": "Digitize Polygon Count Is Not Updated"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"message": f"{total_len} Tippen Gov Qc Files Updated"}, status=status.HTTP_200_OK)
            
        elif action == 'rejected':
            data = request.data

            # Assuming you send a list of dictionaries with update data
            update_data_list = data

            for update_data in update_data_list:
                document_id = update_data.get("id")
                tippen_remarks = update_data.get("tippen_remarks")

                if not tippen_remarks or not str(tippen_remarks).strip():
                    return Response(
                        {"message": f"Tippen Gov Qc  remarks are required for rejecting."},
                        status=status.HTTP_200_OK
                    )

                try:
                    rectify_obj = Document.objects.get(id=document_id)
                except Document.DoesNotExist:
                    return Response({"msg": f"Record with ID {document_id} does not exist"})

                # Update the fields specified in the dictionary
                serializer = UploadDocumentSerializer(rectify_obj, data=update_data, partial=True)
                if serializer.is_valid():
                    serializer.save(current_status=DocumentStatus.objects.get(id=42))
        
            return Response({"message": "Digitize Files Rejected"})
            # Handle 'rejected' action here
            # Update current_status to 1 for the appropriate documents
            # Add your code for the 'rejected' action here

        else:
            return Response({"message": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)

class UpdateTippenGovQCFileCreateView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)
    serializer_class = TippenUploadDocumentSerializer  # Use the custom serializer

    def put(self, request, *args, **kwargs):
        # Extract the action from the URL
        action = kwargs.get('action', None)

        if action == 'approved':
            data = request.FILES.getlist('files')
            tippen_polygon_count = request.data.get("polygon_count")
            tippen_gov_qc_remarks = request.data.get("tippen_gov_qc_remarks")
            
            total_len = 0
            errors = []

            for file in data:
                filename = file.name
                base_filename,file_extension = os.path.splitext(filename)
                code = base_filename.split("_")[0]

                
                try:
                    # Get the existing object based on the barcode
                    obj = TippenDocument.objects.get(barcode_number=code,tippen_gov_qc_completed_date__isnull=False,current_status__in=[45,47,48])
                    # new_filename = f"{base_filename}{file_extension}"
                    if file_extension.lower() == ".pdf":
                        new_filename = f"{base_filename}{file_extension}"

                    # Create a SimpleUploadedFile with the file data
                    tippen_gov_qc_upload = SimpleUploadedFile(name=new_filename, content=file.read())

                    # Create a dictionary with the data to update
                    tippen_gov_qc_by = self.request.user.id
                    tippen_gov_qc_agency_id = self.request.user.agency.id
                    completed_date = datetime.now()

                  

                    if file_extension.lower() == ".pdf":
                        update_data = {
                            'tippen_gov_qc_agency_id':tippen_gov_qc_agency_id,
                            'tippen_gov_qc_upload': tippen_gov_qc_upload,  # Pass the uploaded file data
                            "tippen_gov_qc_by": tippen_gov_qc_by,
                            "tippen_gov_qc_remarks":tippen_gov_qc_remarks,
                            "tippen_gov_qc_completed_date": completed_date,
                            "current_status": 46
                        }

                    serializer = self.get_serializer(obj, data=update_data, partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        total_len += 1
                    else:
                        errors.append(f"Error validating data for code {code}: {serializer.errors}")

                except Document.DoesNotExist:
                    errors.append(f"Object with barcode {code} does not exist.")

            if total_len == 0:
                return Response({"message": "Digitize Polygon Count Is Not Updated"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"message": f"{total_len} Tippen Gov Qc Files Updated"}, status=status.HTTP_200_OK)
            
        elif action == 'rejected':
            data = request.data

            # Assuming you send a list of dictionaries with update data
            update_data_list = data

            for update_data in update_data_list:
                document_id = update_data.get("id")
                tippen_remarks = update_data.get("tippen_remarks")

                if not tippen_remarks or not str(tippen_remarks).strip():
                    return Response(
                        {"message": f"Tippen Gov Qc  remarks are required for rejecting."},
                        status=status.HTTP_200_OK
                    )

                try:
                    rectify_obj = Document.objects.get(id=document_id)
                except Document.DoesNotExist:
                    return Response({"msg": f"Record with ID {document_id} does not exist"})

                # Update the fields specified in the dictionary
                serializer = UploadDocumentSerializer(rectify_obj, data=update_data, partial=True)
                if serializer.is_valid():
                    serializer.save(current_status=DocumentStatus.objects.get(id=42))
        
            return Response({"message": "Digitize Files Rejected"})
            # Handle 'rejected' action here
            # Update current_status to 1 for the appropriate documents
            # Add your code for the 'rejected' action here

        else:
            return Response({"message": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)

class TippenDigitizeDocumentListView(ListAPIView):
    queryset = TippenDocument.objects.all()
    permission_classes = [IsAuthenticated,]
    authentication_classes = (TokenAuthentication,)
    serializer_class = TippenScanDocumentListSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend,filters.SearchFilter]
    search_fields = []
    filterset_fields = ['taluka_code']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)

        if request.GET.get('is_export') and request.GET.get('is_export') in ['1', 1]:
            for_count = 0
            csv_header = ['Sr.No', 'File Name','District','Taluka','Village','Map Code','Current Status','Remark']
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
                        qs.get('file_name'),
                        district_name,
                        taluka_name,
                        village_name,
                        qs.get('map_code'),
                        qs.get('current_status'),
                        qs.get('tippen_remarks',''),
                       
                    ]
                )

            csv_data = generate_data_csv(csv_header, csv_body, f"scan_report_{datetime.now()}_.csv")
            return Response({'csv_path': csv_data.get('csv_path')})

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        queryset = self.queryset
        agency_ids = User.objects.filter(id=self.request.user.id).values_list('agency', flat=True)
        if User.objects.filter(id=self.request.user.id, user_role__role_name="Super Admin"):
            query_set = queryset.filter(current_status=38).order_by('-date_created')
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Agency Admin"):
            query_set = queryset.filter(tippen_qc_agency_id_id__in=agency_ids,current_status=41).exclude(tippen_qc_by__isnull=False).order_by('-date_created')
        else:
            current_status_values = [41,43,44]
            query_set = queryset.filter(tippen_qc_agency_id__in=agency_ids,tippen_qc_by=self.request.user.id,current_status__in=current_status_values).order_by('-date_created')
        
        village_name = self.request.query_params.get('village_name', None)
        taluka_name = self.request.query_params.get('taluka_name', None)
        district_name = self.request.query_params.get('district_name', None)
        barcode_number = self.request.query_params.get('barcode_number', None)
        file_name = self.request.query_params.get('file_name', None)
        district_code = self.request.query_params.get('district_code', None)
        village_code = self.request.query_params.get('village_code', None)
        map_code = self.request.query_params.get('map_code', None)
        current_status = self.request.query_params.get('current_status', None)
        
        
       
        
        if village_name:
            village_names = Village.objects.filter(village_name__icontains=village_name).values_list('village_code',flat=True)
            query_set = query_set.filter(village_code__in=village_names)
            

        if taluka_name:
            taluka_names = Taluka.objects.filter(taluka_name__icontains=taluka_name).values_list('taluka_code',flat=True)
            query_set = query_set.filter(taluka_code__in=taluka_names)


        if district_name:
            district_names = District.objects.filter(district_name__icontains=district_name).values_list('district_code',flat=True)
            query_set = query_set.filter(district_code__in=district_names)
        
        if barcode_number:
            query_set = query_set.filter(barcode_number__icontains=barcode_number)
        
        if file_name:
            query_set = query_set.filter(file_name__icontains=file_name)
            
        if district_code:
            query_set = query_set.filter(district_code__icontains=district_code)
        
        if village_code:
            query_set = query_set.filter(village_code__icontains=village_code)
       
        if map_code:
            query_set = query_set.filter(map_code__icontains=map_code)

        
        
        if current_status:
            query_set = query_set.filter(current_status__status__icontains=current_status)
        

        return query_set
    

class TippenQCDocumentListView(ListAPIView):
    queryset = TippenDocument.objects.all()
    permission_classes = [IsAuthenticated,]
    authentication_classes = (TokenAuthentication,)
    serializer_class = TippenScanDocumentListSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend,filters.SearchFilter]
    search_fields = []
    filterset_fields = ['taluka_code']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)

        if request.GET.get('is_export') and request.GET.get('is_export') in ['1', 1]:
            for_count = 0
            csv_header = ['Sr.No', 'File Name','District','Taluka','Village','Map Code','Current Status','Remark']
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
                        qs.get('file_name'),
                        district_name,
                        taluka_name,
                        village_name,
                        qs.get('map_code'),
                        qs.get('current_status'),
                        qs.get('tippen_remarks',''),
                       
                    ]
                )

            csv_data = generate_data_csv(csv_header, csv_body, f"scan_report_{datetime.now()}_.csv")
            return Response({'csv_path': csv_data.get('csv_path')})

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        queryset = self.queryset
        agency_ids = User.objects.filter(id=self.request.user.id).values_list('agency', flat=True)
        if User.objects.filter(id=self.request.user.id, user_role__role_name="Super Admin"):
            query_set = queryset.filter(current_status=38).order_by('-date_created')
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Agency Admin"):
            query_set = queryset.filter(tippen_qc_agency_id__in=agency_ids,current_status=41).exclude(tippen_qc_by__isnull=False).order_by('-date_created')
        else:
            current_status_values = [41,43,44]
            query_set = queryset.filter(tippen_qc_agency_id__in=agency_ids,tippen_qc_by=self.request.user.id,current_status__in=current_status_values).order_by('-date_created')
        
        village_name = self.request.query_params.get('village_name', None)
        taluka_name = self.request.query_params.get('taluka_name', None)
        district_name = self.request.query_params.get('district_name', None)
        barcode_number = self.request.query_params.get('barcode_number', None)
        file_name = self.request.query_params.get('file_name', None)
        district_code = self.request.query_params.get('district_code', None)
        village_code = self.request.query_params.get('village_code', None)
        map_code = self.request.query_params.get('map_code', None)
        current_status = self.request.query_params.get('current_status', None)
        
        
       
        
        if village_name:
            village_names = Village.objects.filter(village_name__icontains=village_name).values_list('village_code',flat=True)
            query_set = query_set.filter(village_code__in=village_names)
            

        if taluka_name:
            taluka_names = Taluka.objects.filter(taluka_name__icontains=taluka_name).values_list('taluka_code',flat=True)
            query_set = query_set.filter(taluka_code__in=taluka_names)


        if district_name:
            district_names = District.objects.filter(district_name__icontains=district_name).values_list('district_code',flat=True)
            query_set = query_set.filter(district_code__in=district_names)
        
        if barcode_number:
            query_set = query_set.filter(barcode_number__icontains=barcode_number)
        
        if file_name:
            query_set = query_set.filter(file_name__icontains=file_name)
            
        if district_code:
            query_set = query_set.filter(district_code__icontains=district_code)
        
        if village_code:
            query_set = query_set.filter(village_code__icontains=village_code)
       
        if map_code:
            query_set = query_set.filter(map_code__icontains=map_code)

        
        
        if current_status:
            query_set = query_set.filter(current_status__status__icontains=current_status)
        

        return query_set
    
class TippenGovQCDocumentListView(ListAPIView):
    queryset = TippenDocument.objects.all()
    permission_classes = [IsAuthenticated,]
    authentication_classes = (TokenAuthentication,)
    serializer_class = TippenScanDocumentListSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend,filters.SearchFilter]
    search_fields = []
    filterset_fields = ['taluka_code']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)

        if request.GET.get('is_export') and request.GET.get('is_export') in ['1', 1]:
            for_count = 0
            csv_header = ['Sr.No', 'File Name','District','Taluka','Village','Map Code','Current Status','Remark']
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
                        qs.get('file_name'),
                        district_name,
                        taluka_name,
                        village_name,
                        qs.get('map_code'),
                        qs.get('current_status'),
                        qs.get('tippen_remarks',''),
                       
                    ]
                )

            csv_data = generate_data_csv(csv_header, csv_body, f"scan_report_{datetime.now()}_.csv")
            return Response({'csv_path': csv_data.get('csv_path')})

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        queryset = self.queryset
        agency_ids = User.objects.filter(id=self.request.user.id).values_list('agency', flat=True)
        if User.objects.filter(id=self.request.user.id, user_role__role_name="Super Admin"):
            query_set = queryset.filter(current_status=42).order_by('-date_created')
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Agency Admin"):
            query_set = queryset.filter(tippen_gov_qc_agency_id__in=agency_ids,current_status=45).exclude(tippen_gov_qc_by__isnull=False).order_by('-date_created')
        else:
            current_status_values = [45,47,48]
            query_set = queryset.filter(tippen_gov_qc_agency_id_in=agency_ids,tippen_gov_qc_by=self.request.user.id,current_status__in=current_status_values).order_by('-date_created')
        
        village_name = self.request.query_params.get('village_name', None)
        taluka_name = self.request.query_params.get('taluka_name', None)
        district_name = self.request.query_params.get('district_name', None)
        barcode_number = self.request.query_params.get('barcode_number', None)
        file_name = self.request.query_params.get('file_name', None)
        district_code = self.request.query_params.get('district_code', None)
        village_code = self.request.query_params.get('village_code', None)
        map_code = self.request.query_params.get('map_code', None)
        current_status = self.request.query_params.get('current_status', None)
        
        
       
        
        if village_name:
            village_names = Village.objects.filter(village_name__icontains=village_name).values_list('village_code',flat=True)
            query_set = query_set.filter(village_code__in=village_names)
            

        if taluka_name:
            taluka_names = Taluka.objects.filter(taluka_name__icontains=taluka_name).values_list('taluka_code',flat=True)
            query_set = query_set.filter(taluka_code__in=taluka_names)


        if district_name:
            district_names = District.objects.filter(district_name__icontains=district_name).values_list('district_code',flat=True)
            query_set = query_set.filter(district_code__in=district_names)
        
        if barcode_number:
            query_set = query_set.filter(barcode_number__icontains=barcode_number)
        
        if file_name:
            query_set = query_set.filter(file_name__icontains=file_name)
            
        if district_code:
            query_set = query_set.filter(district_code__icontains=district_code)
        
        if village_code:
            query_set = query_set.filter(village_code__icontains=village_code)
       
        if map_code:
            query_set = query_set.filter(map_code__icontains=map_code)

        
        
        if current_status:
            query_set = query_set.filter(current_status__status__icontains=current_status)
        

        return query_set

class TippenDigitizeAssignToAgencyUserView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)
    serializer_class = TippenUploadDocumentSerializer  # Use the custom serializer

    def put(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id')
        user_agency = User.objects.filter(id=user_id).values_list('agency', flat=True).first()
       

        try:
            user_id = get_object_or_404(User, id=user_id)
        except Http404:
            return Response({"message": f"Agency with ID {user_id} does not exist"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.get('document_id', [])
        total_len = 0

        for file in data:
            assign_date =datetime.now()
            documentz_agency= TippenDocument.objects.filter(id=file).values_list('tippen_digitize_agency_id', flat=True).first()
            if documentz_agency == user_agency:
                created_input_file = TippenDocument.objects.filter(id=file,tippen_digitize_by__isnull=True).update(tippen_digitize_by=user_id,tippen_digitize_assign_date=assign_date)
                if created_input_file > 0:
                    total_len += 1
            else:
                return Response({"message": "You do not have permission to assign documents to this user."}, status=status.HTTP_403_FORBIDDEN)


        return Response({"message": f"{total_len} Tippen Digitize Document Assign To User"}, status=status.HTTP_201_CREATED)
    



class TippenQCAssignToAgencyUserView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)
    serializer_class = TippenUploadDocumentSerializer  # Use the custom serializer

    def put(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id')
        user_agency = User.objects.filter(id=user_id).values_list('agency', flat=True).first()
       

        try:
            user_id = get_object_or_404(User, id=user_id)
        except Http404:
            return Response({"message": f"Agency with ID {user_id} does not exist"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.get('document_id', [])
        total_len = 0

        for file in data:
            assign_date =datetime.now()
            documentz_agency= TippenDocument.objects.filter(id=file).values_list('tippen_qc_agency_id', flat=True).first()
            if documentz_agency == user_agency:
                created_input_file = TippenDocument.objects.filter(id=file,tippen_qc_by__isnull=True).update(tippen_qc_by=user_id,tippen_qc_assign_date=assign_date)
                if created_input_file > 0:
                    total_len += 1
            else:
                return Response({"message": "You do not have permission to assign documents to this user."}, status=status.HTTP_403_FORBIDDEN)


        return Response({"message": f"{total_len} Tippen Gov QC Document Assign To User"}, status=status.HTTP_201_CREATED)
    
class TippenGovQCAssignToAgencyUserView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)
    serializer_class = TippenUploadDocumentSerializer  # Use the custom serializer

    def put(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id')
        user_agency = User.objects.filter(id=user_id).values_list('agency', flat=True).first()
       

        try:
            user_id = get_object_or_404(User, id=user_id)
        except Http404:
            return Response({"message": f"Agency with ID {user_id} does not exist"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.get('document_id', [])
        total_len = 0

        for file in data:
            assign_date =datetime.now()
            documentz_agency= TippenDocument.objects.filter(id=file).values_list('tippen_gov_qc_agency_id', flat=True).first()
            if documentz_agency == user_agency:
                created_input_file = TippenDocument.objects.filter(id=file,tippen_gov_qc_by__isnull=True).update(tippen_gov_qc_by=user_id,tippen_gov_qc_assign_date=assign_date)
                if created_input_file > 0:
                    total_len += 1
            else:
                return Response({"message": "You do not have permission to assign documents to this user."}, status=status.HTTP_403_FORBIDDEN)


        return Response({"message": f"{total_len} Tippen Gov QC Document Assign To User"}, status=status.HTTP_201_CREATED)

class TippenDigitizeAssignToAgencyView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)
    serializer_class = TippenUploadDocumentSerializer  # Use the custom serializer

    def put(self, request, *args, **kwargs):
        agency_id = kwargs.get('agency_id')
        try:
            agency_id = get_object_or_404(Agency, id=agency_id)
        except Http404:
            return Response({"message": f"Agency with ID {agency_id} does not exist"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.get('document_id', [])
        total_len = 0

        for file in data:
            assign_date =datetime.now()
            created_input_file = TippenDocument.objects.filter(id=file,tippen_digitize_agency_id__isnull=True).update(tippen_digitize_agency_id=agency_id,tippen_digitize_assign_date=assign_date,current_status=37)
            if created_input_file > 0:
                total_len += 1
        return Response({"message": f"{total_len} Tippen Digitize Document Assign To Agency"}, status=status.HTTP_201_CREATED)


class TippenQCAssignToAgencyView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)
    serializer_class = TippenUploadDocumentSerializer  # Use the custom serializer

    def put(self, request, *args, **kwargs):
        agency_id = kwargs.get('agency_id')
        try:
            agency_id = get_object_or_404(Agency, id=agency_id)
        except Http404:
            return Response({"message": f"Agency with ID {agency_id} does not exist"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.get('document_id', [])
        total_len = 0

        for file in data:
            assign_date =datetime.now()
            created_input_file = TippenDocument.objects.filter(id=file,tippen_qc_agency_id__isnull=True).update(tippen_qc_agency_id=agency_id,tippen_qc_assign_date=assign_date,current_status=41)
            if created_input_file > 0:
                total_len += 1
        return Response({"message": f"{total_len} Tippen Digitize Document Assign To Agency"}, status=status.HTTP_201_CREATED)

class TippenGovQCAssignToAgencyView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)
    serializer_class = TippenUploadDocumentSerializer  # Use the custom serializer

    def put(self, request, *args, **kwargs):
        agency_id = kwargs.get('agency_id')
        try:
            agency_id = get_object_or_404(Agency, id=agency_id)
        except Http404:
            return Response({"message": f"Agency with ID {agency_id} does not exist"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.get('document_id', [])
        total_len = 0

        for file in data:
            assign_date =datetime.now()
            created_input_file = TippenDocument.objects.filter(id=file,tippen_gov_qc_agency_id__isnull=True).update(tippen_gov_qc_agency_id=agency_id,tippen_gov_qc_assign_date=assign_date,current_status=45)
            if created_input_file > 0:
                total_len += 1
        return Response({"message": f"{total_len} Tippen Digitize Document Assign To Agency"}, status=status.HTTP_201_CREATED)
    
def tippen_scan_download_file(request, document_id):
    try:
        download_file = get_object_or_404(TippenDocument, id=document_id)
        file_path = download_file.tippen_scan_upload.path
        content_type, _ = guess_type(file_path)

        with open(file_path, 'rb') as file:
            response = HttpResponse(file.read(), content_type=content_type)
            
            # Get the original filename from the path
            barcode = download_file.barcode_number
            original_filename = os.path.basename(file_path)
            prefix, extension = os.path.splitext(original_filename)#
            modified_filename = barcode + extension
            # Set the Content-Disposition header with the original filename
            response['Content-Disposition'] = f'attachment; filename="{quote(modified_filename)}"'

            # Update the status here if needed
            # update_status = Document.objects.filter(id=download_file.id).update(current_status=9)
            
            return response
    except Document.DoesNotExist:
        raise Http404("Document does not exist")
    except Exception:
        return HttpResponse('Tippen Scan Document File Does Not Exist', status=404)
    

class TippenAllDocumentListView(generics.ListAPIView):
    queryset = TippenDocument.objects.all()
    permission_classes = [IsAuthenticated,]
    authentication_classes = (TokenAuthentication,)
    serializer_class = AllTippenScanDocumentListSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend,filters.SearchFilter]
    filterset_fields = ['map_code','district_code','village_code','taluka_code']
    

    def get_queryset(self):
        queryset = self.queryset

        if User.objects.filter(id=self.request.user.id, user_role__role_name="Super Admin"):
            query_set = queryset.all().order_by('-date_created')
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Agency Admin"):
            agency_ids = User.objects.filter(id=self.request.user.id).values_list('agency', flat=True)
            agency_filters = Q(tippen_digitize_agency_id__in=agency_ids) | Q(tippen_qc_agency_id__in=agency_ids)
            query_set = queryset.filter(agency_filters).order_by('-date_created')
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="District Admin"):
            team_district_code = DistrictTalukaAdmin.objects.filter(user_id=self.request.user.id).values_list('district_id__district_code', flat=True)
            query_set = queryset.filter(district_code__in=team_district_code).order_by('-date_created')
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Taluka Admin"):
            query_set = queryset.filter(scan_uploaded_by=self.request.user.id).order_by('-date_created')
        else:
            query_set = queryset.none()  # Return an empty queryset for other roles
        
        file_name = self.request.query_params.get('file_name', None)
        barcode_number = self.request.query_params.get('barcode_number', None)
        village_name = self.request.query_params.get('village_name', None)
        taluka_name = self.request.query_params.get('taluka_name', None)
        district_name = self.request.query_params.get('district_name', None)
        current_status = self.request.query_params.get('current_status', None)
       

    
        if file_name:
            query_set = query_set.filter(file_name__icontains=file_name)
    

        if barcode_number:
            query_set = query_set.filter(barcode_number__icontains=barcode_number)
       
            
        if village_name:
            village_names = Village.objects.filter(village_name__icontains=village_name).values_list('village_code',flat=True)
            query_set = query_set.filter(village_code__in=village_names)
            

        if taluka_name:
            taluka_names = Taluka.objects.filter(taluka_name__icontains=taluka_name).values_list('taluka_code',flat=True)
            query_set = query_set.filter(taluka_code__in=taluka_names)


        if district_name:
            district_names = District.objects.filter(district_name__icontains=district_name).values_list('district_code',flat=True)
            query_set = query_set.filter(district_code__in=district_names)
        
        
        if current_status:
            query_set = query_set.filter(current_status__status__icontains=current_status)
            
        return query_set
    

class UpdateBackeupFileCreateView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)
    serializer_class = TippenUploadDocumentSerializer  # Use the custom serializer

    def put(self, request, *args, **kwargs):
        # Extract the action from the URL
        action = kwargs.get('action', None)

        if action == 'approved':
            data = request.FILES.getlist('files')
            total_len = 0

            for file in data:
                filename = file.name
                base_filename,file_extension = os.path.splitext(filename)

                if file_extension.lower() != ".zip":
                    print(f"Skipping file {filename}: Only .zip files are allowed.")
                    continue

                code = base_filename.split("_")[0]

                try:
                    obj = TippenDocument.objects.get(barcode_number=code,current_status__in=[40])
                    new_filename = f"{base_filename}{file_extension}"

                   
                    uploaded_file = SimpleUploadedFile(name=new_filename, content=file.read())

                    shape_obj = self.request.user.id
                    completed_date = datetime.now()
                    update_data = {
                        "backup_file_upload": uploaded_file,
                        "tippen_digitize_by":shape_obj,
                        "tippen_digitize_completed_date":completed_date,
                        "current_status":40
                    }   

                    serializer = self.get_serializer(obj, data=update_data, partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        total_len += 1
                    else:
                        print(f"Error validating data for code {code}: {serializer.errors}")

                except Document.DoesNotExist:
                    print(f"Object with barcode {code} does not exist.")

            return Response({"message": f"{total_len} Shape Files Updated"}, status=status.HTTP_200_OK)

        else:
            return Response({"message": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)