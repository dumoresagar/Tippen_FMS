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
from core.models import Document,DocumentStatus,PaginationMaster,MapType
from datetime import datetime,timedelta
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
        team_ids = User.objects.filter(id=self.request.user.id).values_list('agency__team', flat=True)
        if User.objects.filter(id=self.request.user.id, user_role__role_name="Super Admin"):
            query_set = queryset.filter(current_status=1).order_by('-date_created')
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Team Admin"):
            query_set = queryset.filter(team_id__in=team_ids,current_status=1).order_by('-date_created')
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Agency Admin"):
            query_set = queryset.filter(rectify_agency_id__in=agency_ids,current_status=3).exclude(rectify_by__isnull=False).order_by('-date_created')
        else:
            current_status_values = [3, 4, 7,11]
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
        scan_start_date = self.request.query_params.get('scan_start_date',None)
        scan_end_date = self.request.query_params.get('scan_end_date',None)
        scan_by_username = self.request.query_params.get('scan_by_username', None)
        rectify_by_username = self.request.query_params.get('rectify_by_username', None)
        digitize_by_username = self.request.query_params.get('digitize_by_username', None)
        qc_by_username = self.request.query_params.get('qc_by_username', None)
        pdf_by_username = self.request.query_params.get('pdf_by_username', None)
        shape_by_username = self.request.query_params.get('shape_by_username', None)

        
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
        team_ids = User.objects.filter(id=self.request.user.id).values_list('agency__team', flat=True)
        if User.objects.filter(id=self.request.user.id, user_role__role_name="Super Admin"):
            query_set = queryset.filter(current_status=5,digitize_agency_id__isnull=True).order_by('-date_created')
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Team Admin"):
            current_status_values = [8]
            query_set = queryset.filter(team_id__in=team_ids,current_status__in=current_status_values).order_by('-date_created')
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Agency Admin"):
            current_status_values = [5,8]
            query_set = queryset.filter(digitize_agency_id__in=agency_ids,current_status__in=current_status_values).exclude(digitize_by__isnull=False).order_by('-date_created')
        else:
            current_status_values = [8,9,12,16]
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
        rectify_start_date = self.request.query_params.get('rectify_start_date',None)
        rectify_end_date = self.request.query_params.get('rectify_end_date',None)
        scan_by_username = self.request.query_params.get('scan_by_username', None)
        rectify_by_username = self.request.query_params.get('rectify_by_username', None)
        digitize_by_username = self.request.query_params.get('digitize_by_username', None)
        qc_by_username = self.request.query_params.get('qc_by_username', None)
        pdf_by_username = self.request.query_params.get('pdf_by_username', None)
        shape_by_username = self.request.query_params.get('shape_by_username', None)

        
        if rectify_start_date and rectify_end_date:
            rectify_start_date = datetime.strptime(rectify_start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
            rectify_end_date = datetime.strptime(rectify_end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query_set = query_set.filter(
                        rectify_completed_date__gte=rectify_start_date.date(),
                        rectify_completed_date__lt=(rectify_end_date.date() + timedelta(days=1)))
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
    
        for file in data:
            filename = file.name
            base_filename,file_extension = os.path.splitext(filename)
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
                if self.request.user.agency and self.request.user.agency.team:
                    team_id = self.request.user.agency.team.id
                else:
                    team_id = ""
                completed_date =datetime.now()
                update_data = {
                    "team_id": team_id,
                    'scan_upload': uploaded_file,  # Pass the uploaded file data
                    "scan_uploaded_by":scan_upload_by,
                    "scan_uploaded_date":completed_date,
                    "current_status":status_code
                }

                serializer = self.get_serializer(data=update_data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    total_len += 1
                else:
                    validation_errors.extend(serializer.errors.get('scan_upload', []))


            except Document.DoesNotExist:
                print(f"Object with barcode {code} does not exist.")
        if validation_errors:
            return Response({"message": f"{total_len} Scan Files Uploaded", "errors": validation_errors}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": f"{total_len} Scan Files Uploaded"}, status=status.HTTP_200_OK)
    

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
                created_input_file = Document.objects.filter(id=file).update(rectify_agency_id=agency_id,rectify_assign_date=assign_date,current_status=3)
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
                created_input_file = Document.objects.filter(id=file).update(rectify_agency_id=agency_id,rectify_assign_date=assign_date,digitize_agency_id=agency_id,digitize_assign_date=assign_date,current_status=3)
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
            created_input_file = Document.objects.filter(id=file).update(digitize_agency_id=agency_id,digitize_assign_date=assign_date,current_status=8)
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
            created_input_file = Document.objects.filter(id=file).update(qc_agency_id=agency_id,qc_assign_date=assign_date,current_status=13)
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
        try:
            user_id = get_object_or_404(User, id=user_id)
        except Http404:
            return Response({"message": f"Agency with ID {user_id} does not exist"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.get('document_id', [])
        total_len = 0

        for file in data:
            assign_date =datetime.now()
            created_input_file = Document.objects.filter(id=file).update(rectify_by=user_id,rectify_assign_date=assign_date)
            total_len += 1

        return Response({"message": f"{total_len} Scan Document Assign To User"}, status=status.HTTP_201_CREATED)

class RectifyAssignToAgencyUserView(generics.GenericAPIView):
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
            created_input_file = Document.objects.filter(id=file).update(digitize_by=user_id,digitize_assign_date=assign_date)
            total_len += 1

        return Response({"message": f"{total_len} Rectify Document Assign To User"}, status=status.HTTP_201_CREATED)

class DigitizeAssignToAgencyUserView(generics.GenericAPIView):
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
            created_input_file = Document.objects.filter(id=file).update(qc_by=user_id,qc_assign_date=assign_date)
            total_len += 1

        return Response({"message": f"{total_len} Digitize Document Assign To User"}, status=status.HTTP_201_CREATED)

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
        team_ids = User.objects.filter(id=self.request.user.id).values_list('agency__team', flat=True)
        if User.objects.filter(id=self.request.user.id, user_role__role_name="Super Admin"):
            query_set = queryset.filter(current_status=10).order_by('-date_created')
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Team Admin"):
            query_set = queryset.filter(team_id__in=team_ids,current_status=10).order_by('-date_created')
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Agency Admin"):
            query_set = queryset.filter(qc_agency_id__in=agency_ids,current_status=13).exclude(qc_by__isnull=False).order_by('-date_created')
        else:
            current_status_values = [13,14,17,21]
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
        digitize_start_date = self.request.query_params.get('digitize_start_date',None)
        digitize_end_date = self.request.query_params.get('digitize_end_date',None)
        scan_by_username = self.request.query_params.get('scan_by_username', None)
        rectify_by_username = self.request.query_params.get('rectify_by_username', None)
        digitize_by_username = self.request.query_params.get('digitize_by_username', None)
        qc_by_username = self.request.query_params.get('qc_by_username', None)
        pdf_by_username = self.request.query_params.get('pdf_by_username', None)
        shape_by_username = self.request.query_params.get('shape_by_username', None)
        
        if digitize_start_date and digitize_end_date:
            digitize_start_date = datetime.strptime(digitize_start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
            digitize_end_date = datetime.strptime(digitize_end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query_set = query_set.filter(
                        digitize_completed_date__gte=digitize_start_date.date(),
                        digitize_completed_date__lt=(digitize_end_date.date() + timedelta(days=1)))
        
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
        team_ids = User.objects.filter(id=self.request.user.id).values_list('agency__team', flat=True)
        if User.objects.filter(id=self.request.user.id, user_role__role_name="Super Admin"):
            query_set = queryset.filter(current_status=15).order_by('-date_created')
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Team Admin"):
            query_set = queryset.filter(team_id__in=team_ids,current_status=15).order_by('-date_created')
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Agency Admin"):
            query_set = queryset.filter(qc_agency_id__in=agency_ids,current_status=15).order_by('-date_created')
        else:
            current_status_values = [18,19,22,26]
            query_set = queryset.filter(qc_agency_id__in=agency_ids,pdf_by=self.request.user.id,current_status=current_status_values).order_by('-date_created')

        village_name = self.request.query_params.get('village_name', None)
        taluka_name = self.request.query_params.get('taluka_name', None)
        district_name = self.request.query_params.get('district_name', None)
        barcode_number = self.request.query_params.get('barcode_number', None)
        file_name = self.request.query_params.get('file_name', None)
        district_code = self.request.query_params.get('district_code', None)
        village_code = self.request.query_params.get('village_code', None)
        map_code = self.request.query_params.get('map_code', None)
        current_status = self.request.query_params.get('current_status', None)
        qc_start_date = self.request.query_params.get('qc_start_date',None)
        qc_end_date = self.request.query_params.get('qc_end_date',None)
        scan_by_username = self.request.query_params.get('scan_by_username', None)
        rectify_by_username = self.request.query_params.get('rectify_by_username', None)
        digitize_by_username = self.request.query_params.get('digitize_by_username', None)
        qc_by_username = self.request.query_params.get('qc_by_username', None)
        pdf_by_username = self.request.query_params.get('pdf_by_username', None)
        shape_by_username = self.request.query_params.get('shape_by_username', None)
        
        
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
        team_ids = User.objects.filter(id=self.request.user.id).values_list('agency__team', flat=True)
        if User.objects.filter(id=self.request.user.id, user_role__role_name="Super Admin"):
            query_set = queryset.filter(current_status=20).order_by('-date_created')
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Team Admin"):
            query_set = queryset.filter(team_id__in=team_ids,current_status=20).order_by('-date_created')
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Agency Admin"):
            query_set = queryset.filter(qc_agency_id__in=agency_ids,current_status=20).order_by('-date_created')
        else:
            current_status_values = [23,24,27]
            query_set = queryset.filter(qc_agency_id__in=agency_ids,shape_by=self.request.user.id,current_status=current_status_values).order_by('-date_created')
        
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
    
def scan_download_file(request, document_id):
    try:
        download_file = get_object_or_404(Document, id=document_id)
        file_path = download_file.scan_upload.path
        content_type, _ = guess_type(file_path)

        with open(file_path, 'rb') as file:
            response = HttpResponse(file.read(), content_type=content_type)
            
            # Get the original filename from the path
            original_filename = os.path.basename(file_path)
            modified_filename = original_filename.replace("_O", "")

            # Set the Content-Disposition header with the original filename
            response['Content-Disposition'] = f'attachment; filename="{quote(modified_filename)}"'

            # Update the status here if needed
            update_status = Document.objects.filter(id=download_file.id).update(current_status=4)
            
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
            original_filename = os.path.basename(file_path)
            modified_filename = original_filename.replace("_R", "")
         
            # Set the Content-Disposition header with the original filename
            response['Content-Disposition'] = f'attachment; filename="{quote(modified_filename)}"'

            # Update the status here if needed
            update_status = Document.objects.filter(id=download_file.id).update(current_status=9)
            
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
            update_status = Document.objects.filter(id=download_file.id).update(current_status=14)
            
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
            update_status = Document.objects.filter(id=download_file.id).update(current_status=19)
            
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
            update_status = Document.objects.filter(id=download_file.id).update(current_status=24)
            
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
    search_fields = ["map_code"]
    filterset_fields = ['map_code','file_name','district_code','village_code','taluka_code','bel_scan_uploaded','bel_draft_uploaded','bel_gov_scan_qc_approved','bel_gov_draft_qc_approved']
    
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
            query_set = queryset.all().order_by('-date_created')
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Team Admin"):
            query_set = queryset.filter(team_id__in=team_ids).order_by('-date_created')
       
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Agency Admin"):
            agency_filters = Q(rectify_agency_id__in=agency_ids) | Q(digitize_agency_id__in=agency_ids) | Q(qc_agency_id__in=agency_ids)
            query_set = queryset.filter(agency_filters).order_by('-date_created')
        else:
            query_set = queryset.none()  # Return an empty queryset for other roles
       
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
                    update_data = {
                        'rectify_agency_id':rectify_agency_id,
                        'team_id':agency_team_id,
                        'rectify_upload': uploaded_file,  # Pass the uploaded file data
                        "rectify_by": rectify_obj,
                        "rectify_completed_date": completed_date,
                        "current_status": 5
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
                    obj = Document.objects.get(barcode_number=code,rectify_completed_date__isnull=False,current_status__in=[5,8,9,12,16])
                    new_filename = f"{base_filename}{file_extension}"

                    # Create a SimpleUploadedFile with the file data
                    uploaded_file = SimpleUploadedFile(name=new_filename, content=file.read())

                    # Create a dictionary with the data to update
                    digitize_obj = self.request.user.id
                    digitize_agency_id = self.request.user.agency.id
                    completed_date = datetime.now()
                    update_data = {
                        'digitize_agency_id':digitize_agency_id,
                        'digitize_upload': uploaded_file,  # Pass the uploaded file data
                        "digitize_by": digitize_obj,
                        "digitize_completed_date": completed_date,
                        "current_status": 10
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

class UpdateQCFileCreateView(generics.GenericAPIView):
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
                        "shape_by":pdf_obj,
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
                code = base_filename.split("_")[0]

                try:
                    # Get the existing object based on the barcode
                    obj = Document.objects.get(barcode_number=code)
                    new_filename = f"{base_filename}{file_extension}"

                    # Create a SimpleUploadedFile with the file data
                    uploaded_file = SimpleUploadedFile(name=new_filename, content=file.read())

                    # Create a dictionary with the data to update
                    shape_obj = self.request.user.id
                    completed_date = datetime.now()
                    update_data = {
                        "shape_upload": uploaded_file,  # Pass the uploaded file data
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
                    serializer.save(current_status=DocumentStatus.objects.get(id=26))
        
            return Response({"message": "Shape Files Rejected"})
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
                    serializer.save(current_status=DocumentStatus.objects.get(id=27))
        
            return Response({"message": "Shape Files On-Hold"})
            # Handle 'onhold' action here
            # Update current_status to 2 for the appropriate documents
            # Add your code for the 'onhold' action here

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
                obj = Document.objects.get(barcode_number=code)
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
                    "current_status":1
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

            csv_data = generate_data_csv(csv_header, csv_body, f"notfound_report_{datetime.now()}_.csv")
            return Response({'csv_path': csv_data.get('csv_path')})

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        queryset = self.queryset
        team_ids = User.objects.filter(id=self.request.user.id).values_list('agency__team', flat=True)
        if User.objects.filter(id=self.request.user.id, user_role__role_name="Super Admin"):
            query_set = queryset.filter(current_status=28).order_by('-date_created')
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Team Admin"):
            query_set = queryset.filter(team_id__in=team_ids,current_status=28).order_by('-date_created')
        
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
    
class ExportFileScanDocumentListView(ListAPIView):
    queryset = Document.objects.all()
    permission_classes = [IsAuthenticated,]
    authentication_classes = (TokenAuthentication,)
    serializer_class = ScanDocumentListSerializer
    filter_backends = [DjangoFilterBackend,filters.SearchFilter]
    search_fields = []
    filterset_fields = ['taluka_code']

   
    def get_queryset(self):
        queryset = self.queryset
        agency_ids = User.objects.filter(id=self.request.user.id).values_list('agency', flat=True)
        team_ids = User.objects.filter(id=self.request.user.id).values_list('agency__team', flat=True)
        if User.objects.filter(id=self.request.user.id, user_role__role_name="Super Admin"):
            query_set = queryset.filter(current_status=1).order_by('-date_created')
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Team Admin"):
            query_set = queryset.filter(team_id__in=team_ids,current_status=1).order_by('-date_created')
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Agency Admin"):
            query_set = queryset.filter(rectify_agency_id__in=agency_ids,current_status=3).exclude(rectify_by__isnull=False).order_by('-date_created')
        else:
            current_status_values = [3, 4, 7,11]
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
                
                # Read the Excel file using pandas
                df = pd.read_excel(uploaded_file)
                
                # Extract barcode numbers from the Excel file and remove backticks
                excel_barcodes = df['DOCID'].tolist()  # Replace 'Barcode Column Name' with the actual column name
                excel_barcodes = [barcode.replace('`', '') for barcode in excel_barcodes]

                # Iterate through barcode numbers
                for barcode in excel_barcodes:
                    
                    # Find documents with matching barcode numbers in the database
                    matching_documents = Document.objects.filter(barcode_number=barcode)
                    
                    # Update bel_scan_uploaded for matching documents
                    matching_documents.update(bel_scan_uploaded=True)
                
                # Return response or perform additional actions as needed
                return Response({'message': 'Bel Scan Uploaded  successfully'})
            
            elif action == 'bel_draft_uploaded':
                uploaded_file = request.FILES['file']  # Assuming 'file' is the key for the uploaded Excel file
                
                # Read the Excel file using pandas
                df = pd.read_excel(uploaded_file)
                
                # Extract barcode numbers from the Excel file and remove backticks
                excel_barcodes = df['DOCID'].tolist()  # Replace 'Barcode Column Name' with the actual column name
                excel_barcodes = [barcode.replace('`', '') for barcode in excel_barcodes]

                # Iterate through barcode numbers
                for barcode in excel_barcodes:
                    # Find documents with matching barcode numbers in the database
                    matching_documents = Document.objects.filter(barcode_number=barcode)
                    
                    # Update bel_scan_uploaded for matching documents
                    matching_documents.update(bel_draft_uploaded=True,bel_scan_uploaded=True,bel_gov_scan_qc_approved=True)
                
                # Return response or perform additional actions as needed
                return Response({'message': 'Bel Draft Uploaded  successfully'})
            
            elif action == 'bel_gov_scan_qc_approved':
                uploaded_file = request.FILES['file']  # Assuming 'file' is the key for the uploaded Excel file
                
                # Read the Excel file using pandas
                df = pd.read_excel(uploaded_file)
                
                # Extract barcode numbers from the Excel file and remove backticks
                excel_barcodes = df['DOCID'].tolist()  # Replace 'Barcode Column Name' with the actual column name
                excel_barcodes = [barcode.replace('`', '') for barcode in excel_barcodes]

                # Iterate through barcode numbers
                for barcode in excel_barcodes:                
                    # Find documents with matching barcode numbers in the database
                    matching_documents = Document.objects.filter(barcode_number=barcode)
                    
                    # Update bel_scan_uploaded for matching documents
                    matching_documents.update(bel_gov_scan_qc_approved=True,bel_scan_uploaded=True)
                
                # Return response or perform additional actions as needed
                return Response({'message': 'Bel Government Scan Qc Approved successfully'})
            
            elif action == 'bel_gov_draft_qc_approved':
                uploaded_file = request.FILES['file']  # Assuming 'file' is the key for the uploaded Excel file
                
                # Read the Excel file using pandas
                df = pd.read_excel(uploaded_file)
                
                # Extract barcode numbers from the Excel file and remove backticks
                excel_barcodes = df['DOCID'].tolist()  # Replace 'Barcode Column Name' with the actual column name
                excel_barcodes = [barcode.replace('`', '') for barcode in excel_barcodes]

                # Iterate through barcode numbers
                for barcode in excel_barcodes:
                    
                    # Find documents with matching barcode numbers in the database
                    matching_documents = Document.objects.filter(barcode_number=barcode)
                    
                    # Update bel_scan_uploaded for matching documents
                    matching_documents.update(bel_gov_draft_qc_approved=True,bel_draft_uploaded=True,bel_scan_uploaded=True,bel_gov_scan_qc_approved=True)
                
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
                    file_path = download_file.scan_upload.path
                    # Get the original filename from the path
                    original_filename = os.path.basename(file_path)
                    modified_filename = original_filename.replace("_O", "")
                elif action == 'rectify':
                    file_path = download_file.rectify_upload.path
                    # Get the original filename from the path
                    original_filename = os.path.basename(file_path)
                    modified_filename = original_filename.replace("_R", "")
                elif action == 'digitize':
                    file_path = download_file.digitize_upload.path
                    # Get the original filename from the path
                    original_filename = os.path.basename(file_path)
                    modified_filename = original_filename.replace("_D", "")
                elif action == 'qc':
                    file_path = download_file.qc_upload.path
                    # Get the original filename from the path
                    original_filename = os.path.basename(file_path)
                    if "_Q" in original_filename:
                        modified_filename = original_filename.replace("_Q", "")
                    else:
                        modified_filename = original_filename
                elif action == 'pdf':
                    file_path = download_file.pdf_upload.path

                    # Get the original filename from the path
                    original_filename = os.path.basename(file_path)
                    if "_P" in original_filename:
                        modified_filename = original_filename.replace("_P", "")
                    else:
                        modified_filename = original_filename

                elif action == 'not-found':
                    file_path = download_file.scan_upload.path
                    # Get the original filename from the path
                    original_filename = os.path.basename(file_path)
                    modified_filename = original_filename
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
        map_obj = Document.objects.get(id=kwargs.get("pk"))
        map_obj.delete()
        return Response({"message": "Record deleted successfully","status":True},status=status.HTTP_204_NO_CONTENT)
    


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
                    created_input_file = Document.objects.filter(id=file).update(rectify_agency_id=None,rectify_assign_date=None,rectify_by=None,current_status=1)
                    total_len += 1
                return Response({"message": f"{total_len} Back To Rectify Allocated Files"}, status=status.HTTP_201_CREATED)
            elif action == 'digitize':
                data = request.data.get('document_id', [])
                total_len = 0
                for file in data:
                    assign_date =datetime.now()
                    created_input_file = Document.objects.filter(id=file).update(digitize_agency_id=None,digitize_assign_date=None,digitize_by=None,current_status=5)
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
            query_set = queryset.filter(current_status__in=[3,8,13]).order_by('-date_created')
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Team Admin"):
            query_set = queryset.filter(team_id__in=team_ids,current_status__in=[3,8,13]).order_by('-date_created')
        else:
            query_set = queryset.none()  # Return an empty queryset for other roles
       
        village_name = self.request.query_params.get('village_name', None)
        taluka_name = self.request.query_params.get('taluka_name', None)
        district_name = self.request.query_params.get('district_name', None)
        scan_by_username = self.request.query_params.get('scan_by_username', None)
        current_status = self.request.query_params.get('current_status', None)
        scan_start_date = self.request.query_params.get('scan_start_date',None)
        scan_end_date = self.request.query_params.get('scan_end_date',None)
        agency_name = self.request.query_params.get('agency_name',None)

        if agency_name:
            query_set = query_set.filter(rectify_agency_id__agency_name__icontains=agency_name)
        
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
        
        
        if scan_by_username:
            query_set = query_set.filter(scan_uploaded_by__username__icontains=scan_by_username)
        

        if current_status:
            query_set = query_set.filter(current_status__status__icontains=current_status)
            
        return query_set