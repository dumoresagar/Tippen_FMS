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
from core.models import Document,DocumentStatus,PaginationMaster,MapType,TeamDistrictMaster
from datetime import datetime,date, time, timedelta
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


class DashboardView(APIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    # This API User Base Count Display
    def get(self, request):
        agency_ids = User.objects.filter(id=self.request.user.id).values_list('agency', flat=True)
        team_ids = User.objects.filter(id=self.request.user.id).values_list('agency__team', flat=True)

        if User.objects.filter(id=self.request.user.id, user_role__role_name="Super Admin"):
            polygon_count = Document.objects.all().aggregate(total_amount=Sum('polygon_count'))['total_amount']
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Team Admin"):
            polygon_count = Document.objects.filter(team_id__in=team_ids).aggregate(total_amount=Sum('polygon_count'))['total_amount']
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Agency Admin"):
            polygon_count = Document.objects.filter(digitize_agency_id__in=agency_ids).aggregate(total_amount=Sum('polygon_count'))['total_amount']
        else:
            polygon_count = 0

        if User.objects.filter(id=self.request.user.id, user_role__role_name="Super Admin"):
            qc_polygon_count = Document.objects.all().aggregate(total_amount=Sum('qc_polygon_count'))['total_amount']
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Team Admin"):
            qc_polygon_count = Document.objects.filter(team_id__in=team_ids).aggregate(total_amount=Sum('qc_polygon_count'))['total_amount']
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Agency Admin"):
            qc_polygon_count = Document.objects.filter(qc_agency_id__in=agency_ids).aggregate(total_amount=Sum('qc_polygon_count'))['total_amount']
        else:
            qc_polygon_count = 0

        if User.objects.filter(id=self.request.user.id, user_role__role_name="Super Admin"):
            total_scan_uploaded = Document.objects.all().count()
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Team Admin"):
            total_scan_uploaded = Document.objects.filter(team_id__in=team_ids).order_by('-date_created')
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Agency Admin"):
            total_scan_uploaded = Document.objects.filter(rectify_agency_id__in=agency_ids).count()   
        else:
            total_scan_uploaded = 0

        if User.objects.filter(id=self.request.user.id, user_role__role_name="Super Admin"):
            scan_uploaded = Document.objects.filter(current_status=1).count()
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Team Admin"):
            scan_uploaded = Document.objects.filter(team_id__in=team_ids,current_status=1).order_by('-date_created')

        elif User.objects.filter(id=self.request.user.id,user_role__role_name="Agency Admin"):
            scan_uploaded = Document.objects.filter(team_id__in=team_ids,current_status=1) 
        else:
            scan_uploaded = 0

        if User.objects.filter(id=self.request.user.id, user_role__role_name="Super Admin"):
            not_found = Document.objects.filter(current_status=28).count()
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Team Admin"):
            not_found = Document.objects.filter(team_id__in=team_ids,current_status=28).order_by('-date_created')

        elif User.objects.filter(id=self.request.user.id,user_role__role_name="Agency Admin"):
            not_found = Document.objects.filter(rectify_agency_id__in=agency_ids,current_status=28)
        else:
            not_found = 0

        if User.objects.filter(id=self.request.user.id, user_role__role_name="Super Admin"):
            rectify_allocated = Document.objects.filter(current_status=3).count()
            rectify_inprocess = Document.objects.filter(current_status=4).count()
            rectify_rejected = Document.objects.filter(current_status=6).count()
            rectify_onhold = Document.objects.filter(current_status=7).count()
            rectify_completed = Document.objects.filter(rectify_completed_date__isnull=False).count()

        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Team Admin"):
            rectify_allocated = Document.objects.filter(team_id__in=team_ids,current_status=3).count()
            rectify_inprocess = Document.objects.filter(team_id__in=team_ids,current_status=4).count()
            rectify_rejected = Document.objects.filter(team_id__in=team_ids,current_status=6).count()
            rectify_onhold = Document.objects.filter(team_id__in=team_ids,current_status=7).count()
            rectify_completed = Document.objects.filter(team_id__in=team_ids,rectify_completed_date__isnull=False).count()

        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Agency Admin"):
            rectify_allocated = Document.objects.filter(rectify_agency_id__in=agency_ids,current_status=3).count()
            rectify_inprocess = Document.objects.filter(rectify_agency_id__in=agency_ids,current_status=4).count()
            rectify_rejected = Document.objects.filter(rectify_agency_id__in=agency_ids,current_status=6).count()
            rectify_onhold = Document.objects.filter(rectify_agency_id__in=agency_ids,current_status=7).count()
            rectify_completed = Document.objects.filter(rectify_agency_id__in=agency_ids,rectify_completed_date__isnull=False).count()
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="User"):
            rectify_allocated = Document.objects.filter(rectify_agency_id__in=agency_ids,rectify_by=self.request.user,current_status=3).count()
            rectify_inprocess = Document.objects.filter(rectify_agency_id__in=agency_ids,rectify_by=self.request.user,current_status=4).count()
            rectify_rejected = Document.objects.filter(rectify_agency_id__in=agency_ids,rectify_by=self.request.user,current_status=6).count()
            rectify_onhold = Document.objects.filter(rectify_agency_id__in=agency_ids,rectify_by=self.request.user,current_status=7).count()
            rectify_completed = Document.objects.filter(rectify_agency_id__in=agency_ids,rectify_by=self.request.user,rectify_completed_date__isnull=False).count()
        else:
            rectify_allocated = 0
            rectify_inprocess = 0
            rectify_rejected = 0
            rectify_onhold = 0
            rectify_completed = 0
        
        if User.objects.filter(id=self.request.user.id, user_role__role_name="Super Admin"):
            digitize_allocated = Document.objects.filter(current_status=8).count()
            digitize_inprocess = Document.objects.filter(current_status=9).count()
            digitize_rejected = Document.objects.filter(current_status=11).count()
            digitize_onhold = Document.objects.filter(current_status=12).count()
            digitize_completed = Document.objects.filter(digitize_completed_date__isnull=False).count()

        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Team Admin"):
            digitize_allocated = Document.objects.filter(team_id__in=team_ids,current_status=8).count()
            digitize_inprocess = Document.objects.filter(team_id__in=team_ids,current_status=9).count()
            digitize_rejected = Document.objects.filter(team_id__in=team_ids,current_status=11).count()
            digitize_onhold = Document.objects.filter(team_id__in=team_ids,current_status=12).count()
            digitize_completed = Document.objects.filter(team_id__in=team_ids,digitize_completed_date__isnull=False).count()


        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Agency Admin"):
            digitize_allocated = Document.objects.filter(digitize_agency_id__in=agency_ids,current_status=8).count()
            digitize_inprocess = Document.objects.filter(digitize_agency_id__in=agency_ids,current_status=9).count()
            digitize_rejected = Document.objects.filter(digitize_agency_id__in=agency_ids,current_status=11).count()
            digitize_onhold = Document.objects.filter(digitize_agency_id__in=agency_ids,current_status=12).count()
            digitize_completed = Document.objects.filter(digitize_agency_id__in=agency_ids,digitize_completed_date__isnull=False).count()
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="User"):
            digitize_allocated = Document.objects.filter(digitize_agency_id__in=agency_ids,digitize_by=self.request.user,current_status=8).count()
            digitize_inprocess = Document.objects.filter(digitize_agency_id__in=agency_ids,digitize_by=self.request.user,current_status=9).count()
            digitize_rejected = Document.objects.filter(digitize_agency_id__in=agency_ids,digitize_by=self.request.user,current_status=11).count()
            digitize_onhold = Document.objects.filter(digitize_agency_id__in=agency_ids,digitize_by=self.request.user,current_status=12).count()
            digitize_completed = Document.objects.filter(digitize_agency_id__in=agency_ids,digitize_by=self.request.user,digitize_completed_date__isnull=False).count()
        else:
            digitize_allocated = 0
            digitize_inprocess = 0
            digitize_rejected = 0
            digitize_onhold = 0
            digitize_completed = 0

        
        if User.objects.filter(id=self.request.user.id, user_role__role_name="Super Admin"):
            qc_allocated = Document.objects.filter(current_status=13).count()
            qc_inprocess = Document.objects.filter(current_status=14).count()
            qc_rejected = Document.objects.filter(current_status=16).count()
            qc_onhold = Document.objects.filter(current_status=17).count()
            qc_completed = Document.objects.filter(qc_completed_date__isnull=False).count()

        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Team Admin"):
            qc_allocated = Document.objects.filter(team_id__in=team_ids,current_status=13).count()
            qc_inprocess = Document.objects.filter(team_id__in=team_ids,current_status=14).count()
            qc_rejected = Document.objects.filter(team_id__in=team_ids,current_status=16).count()
            qc_onhold = Document.objects.filter(team_id__in=team_ids,current_status=17).count()
            qc_completed = Document.objects.filter(team_id__in=team_ids,qc_completed_date__isnull=False).count()

        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Agency Admin"):
            qc_allocated = Document.objects.filter(qc_agency_id__in=agency_ids,current_status=13).count()
            qc_inprocess = Document.objects.filter(qc_agency_id__in=agency_ids,current_status=14).count()
            qc_rejected = Document.objects.filter(qc_agency_id__in=agency_ids,current_status=16).count()
            qc_onhold = Document.objects.filter(qc_agency_id__in=agency_ids,current_status=17).count()
            qc_completed = Document.objects.filter(qc_agency_id__in=agency_ids,qc_completed_date__isnull=False).count()
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="User"):
            qc_allocated = Document.objects.filter(qc_agency_id__in=agency_ids,qc_by=self.request.user,current_status=13).count()
            qc_inprocess = Document.objects.filter(qc_agency_id__in=agency_ids,qc_by=self.request.user,current_status=14).count()
            qc_rejected = Document.objects.filter(qc_agency_id__in=agency_ids,qc_by=self.request.user,current_status=16).count()
            qc_onhold = Document.objects.filter(qc_agency_id__in=agency_ids,qc_by=self.request.user,current_status=17).count()
            qc_completed = Document.objects.filter(qc_agency_id__in=agency_ids,qc_by=self.request.user,qc_completed_date__isnull=False).count()
        else:
            qc_allocated = 0
            qc_inprocess = 0
            qc_rejected = 0
            qc_onhold = 0
            qc_completed = 0
        
        if User.objects.filter(id=self.request.user.id, user_role__role_name="Super Admin"):
            pdf_allocated = Document.objects.filter(current_status=18).count()
            pdf_inprocess = Document.objects.filter(current_status=19).count()
            pdf_rejected = Document.objects.filter(current_status=21).count()
            pdf_onhold = Document.objects.filter(current_status=22).count()
            pdf_completed = Document.objects.filter(pdf_completed_date__isnull=False).count()

        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Team Admin"):
            pdf_allocated = Document.objects.filter(team_id__in=team_ids,current_status=18).count()
            pdf_inprocess = Document.objects.filter(team_id__in=team_ids,current_status=19).count()
            pdf_rejected = Document.objects.filter(team_id__in=team_ids,current_status=21).count()
            pdf_onhold = Document.objects.filter(team_id__in=team_ids,current_status=22).count()
            pdf_completed = Document.objects.filter(team_id__in=team_ids,pdf_completed_date__isnull=False).count()

        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Agency Admin"):
            pdf_allocated = Document.objects.filter(qc_agency_id__in=agency_ids,current_status=18).count()
            pdf_inprocess = Document.objects.filter(qc_agency_id__in=agency_ids,current_status=19).count()
            pdf_rejected = Document.objects.filter(qc_agency_id__in=agency_ids,current_status=21).count()
            pdf_onhold = Document.objects.filter(qc_agency_id__in=agency_ids,current_status=22).count()
            pdf_completed = Document.objects.filter(qc_agency_id__in=agency_ids,pdf_completed_date__isnull=False).count()

        elif User.objects.filter(id=self.request.user.id, user_role__role_name="User"):
            pdf_allocated = Document.objects.filter(qc_agency_id__in=agency_ids,pdf_by=self.request.user,current_status=18).count()
            pdf_inprocess = Document.objects.filter(qc_agency_id__in=agency_ids,pdf_by=self.request.user,current_status=19).count()
            pdf_rejected = Document.objects.filter(qc_agency_id__in=agency_ids,pdf_by=self.request.user,current_status=21).count()
            pdf_onhold = Document.objects.filter(qc_agency_id__in=agency_ids,pdf_by=self.request.user,current_status=22).count()
            pdf_completed = Document.objects.filter(qc_agency_id__in=agency_ids,pdf_by=self.request.user,pdf_completed_date__isnull=False).count()
        else:
            pdf_allocated = 0
            pdf_inprocess = 0
            pdf_rejected = 0
            pdf_onhold = 0
            pdf_completed = 0

        if User.objects.filter(id=self.request.user.id, user_role__role_name="Super Admin"):
            shape_allocated = Document.objects.filter(current_status=23).count()
            shape_inprocess = Document.objects.filter(current_status=26).count()
            shape_rejected = Document.objects.filter(current_status=27).count()
            shape_onhold = Document.objects.filter(current_status=22).count()
            shape_completed = Document.objects.filter(shape_completed_date__isnull=False).count()


        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Team Admin"):
            shape_allocated = Document.objects.filter(team_id__in=team_ids,current_status=23).count()
            shape_inprocess = Document.objects.filter(team_id__in=team_ids,current_status=26).count()
            shape_rejected = Document.objects.filter(team_id__in=team_ids,current_status=27).count()
            shape_onhold = Document.objects.filter(team_id__in=team_ids,current_status=22).count()
            shape_completed = Document.objects.filter(team_id__in=team_ids,shape_completed_date__isnull=False).count()

        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Agency Admin"):
            shape_allocated = Document.objects.filter(qc_agency_id__in=agency_ids,current_status=23).count()
            shape_inprocess = Document.objects.filter(qc_agency_id__in=agency_ids,current_status=26).count()
            shape_rejected = Document.objects.filter(qc_agency_id__in=agency_ids,current_status=27).count()
            shape_onhold = Document.objects.filter(qc_agency_id__in=agency_ids,current_status=22).count()
            shape_completed = Document.objects.filter(qc_agency_id__in=agency_ids,shape_completed_date__isnull=False).count()
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="User"):
            shape_allocated = Document.objects.filter(qc_agency_id__in=agency_ids,shape_by=self.request.user,current_status=23).count()
            shape_inprocess = Document.objects.filter(qc_agency_id__in=agency_ids,shape_by=self.request.user,current_status=26).count()
            shape_rejected = Document.objects.filter(qc_agency_id__in=agency_ids,shape_by=self.request.user,current_status=27).count()
            shape_onhold = Document.objects.filter(qc_agency_id__in=agency_ids,shape_by=self.request.user,current_status=22).count()
            shape_completed = Document.objects.filter(qc_agency_id__in=agency_ids,shape_by=self.request.user,shape_completed_date__isnull=False).count()
        else:
            shape_allocated = 0
            shape_inprocess = 0
            shape_rejected = 0
            shape_onhold = 0
            shape_completed = 0

        if User.objects.filter(id=self.request.user.id, user_role__role_name="Super Admin"):
            bel_scan_uploaded = Document.objects.filter(bel_scan_uploaded=True).count()
            bel_draft_uploaded = Document.objects.filter(bel_draft_uploaded=True).count()
            bel_gov_scan_qc_approved = Document.objects.filter(bel_gov_scan_qc_approved=True).count()
            bel_gov_draft_qc_approved = Document.objects.filter(bel_gov_draft_qc_approved=True).count()

        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Team Admin"):
            bel_scan_uploaded = Document.objects.filter(team_id__in=team_ids,bel_scan_uploaded=True).count()
            bel_draft_uploaded = Document.objects.filter(team_id__in=team_ids,bel_draft_uploaded=True).count()
            bel_gov_scan_qc_approved = Document.objects.filter(team_id__in=team_ids,bel_gov_scan_qc_approved=True).count()
            bel_gov_draft_qc_approved = Document.objects.filter(team_id__in=team_ids,bel_gov_draft_qc_approved=True).count()

        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Agency Admin"):
            bel_scan_uploaded = Document.objects.filter(rectify_agency_id__in=agency_ids,bel_scan_uploaded=True).count()
            bel_draft_uploaded = Document.objects.filter(rectify_agency_id__in=agency_ids,bel_draft_uploaded=True).count()
            bel_gov_scan_qc_approved = Document.objects.filter(rectify_agency_id__in=agency_ids,bel_gov_scan_qc_approved=True).count()
            bel_gov_draft_qc_approved = Document.objects.filter(rectify_agency_id__in=agency_ids,bel_gov_draft_qc_approved=True).count()
        
        else:
            bel_scan_uploaded = 0
            bel_draft_uploaded = 0
            bel_gov_scan_qc_approved = 0
            bel_gov_draft_qc_approved = 0



       
        return Response(data={
            'total_scan_uploaded':total_scan_uploaded,
            'not_found_uploaded' : not_found,
            'scan_uploaded_count': scan_uploaded,
            'rectify_allocated':rectify_allocated,
            'rectify_inprocess':rectify_inprocess,
            'rectify_rejected':rectify_rejected,
            'rectify_onhold':rectify_onhold,
            'rectify_completed':rectify_completed,
            'digitize_allocated':digitize_allocated,
            'digitize_inprocess':digitize_inprocess,
            'digitize_rejected' :digitize_rejected,
            'digitize_onhold' :digitize_onhold,
            'digitize_completed':digitize_completed,
            'qc_allocated':qc_allocated,
            'qc_inprocess' :qc_inprocess,
            'qc_rejected' :qc_rejected,
            'qc_onhold' :qc_onhold,
            'qc_completed' :qc_completed,
            'pdf_allocated':pdf_allocated,
            'pdf_inprocess':pdf_inprocess,
            'pdf_rejected' :pdf_rejected,
            'pdf_onhold' :pdf_onhold,
            'pdf_completed' :pdf_completed,
            'shape_allocated':shape_allocated,
            'shape_inprocess' :shape_inprocess,
            'shape_rejected' :shape_rejected,
            'shape_onhold' :shape_onhold,
            'shape_completed':shape_completed,
            'digitize_polygon_count':polygon_count,
            'qc_polygon_count':qc_polygon_count,
            'bel_scan_uploaded':bel_scan_uploaded,
            'bel_draft_uploaded':bel_draft_uploaded,
            'bel_gov_scan_qc_approved':bel_gov_scan_qc_approved,
            'bel_gov_draft_qc_approved':bel_gov_draft_qc_approved,

            'status': True
        }, status=status.HTTP_200_OK)


class RectifyDocumentListView(generics.ListAPIView):
    queryset = Document.objects.all()
    permission_classes = [IsAuthenticated,]
    authentication_classes = (TokenAuthentication,)
    serializer_class = RectifyListSerialzer
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend,filters.SearchFilter]
    search_fields = ["map_code"]
    filterset_fields = ['barcode_number','map_code','file_name','district_code','village_code']


    def get_queryset(self):
        queryset = self.queryset
        agency_ids = User.objects.filter(id=self.request.user.id).values_list('agency', flat=True)
        if User.objects.filter(id=self.request.user.id, user_role__role_name="Super Admin"):
            query_set = queryset.all().order_by('-date_created')
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Agency Admin"):
            query_set = queryset.filter(rectify_agency_id__in=agency_ids).order_by('-date_created')
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="User"):
            query_set = queryset.filter(rectify_agency_id__in=agency_ids,rectify_by=self.request.user).order_by('-date_created')
        else:
            query_set = queryset.none()  # Return an empty queryset for other roles
  
      
            
        return query_set


class DistrictWiseDashboardView(generics.ListAPIView):
    queryset = District.objects.all()
    permission_classes = [IsAuthenticated,]
    authentication_classes = (TokenAuthentication,)
    serializer_class = DistrictListSerialzer
   


    def get_queryset(self):
        queryset = self.queryset
        team_ids = User.objects.filter(id=self.request.user.id).values_list('agency__team', flat=True)
        team_district_code = TeamDistrictMaster.objects.filter(team__in=team_ids).values_list('district_id__district_code', flat=True)


        if User.objects.filter(id=self.request.user.id, user_role__role_name="Super Admin"):
            query_set = queryset.all().order_by('-date_created')
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Team Admin"):
            query_set = queryset.filter(district_code__in=team_district_code).order_by('-date_created')
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Agency Admin"):
            query_set = queryset.filter(district_code__in=team_district_code).order_by('-date_created')
        else:
            query_set = queryset.none()  # Return an empty queryset for other roles
  
      
            
        return query_set
    
    

class UserPaginationUpdateGenericAPI(generics.GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = UpdateUserPaginationcountSerialzier
    
    def put(self,request,*args,**kwargs):
        try:
            pagination_obj = PaginationMaster.objects.get(pagination_user=kwargs.get("pk"))
        except pagination_obj.DoesNotExist:
            return Response({"msg":"record does not exist"})
        serializer = UpdateUserPaginationcountSerialzier(pagination_obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data,"message":"Success","status":True})
        return Response(serializer.errors)
    

class UserWiseDocumentListAPI(APIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    page_size = 20

    # This API User Base Count Display
    def get(self, request):
        user_name = self.request.query_params.get('user_name', None)
        dept_name = self.request.query_params.get('dept_name', None)
        agency_name = self.request.query_params.get('agency_name', None)
        rectify_start_date = self.request.query_params.get('rectify_start_date')
        rectify_end_date = self.request.query_params.get('rectify_end_date')
        digitize_start_date = self.request.query_params.get('digitize_start_date')
        digitize_end_date = self.request.query_params.get('digitize_end_date')
        qc_start_date = self.request.query_params.get('qc_start_date')
        qc_end_date = self.request.query_params.get('qc_end_date')

        agency = User.objects.filter(id=self.request.user.id).values_list('agency',flat=True)
        team_ids = User.objects.filter(id=self.request.user.id).values_list('agency__team', flat=True)

        if User.objects.filter(id=self.request.user.id, user_role__role_name="Super Admin"):
            users = User.objects.all().exclude(agency__isnull=True)  # Get all users

        elif User.objects.filter(id=self.request.user.id,user_role__role_name="Team Admin"):
            users = User.objects.filter(agency__team__in=team_ids)
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Agency Admin"):
            users = User.objects.filter(agency__in=agency)

        elif User.objects.filter(id=self.request.user.id, user_role__role_name="User"):
            users = User.objects.filter(agency__in=agency,id=self.request.user.id)

        if user_name:
            users = users.filter(agency__in=agency,username__icontains=user_name)
        if dept_name:
            users = users.filter(agency__in=agency,department__department_name__icontains=dept_name)
            
        if agency_name:
            users = users.filter(agency__in=agency,agency__agency_name__icontains=agency_name)

        if rectify_start_date and rectify_end_date:
            rectify_start_date = datetime.strptime(str(rectify_start_date), '%Y-%m-%d').replace(hour=0, minute=0, second=0)
            rectify_end_date = datetime.strptime(str(rectify_end_date), '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            # # Convert start_date and end_date to datetime objects if they are strings
            # start_date = datetime.strptime(str(start_date), '%Y-%m-%d') if isinstance(start_date, (date, str)) else start_date
            # end_date = datetime.strptime(str(end_date), '%Y-%m-%d') if isinstance(end_date, (date, str)) else end_date

            # # Ensure that start_date and end_date are datetime objects
            # start_date = datetime.combine(start_date, time.min) if isinstance(start_date, date) else start_date
            # end_date = datetime.combine(end_date, time.max) if isinstance(end_date, date) else end_date

            # # Extract the date part to handle the warning
            # start_date = start_date.date() if isinstance(start_date, datetime) else start_date
            # end_date = end_date.date() if isinstance(end_date, datetime) else end_date
        
        if qc_start_date and qc_end_date:
            qc_start_date = datetime.strptime(str(qc_start_date), '%Y-%m-%d').replace(hour=0, minute=0, second=0)
            qc_end_date = datetime.strptime(str(qc_end_date), '%Y-%m-%d').replace(hour=23, minute=59, second=59)

        if digitize_start_date and digitize_end_date:
            digitize_start_date = datetime.strptime(str(digitize_start_date), '%Y-%m-%d').replace(hour=0, minute=0, second=0)
            digitize_end_date = datetime.strptime(str(digitize_end_date), '%Y-%m-%d').replace(hour=23, minute=59, second=59)
        
        paginator = PageNumberPagination()
        paginator.page_size = self.page_size
        paginated_users = paginator.paginate_queryset(users, request)
        counts_by_user = []

        for user in users:
            user_id = user.id
            username = user.username
            departments = user.department.all()  # Assuming 'user' is an instance of the User model
            department_names = [department.department_name for department in departments]
            agency_name = user.agency.agency_name
  
            # agency_ids = user.agency.values_list('id', flat=True)
            
            counts = {
                'rectify_allocated': 0,
                'rectify_inprocess': 0,
                'rectify_rejected': 0,
                'rectify_onhold': 0,
                'rectify_completed': 0,
                'digitize_allocated': 0,
                'digitize_inprocess': 0,
                'digitize_rejected': 0,
                'digitize_onhold': 0,
                'digitize_completed': 0,
                'qc_allocated': 0,
                'qc_inprocess': 0,
                'qc_rejected': 0,
                'qc_onhold': 0,
                'qc_completed': 0,
                'pdf_allocated': 0,
                'pdf_inprocess': 0,
                'pdf_rejected': 0,
                'pdf_onhold': 0,
                'pdf_completed': 0,
                'shape_allocated': 0,
                'shape_inprocess': 0,
                'shape_rejected': 0,
                'shape_onhold': 0,
                'shape_completed': 0,
                'polygon_count':0
            }

            if User.objects.filter(id=self.request.user.id, user_role__role_name="Super Admin"):

                if rectify_start_date and rectify_end_date:
                    counts['rectify_completed'] = Document.objects.filter(
                        rectify_by=user_id,
                        rectify_completed_date__isnull=False,
                        rectify_completed_date__gte=rectify_start_date.date(),
                        rectify_completed_date__lt=(rectify_end_date.date() + timedelta(days=1))  # Add one day to include the end date
                    ).count()
                else:
                    counts['rectify_completed'] = Document.objects.filter(rectify_by=user_id, rectify_completed_date__isnull=False).count()

                counts['rectify_allocated'] = Document.objects.filter(rectify_by=user_id, current_status=3).count()
                counts['rectify_inprocess'] = Document.objects.filter(rectify_by=user_id, current_status=4).count()
                counts['rectify_rejected'] = Document.objects.filter(rectify_by=user_id, current_status=6).count()
                counts['rectify_onhold'] = Document.objects.filter(rectify_by=user_id, current_status=7).count()
                counts['digitize_allocated'] = Document.objects.filter(digitize_by=user_id, current_status=8).count()
                counts['digitize_inprocess'] = Document.objects.filter(digitize_by=user_id, current_status=9).count()
                counts['digitize_rejected'] = Document.objects.filter(digitize_by=user_id, current_status=11).count()
                counts['digitize_onhold'] = Document.objects.filter(digitize_by=user_id, current_status=12).count()

                if digitize_start_date and digitize_end_date:
                    counts['digitize_completed'] = Document.objects.filter(
                        digitize_by=user_id,
                        digitize_completed_date__isnull=False,
                        digitize_completed_date__gte=digitize_start_date.date(),
                        digitize_completed_date__lt=(digitize_end_date.date() + timedelta(days=1))  # Add one day to include the end date
                    ).count()
                else:
                    counts['digitize_completed'] = Document.objects.filter(digitize_by=user_id, digitize_completed_date__isnull=False).count()

                counts['qc_allocated'] = Document.objects.filter(qc_by=user_id, current_status=13).count()
                counts['qc_inprocess'] = Document.objects.filter(qc_by=user_id, current_status=14).count()
                counts['qc_rejected'] = Document.objects.filter(qc_by=user_id, current_status=16).count()
                counts['qc_onhold'] = Document.objects.filter(qc_by=user_id, current_status=17).count()

                if qc_start_date and qc_end_date:
                    counts['qc_completed'] = Document.objects.filter(
                        qc_by=user_id,
                        qc_completed_date__isnull=False,
                        qc_completed_date__gte=qc_start_date.date(),
                        qc_completed_date__lt=(qc_end_date.date() + timedelta(days=1))  # Add one day to include the end date
                    ).count()
                    counts['polygon_count'] = Document.objects.filter(
                                                qc_by=user_id,
                                                qc_completed_date__isnull=False,
                                                qc_completed_date__gte=qc_start_date.date(),
                                                qc_completed_date__lt=(qc_end_date.date() + timedelta(days=1))
                                              ).aggregate(total_amount=Sum('polygon_count'))['total_amount']
                else:
                    counts['qc_completed'] = Document.objects.filter(qc_by=user_id, qc_completed_date__isnull=False).count()
                    counts['polygon_count'] = Document.objects.filter(qc_by=user_id, qc_completed_date__isnull=False).aggregate(total_amount=Sum('polygon_count'))['total_amount']

                counts['pdf_allocated'] = Document.objects.filter(pdf_by=user_id, current_status=18).count()
                counts['pdf_inprocess'] = Document.objects.filter(pdf_by=user_id, current_status=19).count()
                counts['pdf_rejected'] = Document.objects.filter(pdf_by=user_id, current_status=21).count()
                counts['pdf_onhold'] = Document.objects.filter(pdf_by=user_id, current_status=22).count()
                counts['pdf_completed'] = Document.objects.filter(pdf_by=user_id, pdf_completed_date__isnull=False).count()
                counts['shape_allocated'] = Document.objects.filter(shape_by=user_id, current_status=23).count()
                counts['shape_inprocess'] = Document.objects.filter(shape_by=user_id, current_status=26).count()
                counts['shape_rejected'] = Document.objects.filter(shape_by=user_id, current_status=27).count()
                counts['shape_onhold'] = Document.objects.filter(shape_by=user_id, current_status=22).count()
                counts['shape_completed'] = Document.objects.filter(shape_by=user_id, shape_completed_date__isnull=False).count()
            
            elif User.objects.filter(id=self.request.user.id, user_role__role_name="Agency Admin"):

                if rectify_start_date and rectify_end_date:
                    counts['rectify_completed'] = Document.objects.filter(
                        rectify_agency_id__in=agency,
                        rectify_by=user_id,
                        rectify_completed_date__isnull=False,
                        rectify_completed_date__gte=rectify_start_date.date(),
                        rectify_completed_date__lt=(rectify_end_date.date() + timedelta(days=1))  # Add one day to include the end date
                    ).count()
                else:
                    counts['rectify_completed'] = Document.objects.filter(rectify_agency_id__in=agency,rectify_by=user_id,rectify_completed_date__isnull=False).count()

                counts['rectify_allocated'] = Document.objects.filter(rectify_agency_id__in=agency,rectify_by=user_id, current_status=3).count()
                counts['rectify_inprocess'] = Document.objects.filter(rectify_agency_id__in=agency,rectify_by=user_id, current_status=4).count()
                counts['rectify_rejected'] = Document.objects.filter(rectify_agency_id__in=agency,rectify_by=user_id, current_status=6).count()
                counts['rectify_onhold'] = Document.objects.filter(rectify_agency_id__in=agency,rectify_by=user_id, current_status=7).count()
                counts['digitize_allocated'] = Document.objects.filter(digitize_agency_id__in=agency,digitize_by=user_id, current_status=8).count()
                counts['digitize_inprocess'] = Document.objects.filter(digitize_agency_id__in=agency,digitize_by=user_id, current_status=9).count()
                counts['digitize_rejected'] = Document.objects.filter(digitize_agency_id__in=agency,digitize_by=user_id, current_status=11).count()
                counts['digitize_onhold'] = Document.objects.filter(digitize_agency_id__in=agency,digitize_by=user_id, current_status=12).count()

                if digitize_start_date and digitize_end_date:
                    counts['digitize_completed'] = Document.objects.filter(
                        digitize_agency_id__in=agency,
                        digitize_by=user_id,
                        digitize_completed_date__isnull=False,
                        digitize_completed_date__gte=digitize_start_date.date(),
                        digitize_completed_date__lt=(digitize_end_date.date() + timedelta(days=1))  # Add one day to include the end date
                    ).count()
                else:
                    counts['digitize_completed'] = Document.objects.filter(digitize_agency_id__in=agency,digitize_by=user_id, digitize_completed_date__isnull=False).count()

                counts['qc_allocated'] = Document.objects.filter(qc_agency_id__in=agency,qc_by=user_id, current_status=13).count()
                counts['qc_inprocess'] = Document.objects.filter(qc_agency_id__in=agency,qc_by=user_id, current_status=14).count()
                counts['qc_rejected'] = Document.objects.filter(qc_agency_id__in=agency,qc_by=user_id, current_status=16).count()
                counts['qc_onhold'] = Document.objects.filter(qc_agency_id__in=agency,qc_by=user_id, current_status=17).count()

                if qc_start_date and qc_end_date:
                    counts['qc_completed'] = Document.objects.filter(
                        qc_agency_id__in=agency,
                        qc_by=user_id,
                        qc_completed_date__isnull=False,
                        qc_completed_date__gte=qc_start_date.date(),
                        qc_completed_date__lt=(qc_end_date.date() + timedelta(days=1))  # Add one day to include the end date
                    ).count()
                    counts['polygon_count'] = Document.objects.filter(
                                                qc_agency_id__in=agency,
                                                qc_by=user_id,
                                                qc_completed_date__isnull=False,
                                                qc_completed_date__gte=qc_start_date.date(),
                                                qc_completed_date__lt=(qc_end_date.date() + timedelta(days=1))
                                              ).aggregate(total_amount=Sum('polygon_count'))['total_amount']
                else:
                    counts['qc_completed'] = Document.objects.filter(qc_agency_id__in=agency,qc_by=user_id, qc_completed_date__isnull=False).count()
                    counts['polygon_count'] = Document.objects.filter(qc_agency_id__in=agency,qc_by=user_id, qc_completed_date__isnull=False).aggregate(total_amount=Sum('polygon_count'))['total_amount']

                counts['pdf_allocated'] = Document.objects.filter(qc_agency_id__in=agency,pdf_by=user_id, current_status=18).count()
                counts['pdf_inprocess'] = Document.objects.filter(qc_agency_id__in=agency,pdf_by=user_id, current_status=19).count()
                counts['pdf_rejected'] = Document.objects.filter(qc_agency_id__in=agency,pdf_by=user_id, current_status=21).count()
                counts['pdf_onhold'] = Document.objects.filter(qc_agency_id__in=agency,pdf_by=user_id, current_status=22).count()
                counts['pdf_completed'] = Document.objects.filter(qc_agency_id__in=agency,pdf_by=user_id, pdf_completed_date__isnull=False).count()
                counts['shape_allocated'] = Document.objects.filter(qc_agency_id__in=agency,shape_by=user_id, current_status=23).count()
                counts['shape_inprocess'] = Document.objects.filter(qc_agency_id__in=agency,shape_by=user_id, current_status=26).count()
                counts['shape_rejected'] = Document.objects.filter(qc_agency_id__in=agency,shape_by=user_id, current_status=27).count()
                counts['shape_onhold'] = Document.objects.filter(qc_agency_id__in=agency,shape_by=user_id, current_status=22).count()
                counts['shape_completed'] = Document.objects.filter(qc_agency_id__in=agency,shape_by=user_id, shape_completed_date__isnull=False).count()
            
            elif User.objects.filter(id=self.request.user.id, user_role__role_name="User"):
                if rectify_start_date and rectify_end_date:
                    counts['rectify_completed'] = Document.objects.filter(
                        rectify_agency_id__in=agency,
                        rectify_by=user_id,
                        rectify_completed_date__isnull=False,
                        rectify_completed_date__gte=rectify_start_date.date(),
                        rectify_completed_date__lt=(rectify_end_date.date() + timedelta(days=1))  # Add one day to include the end date
                    ).count()
                else:
                    counts['rectify_completed'] = Document.objects.filter(rectify_agency_id__in=agency,rectify_by=user_id, rectify_completed_date__isnull=False).count()

                counts['rectify_allocated'] = Document.objects.filter(rectify_agency_id__in=agency,rectify_by=user_id, current_status=3).count()
                counts['rectify_inprocess'] = Document.objects.filter(rectify_agency_id__in=agency,rectify_by=user_id, current_status=4).count()
                counts['rectify_rejected'] = Document.objects.filter(rectify_agency_id__in=agency,rectify_by=user_id, current_status=6).count()
                counts['rectify_onhold'] = Document.objects.filter(rectify_agency_id__in=agency,rectify_by=user_id, current_status=7).count()
                counts['digitize_allocated'] = Document.objects.filter(digitize_agency_id__in=agency,digitize_by=user_id, current_status=8).count()
                counts['digitize_inprocess'] = Document.objects.filter(digitize_agency_id__in=agency,digitize_by=user_id, current_status=9).count()
                counts['digitize_rejected'] = Document.objects.filter(digitize_agency_id__in=agency,digitize_by=user_id, current_status=11).count()
                counts['digitize_onhold'] = Document.objects.filter(digitize_agency_id__in=agency,digitize_by=user_id, current_status=12).count()

                if digitize_start_date and digitize_end_date:
                    counts['digitize_completed'] = Document.objects.filter(
                        digitize_agency_id__in=agency,
                        digitize_by=user_id,
                        digitize_completed_date__isnull=False,
                        digitize_completed_date__gte=digitize_start_date.date(),
                        digitize_completed_date__lt=(digitize_end_date.date() + timedelta(days=1))  # Add one day to include the end date
                    ).count()
                else:
                    counts['digitize_completed'] = Document.objects.filter(digitize_agency_id__in=agency,digitize_by=user_id,  digitize_completed_date__isnull=False).count()

                counts['qc_allocated'] = Document.objects.filter(qc_agency_id__in=agency,qc_by=user_id, current_status=13).count()
                counts['qc_inprocess'] = Document.objects.filter(qc_agency_id__in=agency,qc_by=user_id, current_status=14).count()
                counts['qc_rejected'] = Document.objects.filter(qc_agency_id__in=agency,qc_by=user_id, current_status=16).count()
                counts['qc_onhold'] = Document.objects.filter(qc_agency_id__in=agency,qc_by=user_id, current_status=17).count()

                if qc_start_date and qc_end_date:
                    counts['qc_completed'] = Document.objects.filter(
                        qc_agency_id__in=agency,
                        qc_by=user_id,
                        qc_completed_date__isnull=False,
                        qc_completed_date__gte=qc_start_date.date(),
                        qc_completed_date__lt=(qc_end_date.date() + timedelta(days=1))  # Add one day to include the end date
                    ).count()
                    counts['polygon_count'] = Document.objects.filter(
                                                qc_agency_id__in=agency,
                                                qc_by=user_id,
                                                qc_completed_date__isnull=False,
                                                qc_completed_date__gte=qc_start_date.date(),
                                                qc_completed_date__lt=(qc_end_date.date() + timedelta(days=1))
                                              ).aggregate(total_amount=Sum('polygon_count'))['total_amount']
                else:
                    counts['qc_completed'] = Document.objects.filter(qc_agency_id__in=agency,qc_by=user_id, qc_completed_date__isnull=False).count()
                    counts['polygon_count'] = Document.objects.filter(qc_agency_id__in=agency,qc_by=user_id, qc_completed_date__isnull=False).aggregate(total_amount=Sum('polygon_count'))['total_amount']

                counts['pdf_allocated'] = Document.objects.filter(qc_agency_id__in=agency,pdf_by=user_id, current_status=18).count()
                counts['pdf_inprocess'] = Document.objects.filter(qc_agency_id__in=agency,pdf_by=user_id, current_status=19).count()
                counts['pdf_rejected'] = Document.objects.filter(qc_agency_id__in=agency,pdf_by=user_id, current_status=21).count()
                counts['pdf_onhold'] = Document.objects.filter(qc_agency_id__in=agency,pdf_by=user_id, current_status=22).count()
                counts['pdf_completed'] = Document.objects.filter(qc_agency_id__in=agency,pdf_by=user_id, pdf_completed_date__isnull=False).count()
                counts['shape_allocated'] = Document.objects.filter(qc_agency_id__in=agency,shape_by=user_id, current_status=23).count()
                counts['shape_inprocess'] = Document.objects.filter(qc_agency_id__in=agency,shape_by=user_id, current_status=26).count()
                counts['shape_rejected'] = Document.objects.filter(qc_agency_id__in=agency,shape_by=user_id, current_status=27).count()
                counts['shape_onhold'] = Document.objects.filter(qc_agency_id__in=agency,shape_by=user_id, current_status=22).count()
                counts['shape_completed'] = Document.objects.filter(qc_agency_id__in=agency,shape_by=user_id, shape_completed_date__isnull=False).count()


            counts_by_user.append({
                'user_id': user_id,
                'username':username,
                'department':department_names,
                'agency_name':agency_name,
                **counts,
            })

        response_data = {
            'pagination': {
                'per_page_count': self.page_size,
                'count':len(counts_by_user) ,
                'next': paginator.get_next_link(),
                'previous': paginator.get_previous_link(),
                'counts_by_user': counts_by_user,
            },
            # 'counts_by_user': counts_by_user,
            # 'status': True
        }

        return Response(data=response_data, status=status.HTTP_200_OK)

class TalukaWiseDashboardView(APIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    # This API User Base Count Display
    def get(self, request,district_code=None):
        district_code = self.kwargs.get('district_code')
        # user_name = self.request.query_params.get('user_name', None)
        # dept_name = self.request.query_params.get('dept_name', None)
        # agency_name = self.request.query_params.get('agency_name', None)
       

        agency = User.objects.filter(id=self.request.user.id).values_list('agency',flat=True)
        team_ids = User.objects.filter(id=self.request.user.id).values_list('agency__team', flat=True)

        if User.objects.filter(id=self.request.user.id, user_role__role_name="Super Admin"):
            doc_taluka_code = Document.objects.filter(district_code=district_code).values_list('taluka_code', flat=True).distinct()
            taluka = Taluka.objects.filter(taluka_code__in=doc_taluka_code).order_by('-date_created')
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Team Admin"):
            doc_taluka_code = Document.objects.filter(district_code=district_code).values_list('taluka_code', flat=True).distinct()
            taluka = Taluka.objects.filter(taluka_code__in=doc_taluka_code).order_by('-date_created')

        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Agency Admin"):
            doc_taluka_code = Document.objects.filter(district_code=district_code).values_list('taluka_code', flat=True).distinct()
            taluka = Taluka.objects.filter(taluka_code__in=doc_taluka_code).order_by('-date_created')

        else:
            taluka = []

        # if user_name:
        #     users = users.filter(agency__in=agency,username__icontains=user_name)
        # if dept_name:
        #     users = users.filter(agency__in=agency,department__department_name__icontains=dept_name)
            
        # if agency_name:
        #     users = users.filter(agency__in=agency,agency__agency_name__icontains=agency_name)

        counts_by_taluka = []

        for taluka_obj in taluka:
            taluka_id = taluka_obj.id
            taluka_code = taluka_obj.taluka_code
            taluka_name = taluka_obj.taluka_name
            district_id = taluka_obj.district.id
            district_name = taluka_obj.district.district_name

            counts = {
                'total_scan_uploaded':0,
                'scan_uploaded':0,
                'rectify_completed': 0,
                'digitize_completed': 0,
                'qc_completed': 0,
                'pdf_completed': 0,
                'shape_completed': 0,
                'polygon_count':0,
                'bel_scan_uploaded_count':0,
                'bel_draft_uploaded_count':0,
                'bel_gov_scan_qc_approved_count':0,
                'bel_gov_draft_qc_approved_count':0

                # 'rectify_allocated': 0,
                # 'rectify_inprocess': 0,
                # 'rectify_rejected': 0,
                # 'rectify_onhold': 0,
                # 'digitize_allocated': 0,
                # 'digitize_inprocess': 0,
                # 'digitize_rejected': 0,
                # 'digitize_onhold': 0,
                # 'qc_allocated': 0,
                # 'qc_inprocess': 0,
                # 'qc_rejected': 0,
                # 'qc_onhold': 0,
                # 'pdf_allocated': 0,
                # 'pdf_inprocess': 0,
                # 'pdf_rejected': 0,
                # 'pdf_onhold': 0,
                # 'shape_allocated': 0,
                # 'shape_inprocess': 0,
                # 'shape_rejected': 0,
                # 'shape_onhold': 0,
                
            }


            if User.objects.filter(id=self.request.user.id, user_role__role_name="Super Admin"):
                counts['total_scan_uploaded'] = Document.objects.filter(taluka_code=taluka_code).count()
                counts['scan_uploaded'] = Document.objects.filter(taluka_code=taluka_code, current_status=1).count()
                counts['rectify_completed'] = Document.objects.filter(taluka_code=taluka_code, rectify_completed_date__isnull=False).count()
                counts['digitize_completed'] = Document.objects.filter(taluka_code=taluka_code, digitize_completed_date__isnull=False).count()
                counts['qc_completed'] = Document.objects.filter(taluka_code=taluka_code, qc_completed_date__isnull=False).count()
                counts['pdf_completed'] = Document.objects.filter(taluka_code=taluka_code, pdf_completed_date__isnull=False).count()
                counts['shape_completed'] = Document.objects.filter(taluka_code=taluka_code, shape_completed_date__isnull=False).count()
                counts['polygon_count'] = Document.objects.filter(taluka_code=taluka_code).aggregate(total_amount=Sum('polygon_count'))['total_amount']
                counts['bel_scan_uploaded_count'] =Document.objects.filter(taluka_code=taluka_code,bel_scan_uploaded=True).count()
                counts['bel_draft_uploaded_count'] =Document.objects.filter(taluka_code=taluka_code,bel_draft_uploaded=True).count()
                counts['bel_gov_scan_qc_approved_count'] =Document.objects.filter(taluka_code=taluka_code,bel_gov_scan_qc_approved=True).count()
                counts['bel_gov_draft_qc_approved_count'] =Document.objects.filter(taluka_code=taluka_code,bel_gov_draft_qc_approved=True).count()

                # counts['rectify_allocated'] = Document.objects.filter(taluka_code=taluka_code, current_status=3).count()
                # counts['rectify_inprocess'] = Document.objects.filter(taluka_code=taluka_code, current_status=4).count()
                # counts['rectify_rejected'] = Document.objects.filter(taluka_code=taluka_code, current_status=6).count()
                # counts['rectify_onhold'] = Document.objects.filter(taluka_code=taluka_code, current_status=7).count()
                # counts['digitize_allocated'] = Document.objects.filter(taluka_code=taluka_code, current_status=8).count()
                # counts['digitize_inprocess'] = Document.objects.filter(taluka_code=taluka_code, current_status=9).count()
                # counts['digitize_rejected'] = Document.objects.filter(taluka_code=taluka_code, current_status=11).count()
                # counts['digitize_onhold'] = Document.objects.filter(taluka_code=taluka_code, current_status=12).count()
                # counts['qc_allocated'] = Document.objects.filter(taluka_code=taluka_code, current_status=13).count()
                # counts['qc_inprocess'] = Document.objects.filter(taluka_code=taluka_code, current_status=14).count()
                # counts['qc_rejected'] = Document.objects.filter(taluka_code=taluka_code, current_status=16).count()
                # counts['qc_onhold'] = Document.objects.filter(taluka_code=taluka_code, current_status=17).count()
                # counts['pdf_allocated'] = Document.objects.filter(taluka_code=taluka_code, current_status=18).count()
                # counts['pdf_inprocess'] = Document.objects.filter(taluka_code=taluka_code, current_status=19).count()
                # counts['pdf_rejected'] = Document.objects.filter(taluka_code=taluka_code, current_status=21).count()
                # counts['pdf_onhold'] = Document.objects.filter(taluka_code=taluka_code, current_status=22).count()
                # counts['shape_allocated'] = Document.objects.filter(taluka_code=taluka_code, current_status=23).count()
                # counts['shape_inprocess'] = Document.objects.filter(taluka_code=taluka_code, current_status=26).count()
                # counts['shape_rejected'] = Document.objects.filter(taluka_code=taluka_code, current_status=27).count()
                # counts['shape_onhold'] = Document.objects.filter(taluka_code=taluka_code, current_status=22).count()
                
            elif User.objects.filter(id=self.request.user.id, user_role__role_name="Team Admin"):
                counts['total_scan_uploaded'] = Document.objects.filter(team_id__in=team_ids,taluka_code=taluka_code).count()
                counts['scan_uploaded'] = Document.objects.filter(team_id__in=team_ids,taluka_code=taluka_code, current_status=1).count()
                counts['rectify_completed'] = Document.objects.filter(team_id__in=team_ids,taluka_code=taluka_code, rectify_completed_date__isnull=False).count()
                counts['digitize_completed'] = Document.objects.filter(team_id__in=team_ids,taluka_code=taluka_code, digitize_completed_date__isnull=False).count()
                counts['qc_completed'] = Document.objects.filter(team_id__in=team_ids,taluka_code=taluka_code, qc_completed_date__isnull=False).count()
                counts['pdf_completed'] = Document.objects.filter(team_id__in=team_ids,taluka_code=taluka_code, pdf_completed_date__isnull=False).count()
                counts['shape_completed'] = Document.objects.filter(team_id__in=team_ids,taluka_code=taluka_code, shape_completed_date__isnull=False).count()
                counts['polygon_count'] = Document.objects.filter(team_id__in=team_ids,taluka_code=taluka_code).aggregate(total_amount=Sum('polygon_count'))['total_amount']
                
                counts['bel_scan_uploaded_count'] =Document.objects.filter(team_id__in=team_ids,taluka_code=taluka_code,bel_scan_uploaded=True).count()
                counts['bel_draft_uploaded_count'] =Document.objects.filter(team_id__in=team_ids,taluka_code=taluka_code,bel_draft_uploaded=True).count()
                counts['bel_gov_scan_qc_approved_count'] =Document.objects.filter(team_id__in=team_ids,taluka_code=taluka_code,bel_gov_scan_qc_approved=True).count()
                counts['bel_gov_draft_qc_approved_count'] =Document.objects.filter(team_id__in=team_ids,taluka_code=taluka_code,bel_gov_draft_qc_approved=True).count()

               
                # counts['rectify_allocated'] = Document.objects.filter(team_id__in=team_ids,taluka_code=taluka_code, current_status=3).count()
                # counts['rectify_inprocess'] = Document.objects.filter(team_id__in=team_ids,taluka_code=taluka_code, current_status=4).count()
                # counts['rectify_rejected'] = Document.objects.filter(team_id__in=team_ids,taluka_code=taluka_code, current_status=6).count()
                # counts['rectify_onhold'] = Document.objects.filter(team_id__in=team_ids,taluka_code=taluka_code, current_status=7).count()
                # counts['digitize_allocated'] = Document.objects.filter(team_id__in=team_ids,taluka_code=taluka_code, current_status=8).count()
                # counts['digitize_inprocess'] = Document.objects.filter(team_id__in=team_ids,taluka_code=taluka_code, current_status=9).count()
                # counts['digitize_rejected'] = Document.objects.filter(team_id__in=team_ids,taluka_code=taluka_code, current_status=11).count()
                # counts['digitize_onhold'] = Document.objects.filter(team_id__in=team_ids,taluka_code=taluka_code, current_status=12).count()
                # counts['qc_allocated'] = Document.objects.filter(team_id__in=team_ids,taluka_code=taluka_code, current_status=13).count()
                # counts['qc_inprocess'] = Document.objects.filter(team_id__in=team_ids,taluka_code=taluka_code, current_status=14).count()
                # counts['qc_rejected'] = Document.objects.filter(team_id__in=team_ids,taluka_code=taluka_code, current_status=16).count()
                # counts['qc_onhold'] = Document.objects.filter(team_id__in=team_ids,taluka_code=taluka_code, current_status=17).count()
                # counts['pdf_allocated'] = Document.objects.filter(team_id__in=team_ids,taluka_code=taluka_code, current_status=18).count()
                # counts['pdf_inprocess'] = Document.objects.filter(team_id__in=team_ids,taluka_code=taluka_code, current_status=19).count()
                # counts['pdf_rejected'] = Document.objects.filter(team_id__in=team_ids,taluka_code=taluka_code, current_status=21).count()
                # counts['pdf_onhold'] = Document.objects.filter(team_id__in=team_ids,taluka_code=taluka_code, current_status=22).count()
                # counts['shape_allocated'] = Document.objects.filter(team_id__in=team_ids,taluka_code=taluka_code, current_status=23).count()
                # counts['shape_inprocess'] = Document.objects.filter(team_id__in=team_ids,taluka_code=taluka_code, current_status=26).count()
                # counts['shape_rejected'] = Document.objects.filter(team_id__in=team_ids,taluka_code=taluka_code, current_status=27).count()
                # counts['shape_onhold'] = Document.objects.filter(team_id__in=team_ids,taluka_code=taluka_code, current_status=22).count()
               
            elif User.objects.filter(id=self.request.user.id, user_role__role_name="Agency Admin"):
                counts['total_scan_uploaded'] = Document.objects.filter(rectify_agency_id__in=agency,taluka_code=taluka_code).count()
                counts['scan_uploaded'] = Document.objects.filter(rectify_agency_id__in=agency,taluka_code=taluka_code, current_status=1).count()
                counts['rectify_completed'] = Document.objects.filter(rectify_agency_id__in=agency,taluka_code=taluka_code,rectify_completed_date__isnull=False).count()
                counts['digitize_completed'] = Document.objects.filter(digitize_agency_id__in=agency,taluka_code=taluka_code, digitize_completed_date__isnull=False).count()
                counts['qc_completed'] = Document.objects.filter(qc_agency_id__in=agency,taluka_code=taluka_code, qc_completed_date__isnull=False).count()
                counts['pdf_completed'] = Document.objects.filter(qc_agency_id__in=agency,taluka_code=taluka_code, pdf_completed_date__isnull=False).count()
                counts['shape_completed'] = Document.objects.filter(qc_agency_id__in=agency,taluka_code=taluka_code, shape_completed_date__isnull=False).count()
                counts['polygon_count'] = Document.objects.filter(qc_agency_id__in=agency,taluka_code=taluka_code).aggregate(total_amount=Sum('polygon_count'))['total_amount']
                counts['bel_scan_uploaded_count'] =Document.objects.filter(rectify_agency_id__in=agency,taluka_code=taluka_code,bel_scan_uploaded=True).count()
                counts['bel_draft_uploaded_count'] =Document.objects.filter(rectify_agency_id__in=agency,taluka_code=taluka_code,bel_draft_uploaded=True).count()
                counts['bel_gov_scan_qc_approved_count'] =Document.objects.filter(qc_agency_id__in=agency,taluka_code=taluka_code,bel_gov_scan_qc_approved=True).count()
                counts['bel_gov_draft_qc_approved_count'] =Document.objects.filter(qc_agency_id__in=agency,taluka_code=taluka_code,bel_gov_draft_qc_approved=True).count()

                # counts['rectify_allocated'] = Document.objects.filter(rectify_agency_id__in=agency,taluka_code=taluka_code, current_status=3).count()
                # counts['rectify_inprocess'] = Document.objects.filter(rectify_agency_id__in=agency,taluka_code=taluka_code, current_status=4).count()
                # counts['rectify_rejected'] = Document.objects.filter(rectify_agency_id__in=agency,taluka_code=taluka_code, current_status=6).count()
                # counts['rectify_onhold'] = Document.objects.filter(rectify_agency_id__in=agency,taluka_code=taluka_code, current_status=7).count()
                # counts['digitize_allocated'] = Document.objects.filter(digitize_agency_id__in=agency,taluka_code=taluka_code, current_status=8).count()
                # counts['digitize_inprocess'] = Document.objects.filter(digitize_agency_id__in=agency,taluka_code=taluka_code, current_status=9).count()
                # counts['digitize_rejected'] = Document.objects.filter(digitize_agency_id__in=agency,taluka_code=taluka_code, current_status=11).count()
                # counts['digitize_onhold'] = Document.objects.filter(digitize_agency_id__in=agency,taluka_code=taluka_code, current_status=12).count()
                # counts['qc_allocated'] = Document.objects.filter(qc_agency_id__in=agency,taluka_code=taluka_code, current_status=13).count()
                # counts['qc_inprocess'] = Document.objects.filter(qc_agency_id__in=agency,taluka_code=taluka_code, current_status=14).count()
                # counts['qc_rejected'] = Document.objects.filter(qc_agency_id__in=agency,taluka_code=taluka_code, current_status=16).count()
                # counts['qc_onhold'] = Document.objects.filter(qc_agency_id__in=agency,taluka_code=taluka_code, current_status=17).count()
                # counts['pdf_allocated'] = Document.objects.filter(qc_agency_id__in=agency,taluka_code=taluka_code, current_status=18).count()
                # counts['pdf_inprocess'] = Document.objects.filter(qc_agency_id__in=agency,taluka_code=taluka_code, current_status=19).count()
                # counts['pdf_rejected'] = Document.objects.filter(qc_agency_id__in=agency,taluka_code=taluka_code, current_status=21).count()
                # counts['pdf_onhold'] = Document.objects.filter(qc_agency_id__in=agency,taluka_code=taluka_code, current_status=22).count()
                # counts['shape_allocated'] = Document.objects.filter(qc_agency_id__in=agency,taluka_code=taluka_code, current_status=23).count()
                # counts['shape_inprocess'] = Document.objects.filter(qc_agency_id__in=agency,taluka_code=taluka_code, current_status=26).count()
                # counts['shape_rejected'] = Document.objects.filter(qc_agency_id__in=agency,taluka_code=taluka_code, current_status=27).count()
                # counts['shape_onhold'] = Document.objects.filter(qc_agency_id__in=agency,taluka_code=taluka_code, current_status=22).count()
                


            counts_by_taluka.append({
                'taluka_id': taluka_id,
                'taluka_code':taluka_code,
                'taluka_name':taluka_name,
                'district_id':district_id,
                'district_name':district_name,
                **counts,
            })

        response_data = {
            'counts_by_taluka': counts_by_taluka,
            'status': True
        }

        return Response(data=response_data, status=status.HTTP_200_OK)


class VillageWiseDashboardView(APIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    # This API User Base Count Display
    def get(self, request,taluka_code=None):
        taluka_code = self.kwargs.get('taluka_code')
        

        agency = User.objects.filter(id=self.request.user.id).values_list('agency',flat=True)
        team_ids = User.objects.filter(id=self.request.user.id).values_list('agency__team', flat=True)

        if User.objects.filter(id=self.request.user.id, user_role__role_name="Super Admin"):
            doc_village_code = Document.objects.filter(taluka_code=taluka_code).values_list('village_code', flat=True).distinct()
            village = Village.objects.filter(village_code__in=doc_village_code).order_by('-date_created')
        
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Team Admin"):
            doc_village_code = Document.objects.filter(taluka_code=taluka_code).values_list('village_code', flat=True).distinct()
            village = Village.objects.filter(village_code__in=doc_village_code).order_by('-date_created')

        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Agency Admin"):
            doc_village_code = Document.objects.filter(taluka_code=taluka_code).values_list('village_code', flat=True).distinct()
            village = Village.objects.filter(village_code__in=doc_village_code).order_by('-date_created')

        else:
            village = []

      

        counts_by_village = []

        for village_obj in village:
            village_id = village_obj.id
            village_code = village_obj.village_code
            village_name = village_obj.village_name
            taluka_id = village_obj.taluka.id
            taluka_name = village_obj.taluka.taluka_name
            district_name = village_obj.taluka.district.district_name
  
  
            counts = {
                'total_scan_uploaded':0,
                'scan_uploaded':0,
                'rectify_completed': 0,
                'digitize_completed': 0,
                'qc_completed': 0,
                'pdf_completed': 0,
                'shape_completed': 0,
                'polygon_count':0,

                # 'rectify_allocated': 0,
                # 'rectify_inprocess': 0,
                # 'rectify_rejected': 0,
                # 'rectify_onhold': 0,
                # 'digitize_allocated': 0,
                # 'digitize_inprocess': 0,
                # 'digitize_rejected': 0,
                # 'digitize_onhold': 0,
                # 'qc_allocated': 0,
                # 'qc_inprocess': 0,
                # 'qc_rejected': 0,
                # 'qc_onhold': 0,
                # 'pdf_allocated': 0,
                # 'pdf_inprocess': 0,
                # 'pdf_rejected': 0,
                # 'pdf_onhold': 0,
                # 'shape_allocated': 0,
                # 'shape_inprocess': 0,
                # 'shape_rejected': 0,
                # 'shape_onhold': 0,
               
            }


            if User.objects.filter(id=self.request.user.id, user_role__role_name="Super Admin"):
                counts['total_scan_uploaded'] = Document.objects.filter(village_code=village_code).count()
                counts['scan_uploaded'] = Document.objects.filter(village_code=village_code, current_status=1).count()
                counts['rectify_completed'] = Document.objects.filter(village_code=village_code, rectify_completed_date__isnull=False).count()
                counts['digitize_completed'] = Document.objects.filter(village_code=village_code, digitize_completed_date__isnull=False).count()
                counts['qc_completed'] = Document.objects.filter(village_code=village_code, qc_completed_date__isnull=False).count()
                counts['pdf_completed'] = Document.objects.filter(village_code=village_code, pdf_completed_date__isnull=False).count()
                counts['shape_completed'] = Document.objects.filter(village_code=village_code, shape_completed_date__isnull=False).count()
                counts['polygon_count'] = Document.objects.filter(village_code=village_code).aggregate(total_amount=Sum('polygon_count'))['total_amount']

                
                # counts['rectify_allocated'] = Document.objects.filter(village_code=village_code, current_status=3).count()
                # counts['rectify_inprocess'] = Document.objects.filter(village_code=village_code, current_status=4).count()
                # counts['rectify_rejected'] = Document.objects.filter(village_code=village_code, current_status=6).count()
                # counts['rectify_onhold'] = Document.objects.filter(village_code=village_code, current_status=7).count()
                # counts['digitize_allocated'] = Document.objects.filter(village_code=village_code, current_status=8).count()
                # counts['digitize_inprocess'] = Document.objects.filter(village_code=village_code, current_status=9).count()
                # counts['digitize_rejected'] = Document.objects.filter(village_code=village_code, current_status=11).count()
                # counts['digitize_onhold'] = Document.objects.filter(village_code=village_code, current_status=12).count()
                # counts['qc_allocated'] = Document.objects.filter(village_code=village_code, current_status=13).count()
                # counts['qc_inprocess'] = Document.objects.filter(village_code=village_code, current_status=14).count()
                # counts['qc_rejected'] = Document.objects.filter(village_code=village_code, current_status=16).count()
                # counts['qc_onhold'] = Document.objects.filter(village_code=village_code, current_status=17).count()
                # counts['pdf_allocated'] = Document.objects.filter(village_code=village_code, current_status=18).count()
                # counts['pdf_inprocess'] = Document.objects.filter(village_code=village_code, current_status=19).count()
                # counts['pdf_rejected'] = Document.objects.filter(village_code=village_code, current_status=21).count()
                # counts['pdf_onhold'] = Document.objects.filter(village_code=village_code, current_status=22).count()
                # counts['shape_allocated'] = Document.objects.filter(village_code=village_code, current_status=23).count()
                # counts['shape_inprocess'] = Document.objects.filter(village_code=village_code, current_status=26).count()
                # counts['shape_rejected'] = Document.objects.filter(village_code=village_code, current_status=27).count()
                # counts['shape_onhold'] = Document.objects.filter(village_code=village_code, current_status=22).count()
                
            if User.objects.filter(id=self.request.user.id, user_role__role_name="Team Admin"):
                counts['total_scan_uploaded'] = Document.objects.filter(team_id__in=team_ids,village_code=village_code).count()
                counts['scan_uploaded'] = Document.objects.filter(team_id__in=team_ids,village_code=village_code, current_status=1).count()
                counts['rectify_completed'] = Document.objects.filter(team_id__in=team_ids,village_code=village_code, rectify_completed_date__isnull=False).count()
                counts['digitize_completed'] = Document.objects.filter(team_id__in=team_ids,village_code=village_code, digitize_completed_date__isnull=False).count()
                counts['qc_completed'] = Document.objects.filter(team_id__in=team_ids,village_code=village_code, qc_completed_date__isnull=False).count()
                counts['pdf_completed'] = Document.objects.filter(team_id__in=team_ids,village_code=village_code, pdf_completed_date__isnull=False).count()
                counts['shape_completed'] = Document.objects.filter(team_id__in=team_ids,village_code=village_code, shape_completed_date__isnull=False).count()
                counts['polygon_count'] = Document.objects.filter(team_id__in=team_ids,village_code=village_code).aggregate(total_amount=Sum('polygon_count'))['total_amount']
            
                # counts['rectify_allocated'] = Document.objects.filter(team_id__in=team_ids,village_code=village_code, current_status=3).count()
                # counts['rectify_inprocess'] = Document.objects.filter(team_id__in=team_ids,village_code=village_code, current_status=4).count()
                # counts['rectify_rejected'] = Document.objects.filter(team_id__in=team_ids,village_code=village_code, current_status=6).count()
                # counts['rectify_onhold'] = Document.objects.filter(team_id__in=team_ids,village_code=village_code, current_status=7).count()
                # counts['digitize_allocated'] = Document.objects.filter(team_id__in=team_ids,village_code=village_code, current_status=8).count()
                # counts['digitize_inprocess'] = Document.objects.filter(team_id__in=team_ids,village_code=village_code, current_status=9).count()
                # counts['digitize_rejected'] = Document.objects.filter(team_id__in=team_ids,village_code=village_code, current_status=11).count()
                # counts['digitize_onhold'] = Document.objects.filter(team_id__in=team_ids,village_code=village_code, current_status=12).count()
                # counts['qc_allocated'] = Document.objects.filter(team_id__in=team_ids,village_code=village_code, current_status=13).count()
                # counts['qc_inprocess'] = Document.objects.filter(team_id__in=team_ids,village_code=village_code, current_status=14).count()
                # counts['qc_rejected'] = Document.objects.filter(team_id__in=team_ids,village_code=village_code, current_status=16).count()
                # counts['qc_onhold'] = Document.objects.filter(team_id__in=team_ids,village_code=village_code, current_status=17).count()
                # counts['pdf_allocated'] = Document.objects.filter(team_id__in=team_ids,village_code=village_code, current_status=18).count()
                # counts['pdf_inprocess'] = Document.objects.filter(team_id__in=team_ids,village_code=village_code, current_status=19).count()
                # counts['pdf_rejected'] = Document.objects.filter(team_id__in=team_ids,village_code=village_code, current_status=21).count()
                # counts['pdf_onhold'] = Document.objects.filter(team_id__in=team_ids,village_code=village_code, current_status=22).count()
                # counts['shape_allocated'] = Document.objects.filter(team_id__in=team_ids,village_code=village_code, current_status=23).count()
                # counts['shape_inprocess'] = Document.objects.filter(team_id__in=team_ids,village_code=village_code, current_status=26).count()
                # counts['shape_rejected'] = Document.objects.filter(team_id__in=team_ids,village_code=village_code, current_status=27).count()
                # counts['shape_onhold'] = Document.objects.filter(team_id__in=team_ids,village_code=village_code, current_status=22).count()
               
            elif User.objects.filter(id=self.request.user.id, user_role__role_name="Agency Admin"):
                counts['total_scan_uploaded'] = Document.objects.filter(rectify_agency_id__in=agency,village_code=village_code).count()
                counts['scan_uploaded'] = Document.objects.filter(rectify_agency_id__in=agency,village_code=village_code, current_status=1).count()
                counts['rectify_completed'] = Document.objects.filter(rectify_agency_id__in=agency,village_code=village_code,rectify_completed_date__isnull=False).count()
                counts['digitize_completed'] = Document.objects.filter(digitize_agency_id__in=agency,village_code=village_code, digitize_completed_date__isnull=False).count()
                counts['qc_completed'] = Document.objects.filter(qc_agency_id__in=agency,village_code=village_code, qc_completed_date__isnull=False).count()
                counts['pdf_completed'] = Document.objects.filter(qc_agency_id__in=agency,village_code=village_code, pdf_completed_date__isnull=False).count()
                counts['shape_completed'] = Document.objects.filter(qc_agency_id__in=agency,village_code=village_code, shape_completed_date__isnull=False).count()
                counts['polygon_count'] = Document.objects.filter(village_code=village_code).aggregate(total_amount=Sum('polygon_count'))['total_amount']
          
                # counts['rectify_allocated'] = Document.objects.filter(rectify_agency_id__in=agency,village_code=village_code, current_status=3).count()
                # counts['rectify_inprocess'] = Document.objects.filter(rectify_agency_id__in=agency,village_code=village_code, current_status=4).count()
                # counts['rectify_rejected'] = Document.objects.filter(rectify_agency_id__in=agency,village_code=village_code, current_status=6).count()
                # counts['rectify_onhold'] = Document.objects.filter(rectify_agency_id__in=agency,village_code=village_code, current_status=7).count()
                # counts['digitize_allocated'] = Document.objects.filter(digitize_agency_id__in=agency,village_code=village_code, current_status=8).count()
                # counts['digitize_inprocess'] = Document.objects.filter(digitize_agency_id__in=agency,village_code=village_code, current_status=9).count()
                # counts['digitize_rejected'] = Document.objects.filter(digitize_agency_id__in=agency,village_code=village_code, current_status=11).count()
                # counts['digitize_onhold'] = Document.objects.filter(digitize_agency_id__in=agency,village_code=village_code, current_status=12).count()
                # counts['qc_allocated'] = Document.objects.filter(qc_agency_id__in=agency,village_code=village_code, current_status=13).count()
                # counts['qc_inprocess'] = Document.objects.filter(qc_agency_id__in=agency,village_code=village_code, current_status=14).count()
                # counts['qc_rejected'] = Document.objects.filter(qc_agency_id__in=agency,village_code=village_code, current_status=16).count()
                # counts['qc_onhold'] = Document.objects.filter(qc_agency_id__in=agency,village_code=village_code, current_status=17).count()
                # counts['pdf_allocated'] = Document.objects.filter(qc_agency_id__in=agency,village_code=village_code, current_status=18).count()
                # counts['pdf_inprocess'] = Document.objects.filter(qc_agency_id__in=agency,village_code=village_code, current_status=19).count()
                # counts['pdf_rejected'] = Document.objects.filter(qc_agency_id__in=agency,village_code=village_code, current_status=21).count()
                # counts['pdf_onhold'] = Document.objects.filter(qc_agency_id__in=agency,village_code=village_code, current_status=22).count()
                # counts['shape_allocated'] = Document.objects.filter(qc_agency_id__in=agency,village_code=village_code, current_status=23).count()
                # counts['shape_inprocess'] = Document.objects.filter(qc_agency_id__in=agency,village_code=village_code, current_status=26).count()
                # counts['shape_rejected'] = Document.objects.filter(qc_agency_id__in=agency,village_code=village_code, current_status=27).count()
                # counts['shape_onhold'] = Document.objects.filter(qc_agency_id__in=agency,village_code=village_code, current_status=22).count()
                
            counts_by_village.append({
                'village_id': village_id,
                'village_code':village_code,
                'village_name':village_name,
                'taluka_id':taluka_id,
                'taluka_name':taluka_name,
                'district_name':district_name,
                **counts,
            })

        response_data = {
            'counts_by_village': counts_by_village,
            'status': True
        }

        return Response(data=response_data, status=status.HTTP_200_OK)
    
class MapTypeWiseDashboardView(APIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    # This API User Base Count Display
    def get(self, request,taluka_code=None):
        district_name = self.request.query_params.get('district_name', None)
        taluka_name = self.request.query_params.get('taluka_name', None)
        village_name = self.request.query_params.get('village_name', None)
       

        agency = User.objects.filter(id=self.request.user.id).values_list('agency',flat=True)
        team_ids = User.objects.filter(id=self.request.user.id).values_list('agency__team', flat=True)

        if User.objects.filter(id=self.request.user.id, user_role__role_name="Super Admin"):
            maptype = MapType.objects.all().order_by('-date_created')
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Team Admin"):
            maptype = MapType.objects.all().order_by('-date_created')
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Agency Admin"):
            maptype = MapType.objects.all().order_by('-date_created')

        else:
            maptype = []

        # if user_name:
        #     users = users.filter(agency__in=agency,username__icontains=user_name)
        # if dept_name:
        #     users = users.filter(agency__in=agency,department__department_name__icontains=dept_name)
            
        # if agency_name:
        #     users = users.filter(agency__in=agency,agency__agency_name__icontains=agency_name)

        counts_by_maptype = []

        for maptype_obj in maptype:
            maptype_id = maptype_obj.id
            map_code = maptype_obj.map_code
            mapname_english = maptype_obj.mapname_english
            mapname_marathi = maptype_obj.mapname_marathi


            district = None
            taluka = None
            village = None

            if district_name:
                district = District.objects.filter(district_code=district_name).values_list('district_name',flat=True)
            if taluka_name:
                taluka = Taluka.objects.filter(taluka_code=taluka_name).values_list('taluka_name',flat=True)
            if village_name:
                village = Village.objects.filter(village_code=village_name).values_list('village_name',flat=True)
  
            counts = {
                'district_name':district or "",
                'taluka_name' :taluka or "",
                'village_name' : village or "",
                'polygon_count':0,
                'total_scan_uploaded':0,
                'scan_uploaded':0,
                'rectify_allocated': 0,
                'rectify_inprocess': 0,
                'rectify_rejected': 0,
                'rectify_onhold': 0,
                'rectify_completed': 0,
                'digitize_allocated': 0,
                'digitize_inprocess': 0,
                'digitize_rejected': 0,
                'digitize_onhold': 0,
                'digitize_completed': 0,
                'qc_allocated': 0,
                'qc_inprocess': 0,
                'qc_rejected': 0,
                'qc_onhold': 0,
                'qc_completed': 0,
                'pdf_allocated': 0,
                'pdf_inprocess': 0,
                'pdf_rejected': 0,
                'pdf_onhold': 0,
                'pdf_completed': 0,
                'shape_allocated': 0,
                'shape_inprocess': 0,
                'shape_rejected': 0,
                'shape_onhold': 0,
                'shape_completed': 0,
            }
           

            if User.objects.filter(id=self.request.user.id, user_role__role_name="Super Admin"):
                counts['scan_uploaded'] = Document.objects.filter(map_code=map_code, current_status=1).count()
                counts['polygon_count'] = Document.objects.filter(map_code=map_code).aggregate(total_amount=Sum('polygon_count'))['total_amount']
                counts['rectify_allocated'] = Document.objects.filter(map_code=map_code, current_status=3).count()
                counts['rectify_inprocess'] = Document.objects.filter(map_code=map_code, current_status=4).count()
                counts['rectify_rejected'] = Document.objects.filter(map_code=map_code, current_status=6).count()
                counts['rectify_onhold'] = Document.objects.filter(map_code=map_code, current_status=7).count()
                counts['digitize_allocated'] = Document.objects.filter(map_code=map_code, current_status=8).count()
                counts['digitize_inprocess'] = Document.objects.filter(map_code=map_code, current_status=9).count()
                counts['digitize_rejected'] = Document.objects.filter(map_code=map_code, current_status=11).count()
                counts['digitize_onhold'] = Document.objects.filter(map_code=map_code, current_status=12).count()
                
                if (district_name) or (taluka_name) or (village_name):
                    if district_name and not taluka_name:
                        counts['total_scan_uploaded'] = Document.objects.filter(
                            map_code=map_code,
                            district_code=district_name
                        ).count()

                    if district_name and taluka_name and not village_name:
                        counts['total_scan_uploaded'] = Document.objects.filter(
                            map_code=map_code,
                            district_code=district_name,
                            taluka_code=taluka_name
                        ).count()
                    
                    if district_name and taluka_name and village_name:
                        counts['total_scan_uploaded'] = Document.objects.filter(
                            map_code=map_code,
                            district_code=district_name,
                            taluka_code=taluka_name,
                            village_code = village_name
                        ).count()

                    #########################
                    if district_name and not taluka_name:
                        counts['rectify_completed'] = Document.objects.filter(
                            map_code=map_code,
                            district_code=district_name,
                            rectify_completed_date__isnull=False
                        ).count()

                    if district_name and taluka_name and not village_name:
                        counts['rectify_completed'] = Document.objects.filter(
                            map_code=map_code,
                            district_code=district_name,
                            taluka_code=taluka_name,
                            rectify_completed_date__isnull=False
                        ).count()
                    if district_name and taluka_name and village_name:
                        counts['rectify_completed'] = Document.objects.filter(
                            map_code=map_code,
                            district_code=district_name,
                            taluka_code=taluka_name,
                            village_code = village_name,
                            rectify_completed_date__isnull=False
                        ).count()
                    ################################
                    if district_name and not taluka_name:
                        counts['digitize_completed'] = Document.objects.filter(
                            map_code=map_code,
                            district_code=district_name,
                            digitize_completed_date__isnull=False
                        ).count()

                    if district_name and taluka_name and not village_name:
                        counts['digitize_completed'] = Document.objects.filter(
                            map_code=map_code,
                            district_code=district_name,
                            taluka_code=taluka_name,
                            digitize_completed_date__isnull=False
                        ).count()
                    if district_name and taluka_name and village_name:
                        counts['digitize_completed'] = Document.objects.filter(
                            map_code=map_code,
                            district_code=district_name,
                            taluka_code=taluka_name,
                            village_code = village_name,
                            digitize_completed_date__isnull=False
                        ).count()
                    #################################
                    if district_name and not taluka_name:
                        counts['qc_completed'] = Document.objects.filter(
                            map_code=map_code,
                            district_code=district_name,
                            qc_completed_date__isnull=False
                        ).count()

                    if district_name and taluka_name and not village_name:
                        counts['qc_completed'] = Document.objects.filter(
                            map_code=map_code,
                            district_code=district_name,
                            taluka_code=taluka_name,
                            qc_completed_date__isnull=False
                        ).count()
                    if district_name and taluka_name and village_name:
                        counts['qc_completed'] = Document.objects.filter(
                            map_code=map_code,
                            district_code=district_name,
                            taluka_code=taluka_name,
                            village_code = village_name,
                            qc_completed_date__isnull=False
                        ).count()
                    ##################################
                    if district_name and not taluka_name:
                        counts['pdf_completed'] = Document.objects.filter(
                            map_code=map_code,
                            district_code=district_name,
                            pdf_completed_date__isnull=False
                        ).count()

                    if district_name and taluka_name and not village_name:
                        counts['pdf_completed'] = Document.objects.filter(
                            map_code=map_code,
                            district_code=district_name ,
                            taluka_code=taluka_name ,
                            pdf_completed_date__isnull=False
                        ).count()
                    if district_name and taluka_name and village_name:
                        counts['pdf_completed'] = Document.objects.filter(
                            map_code=map_code,
                            district_code=district_name ,
                            taluka_code=taluka_name,
                            village_code = village_name,
                            pdf_completed_date__isnull=False
                        ).count()
                    #########################################
                    if district_name and not taluka_name:
                        counts['shape_completed'] = Document.objects.filter(
                            map_code=map_code,
                            district_code=district_name,
                            shape_completed_date__isnull=False
                        ).count()

                    if district_name and taluka_name and not village_name:
                        counts['shape_completed'] = Document.objects.filter(
                            map_code=map_code,
                            district_code=district_name,
                            taluka_code=taluka_name,
                            shape_completed_date__isnull=False
                        ).count()
                    if district_name and taluka_name and village_name:
                        counts['shape_completed'] = Document.objects.filter(
                            map_code=map_code,
                            district_code=district_name,
                            taluka_code=taluka_name,
                            village_code = village_name,
                            shape_completed_date__isnull=False
                        ).count()
                    ################################################                        
                else:
                    counts['total_scan_uploaded'] = Document.objects.filter(map_code=map_code).count()
                    counts['rectify_completed'] = Document.objects.filter(map_code=map_code, rectify_completed_date__isnull=False).count()
                    counts['digitize_completed'] = Document.objects.filter(map_code=map_code, digitize_completed_date__isnull=False).count()
                    counts['qc_completed'] = Document.objects.filter(map_code=map_code, qc_completed_date__isnull=False).count()
                    counts['pdf_completed'] = Document.objects.filter(map_code=map_code, pdf_completed_date__isnull=False).count()
                    counts['shape_completed'] = Document.objects.filter(map_code=map_code, shape_completed_date__isnull=False).count()


                counts['qc_allocated'] = Document.objects.filter(map_code=map_code, current_status=13).count()
                counts['qc_inprocess'] = Document.objects.filter(map_code=map_code, current_status=14).count()
                counts['qc_rejected'] = Document.objects.filter(map_code=map_code, current_status=16).count()
                counts['qc_onhold'] = Document.objects.filter(map_code=map_code, current_status=17).count()
                counts['pdf_allocated'] = Document.objects.filter(map_code=map_code, current_status=18).count()
                counts['pdf_inprocess'] = Document.objects.filter(map_code=map_code, current_status=19).count()
                counts['pdf_rejected'] = Document.objects.filter(map_code=map_code, current_status=21).count()
                counts['pdf_onhold'] = Document.objects.filter(map_code=map_code, current_status=22).count()
                counts['shape_allocated'] = Document.objects.filter(map_code=map_code, current_status=23).count()
                counts['shape_inprocess'] = Document.objects.filter(map_code=map_code, current_status=26).count()
                counts['shape_rejected'] = Document.objects.filter(map_code=map_code, current_status=27).count()
                counts['shape_onhold'] = Document.objects.filter(map_code=map_code, current_status=22).count()


            elif User.objects.filter(id=self.request.user.id, user_role__role_name="Team Admin"):
                counts['scan_uploaded'] = Document.objects.filter(team_id__in=team_ids,map_code=map_code, current_status=1).count()
                counts['polygon_count'] = Document.objects.filter(team_id__in=team_ids,map_code=map_code).aggregate(total_amount=Sum('polygon_count'))['total_amount']
                
                if (district_name) or (taluka_name) or (village_name):
                    if district_name and not taluka_name:
                        counts['total_scan_uploaded'] = Document.objects.filter(
                            team_id__in=team_ids,
                            map_code=map_code,
                            district_code=district_name,
                        ).count()


                    if district_name and taluka_name and not village_name:
                        counts['total_scan_uploaded'] = Document.objects.filter(
                            team_id__in=team_ids,
                            map_code=map_code,
                            district_code=district_name,
                            taluka_code=taluka_name
                        ).count()

                    
                    if district_name and taluka_name and village_name:
                        counts['total_scan_uploaded'] = Document.objects.filter(
                            team_id__in=team_ids,
                            map_code=map_code,
                            district_code=district_name,
                            taluka_code=taluka_name,
                            village_code = village_name
                        ).count()


                    #########################
                    if district_name and not taluka_name:
                        counts['rectify_completed'] = Document.objects.filter(
                            team_id__in=team_ids,
                            map_code=map_code,
                            district_code=district_name,
                            rectify_completed_date__isnull=False
                        ).count()

                    if district_name and taluka_name and not village_name:
                        counts['rectify_completed'] = Document.objects.filter(
                            team_id__in=team_ids,
                            map_code=map_code,
                            district_code=district_name,
                            taluka_code=taluka_name,
                            rectify_completed_date__isnull=False
                        ).count()
                    if district_name and taluka_name and village_name:
                        counts['rectify_completed'] = Document.objects.filter(
                            team_id__in=team_ids,
                            map_code=map_code,
                            district_code=district_name,
                            taluka_code=taluka_name,
                            village_code = village_name,
                            rectify_completed_date__isnull=False
                        ).count()
                    ################################
                    if district_name and not taluka_name:
                        counts['digitize_completed'] = Document.objects.filter(
                        team_id__in=team_ids,
                        map_code=map_code,
                        district_code=district_name,
                        digitize_completed_date__isnull=False
                    ).count()

                    if district_name and taluka_name and not village_name:
                        counts['digitize_completed'] = Document.objects.filter(
                        team_id__in=team_ids,
                        map_code=map_code,
                        district_code=district_name,
                        taluka_code=taluka_name,
                        digitize_completed_date__isnull=False
                    ).count()
                    if district_name and taluka_name and village_name:
                        counts['digitize_completed'] = Document.objects.filter(
                        team_id__in=team_ids,
                        map_code=map_code,
                        district_code=district_name,
                        taluka_code=taluka_name,
                        village_code = village_name,
                        digitize_completed_date__isnull=False
                    ).count()
                    #################################
                    if district_name and not taluka_name:
                        counts['qc_completed'] = Document.objects.filter(
                        team_id__in=team_ids,
                        map_code=map_code,
                        district_code=district_name,
                        qc_completed_date__isnull=False
                    ).count()

                    if district_name and taluka_name and not village_name:
                        counts['qc_completed'] = Document.objects.filter(
                        team_id__in=team_ids,
                        map_code=map_code,
                        district_code=district_name,
                        taluka_code=taluka_name,
                        qc_completed_date__isnull=False
                    ).count()
                    if district_name and taluka_name and village_name:
                        counts['qc_completed'] = Document.objects.filter(
                        team_id__in=team_ids,
                        map_code=map_code,
                        district_code=district_name,
                        taluka_code=taluka_name,
                        village_code = village_name,
                        qc_completed_date__isnull=False
                    ).count()
                    ##################################
                    if district_name and not taluka_name:
                        counts['pdf_completed'] = Document.objects.filter(
                        team_id__in=team_ids,
                        map_code=map_code,
                        district_code=district_name,
                        pdf_completed_date__isnull=False
                    ).count()

                    if district_name and taluka_name and not village_name:
                        counts['pdf_completed'] = Document.objects.filter(
                        team_id__in=team_ids,
                        map_code=map_code,
                        district_code=district_name,
                        taluka_code=taluka_name,
                        pdf_completed_date__isnull=False
                    ).count()
                    if district_name and taluka_name and village_name:
                        counts['pdf_completed'] = Document.objects.filter(
                        team_id__in=team_ids,
                        map_code=map_code,
                        district_code=district_name,
                        taluka_code=taluka_name,
                        village_code = village_name,
                        pdf_completed_date__isnull=False
                    ).count()
                    #########################################
                    if district_name and not taluka_name:
                        counts['shape_completed'] = Document.objects.filter(
                        team_id__in=team_ids,
                        map_code=map_code,
                        district_code=district_name,
                        shape_completed_date__isnull=False
                    ).count()

                    if district_name and taluka_name and not village_name:
                        counts['shape_completed'] = Document.objects.filter(
                        team_id__in=team_ids,
                        map_code=map_code,
                        district_code=district_name,
                        taluka_code=taluka_name,
                        shape_completed_date__isnull=False
                    ).count()
                    if district_name and taluka_name and village_name:
                        counts['shape_completed'] = Document.objects.filter(
                        team_id__in=team_ids,
                        map_code=map_code,
                        district_code=district_name,
                        taluka_code=taluka_name,
                        village_code = village_name,
                        shape_completed_date__isnull=False
                    ).count()

                else:
                    counts['total_scan_uploaded'] = Document.objects.filter(team_id__in=team_ids,map_code=map_code).count()
                    counts['rectify_completed'] = Document.objects.filter(team_id__in=team_ids,map_code=map_code,rectify_completed_date__isnull=False).count()
                    counts['digitize_completed'] = Document.objects.filter(team_id__in=team_ids,map_code=map_code, digitize_completed_date__isnull=False).count()
                    counts['qc_completed'] = Document.objects.filter(team_id__in=team_ids,map_code=map_code, qc_completed_date__isnull=False).count()
                    counts['pdf_completed'] = Document.objects.filter(team_id__in=team_ids,map_code=map_code, pdf_completed_date__isnull=False).count()
                    counts['shape_completed'] = Document.objects.filter(team_id__in=team_ids,map_code=map_code, shape_completed_date__isnull=False).count()

                counts['rectify_allocated'] = Document.objects.filter(team_id__in=team_ids,map_code=map_code, current_status=3).count()
                counts['rectify_inprocess'] = Document.objects.filter(team_id__in=team_ids,map_code=map_code, current_status=4).count()
                counts['rectify_rejected'] = Document.objects.filter(team_id__in=team_ids,map_code=map_code, current_status=6).count()
                counts['rectify_onhold'] = Document.objects.filter(team_id__in=team_ids,map_code=map_code, current_status=7).count()
                counts['digitize_allocated'] = Document.objects.filter(team_id__in=team_ids,map_code=map_code, current_status=8).count()
                counts['digitize_inprocess'] = Document.objects.filter(team_id__in=team_ids,map_code=map_code, current_status=9).count()
                counts['digitize_rejected'] = Document.objects.filter(team_id__in=team_ids,map_code=map_code, current_status=11).count()
                counts['digitize_onhold'] = Document.objects.filter(team_id__in=team_ids,map_code=map_code, current_status=12).count()
                counts['qc_allocated'] = Document.objects.filter(team_id__in=team_ids,map_code=map_code, current_status=13).count()
                counts['qc_inprocess'] = Document.objects.filter(team_id__in=team_ids,map_code=map_code, current_status=14).count()
                counts['qc_rejected'] = Document.objects.filter(team_id__in=team_ids,map_code=map_code, current_status=16).count()
                counts['qc_onhold'] = Document.objects.filter(team_id__in=team_ids,map_code=map_code, current_status=17).count()
                counts['pdf_allocated'] = Document.objects.filter(team_id__in=team_ids,map_code=map_code, current_status=18).count()
                counts['pdf_inprocess'] = Document.objects.filter(team_id__in=team_ids,map_code=map_code, current_status=19).count()
                counts['pdf_rejected'] = Document.objects.filter(team_id__in=team_ids,map_code=map_code, current_status=21).count()
                counts['pdf_onhold'] = Document.objects.filter(team_id__in=team_ids,map_code=map_code, current_status=22).count()
                counts['shape_allocated'] = Document.objects.filter(team_id__in=team_ids,map_code=map_code, current_status=23).count()
                counts['shape_inprocess'] = Document.objects.filter(team_id__in=team_ids,map_code=map_code, current_status=26).count()
                counts['shape_rejected'] = Document.objects.filter(team_id__in=team_ids,map_code=map_code, current_status=27).count()
                counts['shape_onhold'] = Document.objects.filter(team_id__in=team_ids,map_code=map_code, current_status=22).count()
            
            
            elif User.objects.filter(id=self.request.user.id, user_role__role_name="Agency Admin"):
                counts['scan_uploaded'] = Document.objects.filter(digitize_agency_id__in=agency,map_code=map_code, current_status=1).count()
                counts['polygon_count'] = Document.objects.filter(digitize_agency_id__in=agency,map_code=map_code).aggregate(total_amount=Sum('polygon_count'))['total_amount']
                
                if (district_name) or (taluka_name) or (village_name):
                    if district_name and not taluka_name:
                        counts['total_scan_uploaded'] = Document.objects.filter(
                            digitize_agency_id__in=agency,
                            map_code=map_code,
                            district_code=district_name,
                        ).count()


                    if district_name and taluka_name and not village_name:
                        counts['total_scan_uploaded'] = Document.objects.filter(
                            digitize_agency_id__in=agency,
                            map_code=map_code,
                            district_code=district_name,
                            taluka_code=taluka_name
                        ).count()

                    
                    if district_name and taluka_name and village_name:
                        counts['total_scan_uploaded'] = Document.objects.filter(
                            digitize_agency_id__in=agency,
                            map_code=map_code,
                            district_code=district_name,
                            taluka_code=taluka_name,
                            village_code = village_name
                        ).count()


                    #########################
                    if district_name and not taluka_name:
                        counts['rectify_completed'] = Document.objects.filter(
                            rectify_agency_id__in=agency,
                            map_code=map_code,
                            district_code=district_name,
                            rectify_completed_date__isnull=False
                        ).count()

                    if district_name and taluka_name and not village_name:
                        counts['rectify_completed'] = Document.objects.filter(
                            rectify_agency_id__in=agency,
                            map_code=map_code,
                            district_code=district_name,
                            taluka_code=taluka_name,
                            rectify_completed_date__isnull=False
                        ).count()
                    if district_name and taluka_name and village_name:
                        counts['rectify_completed'] = Document.objects.filter(
                            rectify_agency_id__in=agency,
                            map_code=map_code,
                            district_code=district_name,
                            taluka_code=taluka_name,
                            village_code = village_name,
                            rectify_completed_date__isnull=False
                        ).count()
                    ################################
                    if district_name and not taluka_name:
                        counts['digitize_completed'] = Document.objects.filter(
                        digitize_agency_id__in=agency,
                        map_code=map_code,
                        district_code=district_name,
                        digitize_completed_date__isnull=False
                    ).count()

                    if district_name and taluka_name and not village_name:
                        counts['digitize_completed'] = Document.objects.filter(
                        digitize_agency_id__in=agency,
                        map_code=map_code,
                        district_code=district_name,
                        taluka_code=taluka_name,
                        digitize_completed_date__isnull=False
                    ).count()
                    if district_name and taluka_name and village_name:
                        counts['digitize_completed'] = Document.objects.filter(
                        digitize_agency_id__in=agency,
                        map_code=map_code,
                        district_code=district_name,
                        taluka_code=taluka_name,
                        village_code = village_name,
                        digitize_completed_date__isnull=False
                    ).count()
                    #################################
                    if district_name and not taluka_name:
                        counts['qc_completed'] = Document.objects.filter(
                        qc_agency_id__in=agency,
                        map_code=map_code,
                        district_code=district_name,
                        qc_completed_date__isnull=False
                    ).count()

                    if district_name and taluka_name and not village_name:
                        counts['qc_completed'] = Document.objects.filter(
                        qc_agency_id__in=agency,
                        map_code=map_code,
                        district_code=district_name,
                        taluka_code=taluka_name,
                        qc_completed_date__isnull=False
                    ).count()
                    if district_name and taluka_name and village_name:
                        counts['qc_completed'] = Document.objects.filter(
                        qc_agency_id__in=agency,
                        map_code=map_code,
                        district_code=district_name,
                        taluka_code=taluka_name,
                        village_code = village_name,
                        qc_completed_date__isnull=False
                    ).count()
                    ##################################
                    if district_name and not taluka_name:
                        counts['pdf_completed'] = Document.objects.filter(
                        qc_agency_id__in=agency,
                        map_code=map_code,
                        district_code=district_name,
                        pdf_completed_date__isnull=False
                    ).count()

                    if district_name and taluka_name and not village_name:
                        counts['pdf_completed'] = Document.objects.filter(
                        qc_agency_id__in=agency,
                        map_code=map_code,
                        district_code=district_name,
                        taluka_code=taluka_name,
                        pdf_completed_date__isnull=False
                    ).count()
                    if district_name and taluka_name and village_name:
                        counts['pdf_completed'] = Document.objects.filter(
                        qc_agency_id__in=agency,
                        map_code=map_code,
                        district_code=district_name,
                        taluka_code=taluka_name,
                        village_code = village_name,
                        pdf_completed_date__isnull=False
                    ).count()
                    #########################################
                    if district_name and not taluka_name:
                        counts['shape_completed'] = Document.objects.filter(
                        qc_agency_id__in=agency,
                        map_code=map_code,
                        district_code=district_name,
                        shape_completed_date__isnull=False
                    ).count()

                    if district_name and taluka_name and not village_name:
                        counts['shape_completed'] = Document.objects.filter(
                        qc_agency_id__in=agency,
                        map_code=map_code,
                        district_code=district_name,
                        taluka_code=taluka_name,
                        shape_completed_date__isnull=False
                    ).count()
                    if district_name and taluka_name and village_name:
                        counts['shape_completed'] = Document.objects.filter(
                        qc_agency_id__in=agency,
                        map_code=map_code,
                        district_code=district_name,
                        taluka_code=taluka_name,
                        village_code = village_name,
                        shape_completed_date__isnull=False
                    ).count()

                else:
                    counts['total_scan_uploaded'] = Document.objects.filter(digitize_agency_id__in=agency,map_code=map_code).count()
                    counts['rectify_completed'] = Document.objects.filter(rectify_agency_id__in=agency,map_code=map_code,rectify_completed_date__isnull=False).count()
                    counts['digitize_completed'] = Document.objects.filter(digitize_agency_id__in=agency,map_code=map_code, digitize_completed_date__isnull=False).count()
                    counts['qc_completed'] = Document.objects.filter(qc_agency_id__in=agency,map_code=map_code, qc_completed_date__isnull=False).count()
                    counts['pdf_completed'] = Document.objects.filter(qc_agency_id__in=agency,map_code=map_code, pdf_completed_date__isnull=False).count()
                    counts['shape_completed'] = Document.objects.filter(qc_agency_id__in=agency,map_code=map_code, shape_completed_date__isnull=False).count()

                counts['rectify_allocated'] = Document.objects.filter(rectify_agency_id__in=agency,map_code=map_code, current_status=3).count()
                counts['rectify_inprocess'] = Document.objects.filter(rectify_agency_id__in=agency,map_code=map_code, current_status=4).count()
                counts['rectify_rejected'] = Document.objects.filter(rectify_agency_id__in=agency,map_code=map_code, current_status=6).count()
                counts['rectify_onhold'] = Document.objects.filter(rectify_agency_id__in=agency,map_code=map_code, current_status=7).count()
                counts['digitize_allocated'] = Document.objects.filter(digitize_agency_id__in=agency,map_code=map_code, current_status=8).count()
                counts['digitize_inprocess'] = Document.objects.filter(digitize_agency_id__in=agency,map_code=map_code, current_status=9).count()
                counts['digitize_rejected'] = Document.objects.filter(digitize_agency_id__in=agency,map_code=map_code, current_status=11).count()
                counts['digitize_onhold'] = Document.objects.filter(digitize_agency_id__in=agency,map_code=map_code, current_status=12).count()
                counts['qc_allocated'] = Document.objects.filter(qc_agency_id__in=agency,map_code=map_code, current_status=13).count()
                counts['qc_inprocess'] = Document.objects.filter(qc_agency_id__in=agency,map_code=map_code, current_status=14).count()
                counts['qc_rejected'] = Document.objects.filter(qc_agency_id__in=agency,map_code=map_code, current_status=16).count()
                counts['qc_onhold'] = Document.objects.filter(qc_agency_id__in=agency,map_code=map_code, current_status=17).count()
                counts['pdf_allocated'] = Document.objects.filter(qc_agency_id__in=agency,map_code=map_code, current_status=18).count()
                counts['pdf_inprocess'] = Document.objects.filter(qc_agency_id__in=agency,map_code=map_code, current_status=19).count()
                counts['pdf_rejected'] = Document.objects.filter(qc_agency_id__in=agency,map_code=map_code, current_status=21).count()
                counts['pdf_onhold'] = Document.objects.filter(qc_agency_id__in=agency,map_code=map_code, current_status=22).count()
                counts['shape_allocated'] = Document.objects.filter(qc_agency_id__in=agency,map_code=map_code, current_status=23).count()
                counts['shape_inprocess'] = Document.objects.filter(qc_agency_id__in=agency,map_code=map_code, current_status=26).count()
                counts['shape_rejected'] = Document.objects.filter(qc_agency_id__in=agency,map_code=map_code, current_status=27).count()
                counts['shape_onhold'] = Document.objects.filter(qc_agency_id__in=agency,map_code=map_code, current_status=22).count()
            
          


            counts_by_maptype.append({
                'maptype_id': maptype_id,
                'map_code':map_code,
                'mapname_english':mapname_english,
                'mapname_marathi':mapname_marathi,
                **counts,
            })

        response_data = {
            'counts_by_maptype': counts_by_maptype,
            'status': True
        }

        return Response(data=response_data, status=status.HTTP_200_OK)
    


class VillageWiseMapTypeDashboardView(APIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    # This API User Base Count Display
    def get(self, request,village_code=None):
       
        agency = User.objects.filter(id=self.request.user.id).values_list('agency',flat=True)
        team_ids = User.objects.filter(id=self.request.user.id).values_list('agency__team', flat=True)

        if User.objects.filter(id=self.request.user.id, user_role__role_name="Super Admin"):
            doc_village_code = Document.objects.filter(village_code=village_code).values_list('map_code', flat=True).distinct()
            maptype = MapType.objects.filter(map_code__in=doc_village_code).order_by('-date_created')

        elif User.objects.filter(id=self.request.user.id,user_role__role_name="Team Admin"):
            doc_village_code = Document.objects.filter(team_id__in=team_ids,village_code=village_code).values_list('map_code',flat=True).distinct()
            maptype = MapType.objects.filter(map_code__in=doc_village_code).order_by('-date_created')
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Agency Admin"):
            doc_village_code = Document.objects.filter(digitize_agency_id__in=agency,village_code=village_code).values_list('map_code', flat=True).distinct()
            maptype = MapType.objects.filter(map_code__in=doc_village_code).order_by('-date_created')

        else:
            maptype = []


        counts_by_maptype = []

        for maptype_obj in maptype:
            maptype_id = maptype_obj.id
            map_code = maptype_obj.map_code
            mapname_english = maptype_obj.mapname_english
            mapname_marathi = maptype_obj.mapname_marathi
           
  
            counts = {
                'polygon_count':0,
                'total_scan_uploaded':0,
                'scan_uploaded':0,
                'rectify_allocated': 0,
                'rectify_inprocess': 0,
                'rectify_rejected': 0,
                'rectify_onhold': 0,
                'rectify_completed': 0,
                'digitize_allocated': 0,
                'digitize_inprocess': 0,
                'digitize_rejected': 0,
                'digitize_onhold': 0,
                'digitize_completed': 0,
                'qc_allocated': 0,
                'qc_inprocess': 0,
                'qc_rejected': 0,
                'qc_onhold': 0,
                'qc_completed': 0,
                'pdf_allocated': 0,
                'pdf_inprocess': 0,
                'pdf_rejected': 0,
                'pdf_onhold': 0,
                'pdf_completed': 0,
                'shape_allocated': 0,
                'shape_inprocess': 0,
                'shape_rejected': 0,
                'shape_onhold': 0,
                'shape_completed': 0,
            }
           

            if User.objects.filter(id=self.request.user.id, user_role__role_name="Super Admin"):
                counts['total_scan_uploaded'] = Document.objects.filter(map_code=map_code,village_code=village_code).count()
                counts['scan_uploaded'] = Document.objects.filter(map_code=map_code,village_code=village_code, current_status=1).count()
                counts['polygon_count'] = Document.objects.filter(map_code=map_code,village_code=village_code).aggregate(total_amount=Sum('polygon_count'))['total_amount']
                counts['rectify_allocated'] = Document.objects.filter(map_code=map_code,village_code=village_code, current_status=3).count()
                counts['rectify_inprocess'] = Document.objects.filter(map_code=map_code,village_code=village_code, current_status=4).count()
                counts['rectify_rejected'] = Document.objects.filter(map_code=map_code,village_code=village_code, current_status=6).count()
                counts['rectify_onhold'] = Document.objects.filter(map_code=map_code,village_code=village_code, current_status=7).count()
                counts['digitize_allocated'] = Document.objects.filter(map_code=map_code,village_code=village_code, current_status=8).count()
                counts['digitize_inprocess'] = Document.objects.filter(map_code=map_code,village_code=village_code, current_status=9).count()
                counts['digitize_rejected'] = Document.objects.filter(map_code=map_code,village_code=village_code, current_status=11).count()
                counts['digitize_onhold'] = Document.objects.filter(map_code=map_code,village_code=village_code, current_status=12).count()

                
                counts['rectify_completed'] = Document.objects.filter(map_code=map_code,village_code=village_code, rectify_completed_date__isnull=False).count()
                counts['digitize_completed'] = Document.objects.filter(map_code=map_code,village_code=village_code, digitize_completed_date__isnull=False).count()
                counts['qc_completed'] = Document.objects.filter(map_code=map_code,village_code=village_code, qc_completed_date__isnull=False).count()
                counts['pdf_completed'] = Document.objects.filter(map_code=map_code,village_code=village_code, pdf_completed_date__isnull=False).count()
                counts['shape_completed'] = Document.objects.filter(map_code=map_code,village_code=village_code, shape_completed_date__isnull=False).count()


                counts['qc_allocated'] = Document.objects.filter(map_code=map_code,village_code=village_code, current_status=13).count()
                counts['qc_inprocess'] = Document.objects.filter(map_code=map_code,village_code=village_code, current_status=14).count()
                counts['qc_rejected'] = Document.objects.filter(map_code=map_code,village_code=village_code, current_status=16).count()
                counts['qc_onhold'] = Document.objects.filter(map_code=map_code,village_code=village_code, current_status=17).count()
                counts['pdf_allocated'] = Document.objects.filter(map_code=map_code,village_code=village_code, current_status=18).count()
                counts['pdf_inprocess'] = Document.objects.filter(map_code=map_code,village_code=village_code, current_status=19).count()
                counts['pdf_rejected'] = Document.objects.filter(map_code=map_code,village_code=village_code, current_status=21).count()
                counts['pdf_onhold'] = Document.objects.filter(map_code=map_code,village_code=village_code, current_status=22).count()
                counts['shape_allocated'] = Document.objects.filter(map_code=map_code,village_code=village_code, current_status=23).count()
                counts['shape_inprocess'] = Document.objects.filter(map_code=map_code,village_code=village_code, current_status=26).count()
                counts['shape_rejected'] = Document.objects.filter(map_code=map_code,village_code=village_code, current_status=27).count()
                counts['shape_onhold'] = Document.objects.filter(map_code=map_code,village_code=village_code, current_status=22).count()
            
            elif User.objects.filter(id=self.request.user.id, user_role__role_name="Team Admin"):
                counts['total_scan_uploaded'] = Document.objects.filter(team_id__in=team_ids,map_code=map_code,village_code=village_code).count()
                counts['scan_uploaded'] = Document.objects.filter(team_id__in=team_ids,map_code=map_code,village_code=village_code, current_status=1).count()
                counts['polygon_count'] = Document.objects.filter(team_id__in=team_ids,map_code=map_code,village_code=village_code).aggregate(total_amount=Sum('polygon_count'))['total_amount']
                
                
                counts['rectify_completed'] = Document.objects.filter(team_id__in=team_ids,map_code=map_code,village_code=village_code,rectify_completed_date__isnull=False).count()
                counts['digitize_completed'] = Document.objects.filter(team_id__in=team_ids,map_code=map_code,village_code=village_code, digitize_completed_date__isnull=False).count()
                counts['qc_completed'] = Document.objects.filter(team_id__in=team_ids,map_code=map_code,village_code=village_code, qc_completed_date__isnull=False).count()
                counts['pdf_completed'] = Document.objects.filter(team_id__in=team_ids,map_code=map_code,village_code=village_code, pdf_completed_date__isnull=False).count()
                counts['shape_completed'] = Document.objects.filter(team_id__in=team_ids,map_code=map_code,village_code=village_code, shape_completed_date__isnull=False).count()

                counts['rectify_allocated'] = Document.objects.filter(team_id__in=team_ids,map_code=map_code,village_code=village_code, current_status=3).count()
                counts['rectify_inprocess'] = Document.objects.filter(team_id__in=team_ids,map_code=map_code,village_code=village_code, current_status=4).count()
                counts['rectify_rejected'] = Document.objects.filter(team_id__in=team_ids,map_code=map_code,village_code=village_code, current_status=6).count()
                counts['rectify_onhold'] = Document.objects.filter(team_id__in=team_ids,map_code=map_code,village_code=village_code, current_status=7).count()
                counts['digitize_allocated'] = Document.objects.filter(team_id__in=team_ids,map_code=map_code,village_code=village_code, current_status=8).count()
                counts['digitize_inprocess'] = Document.objects.filter(team_id__in=team_ids,map_code=map_code,village_code=village_code, current_status=9).count()
                counts['digitize_rejected'] = Document.objects.filter(team_id__in=team_ids,map_code=map_code,village_code=village_code, current_status=11).count()
                counts['digitize_onhold'] = Document.objects.filter(team_id__in=team_ids,map_code=map_code,village_code=village_code, current_status=12).count()
                counts['qc_allocated'] = Document.objects.filter(team_id__in=team_ids,map_code=map_code,village_code=village_code, current_status=13).count()
                counts['qc_inprocess'] = Document.objects.filter(team_id__in=team_ids,map_code=map_code,village_code=village_code, current_status=14).count()
                counts['qc_rejected'] = Document.objects.filter(team_id__in=team_ids,map_code=map_code,village_code=village_code, current_status=16).count()
                counts['qc_onhold'] = Document.objects.filter(team_id__in=team_ids,map_code=map_code,village_code=village_code, current_status=17).count()
                counts['pdf_allocated'] = Document.objects.filter(team_id__in=team_ids,map_code=map_code,village_code=village_code, current_status=18).count()
                counts['pdf_inprocess'] = Document.objects.filter(team_id__in=team_ids,map_code=map_code,village_code=village_code, current_status=19).count()
                counts['pdf_rejected'] = Document.objects.filter(team_id__in=team_ids,map_code=map_code,village_code=village_code, current_status=21).count()
                counts['pdf_onhold'] = Document.objects.filter(team_id__in=team_ids,map_code=map_code,village_code=village_code, current_status=22).count()
                counts['shape_allocated'] = Document.objects.filter(team_id__in=team_ids,map_code=map_code,village_code=village_code, current_status=23).count()
                counts['shape_inprocess'] = Document.objects.filter(team_id__in=team_ids,map_code=map_code,village_code=village_code, current_status=26).count()
                counts['shape_rejected'] = Document.objects.filter(team_id__in=team_ids,map_code=map_code,village_code=village_code, current_status=27).count()
                counts['shape_onhold'] = Document.objects.filter(team_id__in=team_ids,map_code=map_code,village_code=village_code, current_status=22).count()
            
          

            
            elif User.objects.filter(id=self.request.user.id, user_role__role_name="Agency Admin"):
                counts['total_scan_uploaded'] = Document.objects.filter(rectify_agency_id__in=agency,map_code=map_code,village_code=village_code).count()
                counts['scan_uploaded'] = Document.objects.filter(rectify_agency_id__in=agency,map_code=map_code,village_code=village_code, current_status=1).count()
                counts['polygon_count'] = Document.objects.filter(rectify_agency_id__in=agency,map_code=map_code,village_code=village_code).aggregate(total_amount=Sum('polygon_count'))['total_amount']
                
                
                counts['rectify_completed'] = Document.objects.filter(rectify_agency_id__in=agency,map_code=map_code,village_code=village_code,rectify_completed_date__isnull=False).count()
                counts['digitize_completed'] = Document.objects.filter(digitize_agency_id__in=agency,map_code=map_code,village_code=village_code, digitize_completed_date__isnull=False).count()
                counts['qc_completed'] = Document.objects.filter(qc_agency_id__in=agency,map_code=map_code,village_code=village_code, qc_completed_date__isnull=False).count()
                counts['pdf_completed'] = Document.objects.filter(qc_agency_id__in=agency,map_code=map_code,village_code=village_code, pdf_completed_date__isnull=False).count()
                counts['shape_completed'] = Document.objects.filter(qc_agency_id__in=agency,map_code=map_code,village_code=village_code, shape_completed_date__isnull=False).count()

                counts['rectify_allocated'] = Document.objects.filter(rectify_agency_id__in=agency,map_code=map_code,village_code=village_code, current_status=3).count()
                counts['rectify_inprocess'] = Document.objects.filter(rectify_agency_id__in=agency,map_code=map_code,village_code=village_code, current_status=4).count()
                counts['rectify_rejected'] = Document.objects.filter(rectify_agency_id__in=agency,map_code=map_code,village_code=village_code, current_status=6).count()
                counts['rectify_onhold'] = Document.objects.filter(rectify_agency_id__in=agency,map_code=map_code,village_code=village_code, current_status=7).count()
                counts['digitize_allocated'] = Document.objects.filter(digitize_agency_id__in=agency,map_code=map_code,village_code=village_code, current_status=8).count()
                counts['digitize_inprocess'] = Document.objects.filter(digitize_agency_id__in=agency,map_code=map_code,village_code=village_code, current_status=9).count()
                counts['digitize_rejected'] = Document.objects.filter(digitize_agency_id__in=agency,map_code=map_code,village_code=village_code, current_status=11).count()
                counts['digitize_onhold'] = Document.objects.filter(digitize_agency_id__in=agency,map_code=map_code,village_code=village_code, current_status=12).count()
                counts['qc_allocated'] = Document.objects.filter(qc_agency_id__in=agency,map_code=map_code,village_code=village_code, current_status=13).count()
                counts['qc_inprocess'] = Document.objects.filter(qc_agency_id__in=agency,map_code=map_code,village_code=village_code, current_status=14).count()
                counts['qc_rejected'] = Document.objects.filter(qc_agency_id__in=agency,map_code=map_code,village_code=village_code, current_status=16).count()
                counts['qc_onhold'] = Document.objects.filter(qc_agency_id__in=agency,map_code=map_code,village_code=village_code, current_status=17).count()
                counts['pdf_allocated'] = Document.objects.filter(qc_agency_id__in=agency,map_code=map_code,village_code=village_code, current_status=18).count()
                counts['pdf_inprocess'] = Document.objects.filter(qc_agency_id__in=agency,map_code=map_code,village_code=village_code, current_status=19).count()
                counts['pdf_rejected'] = Document.objects.filter(qc_agency_id__in=agency,map_code=map_code,village_code=village_code, current_status=21).count()
                counts['pdf_onhold'] = Document.objects.filter(qc_agency_id__in=agency,map_code=map_code,village_code=village_code, current_status=22).count()
                counts['shape_allocated'] = Document.objects.filter(qc_agency_id__in=agency,map_code=map_code,village_code=village_code, current_status=23).count()
                counts['shape_inprocess'] = Document.objects.filter(qc_agency_id__in=agency,map_code=map_code,village_code=village_code, current_status=26).count()
                counts['shape_rejected'] = Document.objects.filter(qc_agency_id__in=agency,map_code=map_code,village_code=village_code, current_status=27).count()
                counts['shape_onhold'] = Document.objects.filter(qc_agency_id__in=agency,map_code=map_code,village_code=village_code, current_status=22).count()
            
          


            counts_by_maptype.append({
                'maptype_id': maptype_id,
                'map_code':map_code,
                'mapname_english':mapname_english,
                'mapname_marathi':mapname_marathi,
                **counts,
            })

        response_data = {
            'counts_by_maptype': counts_by_maptype,
            'status': True
        }

        return Response(data=response_data, status=status.HTTP_200_OK)
    

class AgencyWiseWiseDashboardView(APIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    # This API User Base Count Display
    def get(self, request):
        
        
        agency = User.objects.filter(id=self.request.user.id).values_list('agency',flat=True)
        team_ids = User.objects.filter(id=self.request.user.id).values_list('agency__team', flat=True)

        start_date = self.request.query_params.get('start_date',None)
        end_date = self.request.query_params.get('end_date',None)


        if User.objects.filter(id=self.request.user.id, user_role__role_name="Super Admin"):
            agency_list = Agency.objects.all().order_by('-date_created')
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Team Admin"):
            agency_list = Agency.objects.filter(team__id=team_ids).order_by('-date_created')
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Agency Admin"):
            agency_list = Agency.objects.filter(id__in=agency).order_by('-date_created')

        else:
            agency_list = []

        counts_by_agency = []

        if start_date and end_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
            end_date = datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)

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
                counts['total_scan_uploaded'] = Document.objects.filter(rectify_agency_id=agency_id).count()

                if start_date and end_date:
                    counts['scan_uploaded'] = Document.objects.filter(rectify_agency_id=agency_id, current_status=1,
                                                scan_uploaded_date__gte=start_date.date(),
                                                scan_uploaded_date__lt=(end_date.date() + timedelta(days=1))
                                                ).count()
                    

                    counts['polygon_count'] = Document.objects.filter(rectify_agency_id=agency_id,
                                                rectify_completed_date__isnull=False,
                                                rectify_completed_date__gte=start_date.date(),
                                                rectify_completed_date__lt=(end_date.date() + timedelta(days=1))
                                                ).aggregate(total_amount=Sum('polygon_count'))['total_amount']
                    
                    counts['rectify_allocated'] = Document.objects.filter(rectify_agency_id=agency_id, current_status=3,
                                                rectify_assign_date__isnull=False,
                                                rectify_assign_date__gte=start_date.date(),
                                                rectify_assign_date__lt=(end_date.date() + timedelta(days=1))
                                                ).count()
                    
                    counts['digitize_allocated'] = Document.objects.filter(digitize_agency_id=agency_id, current_status=8,
                                                    digitize_assign_date__isnull=False,
                                                    digitize_assign_date__gte=start_date.date(),
                                                    digitize_assign_date__lt=(end_date.date() + timedelta(days=1))
                                                    ).count()
                    
                    counts['rectify_completed'] = Document.objects.filter(rectify_agency_id=agency_id, 
                                                    rectify_completed_date__isnull=False,
                                                    rectify_completed_date__gte=start_date.date(),
                                                    rectify_completed_date__lt=(end_date.date() + timedelta(days=1))

                                                    ).count()
                    
                    counts['digitize_completed'] = Document.objects.filter(digitize_agency_id=agency_id,
                                                    digitize_completed_date__isnull=False,
                                                    digitize_completed_date__gte=start_date.date(),
                                                    digitize_completed_date__lt=(end_date.date() + timedelta(days=1))
                                                    ).count()
                    
                    counts['qc_completed'] = Document.objects.filter(qc_agency_id=agency_id, 
                                                    qc_completed_date__isnull=False,
                                                    qc_completed_date__gte=start_date.date(),
                                                    qc_completed_date__lt=(end_date.date() + timedelta(days=1))
                                                    ).count()
                    
                    counts['pdf_completed'] = Document.objects.filter(qc_agency_id=agency_id,
                                                    pdf_completed_date__isnull=False,
                                                    pdf_completed_date__gte=start_date.date(),
                                                    pdf_completed_date__lt=(end_date.date() + timedelta(days=1))
                                                    ).count()
                    
                    counts['shape_completed'] = Document.objects.filter(qc_agency_id=agency_id,
                                                    shape_completed_date__isnull=False,
                                                    shape_completed_date__gte=start_date.date(),
                                                    shape_completed_date__lt=(end_date.date() + timedelta(days=1))
                                                    ).count()
                    
                    counts['qc_allocated'] = Document.objects.filter(qc_agency_id=agency_id,
                                                current_status=13,
                                                qc_assign_date__gte=start_date.date(),
                                                qc_assign_date__lt=(end_date.date() + timedelta(days=1))
                                                ).count()
                    
                    counts['pdf_allocated'] = Document.objects.filter(qc_agency_id=agency_id, 
                                                current_status=18,
                                                pdf_assign_date__gte=start_date.date(),
                                                pdf_assign_date__lt=(end_date.date() + timedelta(days=1))
                                                ).count()
                    
                    counts['shape_allocated'] = Document.objects.filter(qc_agency_id=agency_id,
                                                current_status=23,
                                                shape_assign_date__gte=start_date.date(),
                                                shape_assign_date__lt=(end_date.date() + timedelta(days=1))
                                                ).count()


                    
                else:
                    counts['scan_uploaded'] = Document.objects.filter(rectify_agency_id=agency_id, current_status=1).count()
                    counts['polygon_count'] = Document.objects.filter(rectify_agency_id=agency_id).aggregate(total_amount=Sum('polygon_count'))['total_amount']
                    counts['rectify_allocated'] = Document.objects.filter(rectify_agency_id=agency_id, current_status=3).count()
                    counts['digitize_allocated'] = Document.objects.filter(map_code=agency_id, current_status=8).count()
                    counts['rectify_completed'] = Document.objects.filter(rectify_agency_id=agency_id, rectify_completed_date__isnull=False).count()
                    counts['digitize_completed'] = Document.objects.filter(digitize_agency_id=agency_id, digitize_completed_date__isnull=False).count()
                    counts['qc_completed'] = Document.objects.filter(qc_agency_id=agency_id, qc_completed_date__isnull=False).count()
                    counts['pdf_completed'] = Document.objects.filter(qc_agency_id=agency_id, pdf_completed_date__isnull=False).count()
                    counts['shape_completed'] = Document.objects.filter(qc_agency_id=agency_id, shape_completed_date__isnull=False).count()
                    counts['qc_allocated'] = Document.objects.filter(qc_agency_id=agency_id, current_status=13).count()
                    counts['pdf_allocated'] = Document.objects.filter(qc_agency_id=agency_id, current_status=18).count()
                    counts['shape_allocated'] = Document.objects.filter(qc_agency_id=agency_id, current_status=23).count()
                

            elif User.objects.filter(id=self.request.user.id, user_role__role_name="Team Admin"):
                counts['total_scan_uploaded'] = Document.objects.filter(rectify_agency_id=agency_id).count()

                if start_date and end_date:
                    counts['scan_uploaded'] = Document.objects.filter(rectify_agency_id=agency_id, current_status=1,
                                                scan_uploaded_date__gte=start_date.date(),
                                                scan_uploaded_date__lt=(end_date.date() + timedelta(days=1))
                                                ).count()
                    

                    counts['polygon_count'] = Document.objects.filter(rectify_agency_id=agency_id,
                                                rectify_completed_date__isnull=False,
                                                rectify_completed_date__gte=start_date.date(),
                                                rectify_completed_date__lt=(end_date.date() + timedelta(days=1))
                                                ).aggregate(total_amount=Sum('polygon_count'))['total_amount']
                    
                    counts['rectify_allocated'] = Document.objects.filter(rectify_agency_id=agency_id, current_status=3,
                                                rectify_assign_date__isnull=False,
                                                rectify_assign_date__gte=start_date.date(),
                                                rectify_assign_date__lt=(end_date.date() + timedelta(days=1))
                                                ).count()
                    
                    counts['digitize_allocated'] = Document.objects.filter(digitize_agency_id=agency_id, current_status=8,
                                                    digitize_assign_date__isnull=False,
                                                    digitize_assign_date__gte=start_date.date(),
                                                    digitize_assign_date__lt=(end_date.date() + timedelta(days=1))
                                                    ).count()
                    
                    counts['rectify_completed'] = Document.objects.filter(rectify_agency_id=agency_id, 
                                                    rectify_completed_date__isnull=False,
                                                    rectify_completed_date__gte=start_date.date(),
                                                    rectify_completed_date__lt=(end_date.date() + timedelta(days=1))

                                                    ).count()
                    
                    counts['digitize_completed'] = Document.objects.filter(digitize_agency_id=agency_id,
                                                    digitize_completed_date__isnull=False,
                                                    digitize_completed_date__gte=start_date.date(),
                                                    digitize_completed_date__lt=(end_date.date() + timedelta(days=1))
                                                    ).count()
                    
                    counts['qc_completed'] = Document.objects.filter(qc_agency_id=agency_id, 
                                                    qc_completed_date__isnull=False,
                                                    qc_completed_date__gte=start_date.date(),
                                                    qc_completed_date__lt=(end_date.date() + timedelta(days=1))
                                                    ).count()
                    
                    counts['pdf_completed'] = Document.objects.filter(qc_agency_id=agency_id,
                                                    pdf_completed_date__isnull=False,
                                                    pdf_completed_date__gte=start_date.date(),
                                                    pdf_completed_date__lt=(end_date.date() + timedelta(days=1))
                                                    ).count()
                    
                    counts['shape_completed'] = Document.objects.filter(qc_agency_id=agency_id,
                                                    shape_completed_date__isnull=False,
                                                    shape_completed_date__gte=start_date.date(),
                                                    shape_completed_date__lt=(end_date.date() + timedelta(days=1))
                                                    ).count()
                    
                    counts['qc_allocated'] = Document.objects.filter(qc_agency_id=agency_id,
                                                current_status=13,
                                                qc_assign_date__gte=start_date.date(),
                                                qc_assign_date__lt=(end_date.date() + timedelta(days=1))
                                                ).count()
                    
                    counts['pdf_allocated'] = Document.objects.filter(qc_agency_id=agency_id, 
                                                current_status=18,
                                                pdf_assign_date__gte=start_date.date(),
                                                pdf_assign_date__lt=(end_date.date() + timedelta(days=1))
                                                ).count()
                    
                    counts['shape_allocated'] = Document.objects.filter(qc_agency_id=agency_id,
                                                current_status=23,
                                                shape_assign_date__gte=start_date.date(),
                                                shape_assign_date__lt=(end_date.date() + timedelta(days=1))
                                                ).count()
                else:

                    counts['scan_uploaded'] = Document.objects.filter(rectify_agency_id=agency_id, current_status=1).count()
                    counts['polygon_count'] = Document.objects.filter(digitize_agency_id=agency_id).aggregate(total_amount=Sum('polygon_count'))['total_amount']
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
            
        

            
            elif User.objects.filter(id=self.request.user.id, user_role__role_name="Agency Admin"):
                counts['total_scan_uploaded'] = Document.objects.filter(rectify_agency_id=agency_id).count()

                if start_date and end_date:
                    counts['scan_uploaded'] = Document.objects.filter(rectify_agency_id=agency_id, current_status=1,
                                                scan_uploaded_date__gte=start_date.date(),
                                                scan_uploaded_date__lt=(end_date.date() + timedelta(days=1))
                                                ).count()
                    

                    counts['polygon_count'] = Document.objects.filter(rectify_agency_id=agency_id,
                                                rectify_completed_date__isnull=False,
                                                rectify_completed_date__gte=start_date.date(),
                                                rectify_completed_date__lt=(end_date.date() + timedelta(days=1))
                                                ).aggregate(total_amount=Sum('polygon_count'))['total_amount']
                    
                    counts['rectify_allocated'] = Document.objects.filter(rectify_agency_id=agency_id, current_status=3,
                                                rectify_assign_date__isnull=False,
                                                rectify_assign_date__gte=start_date.date(),
                                                rectify_assign_date__lt=(end_date.date() + timedelta(days=1))
                                                ).count()
                    
                    counts['digitize_allocated'] = Document.objects.filter(digitize_agency_id=agency_id, current_status=8,
                                                    digitize_assign_date__isnull=False,
                                                    digitize_assign_date__gte=start_date.date(),
                                                    digitize_assign_date__lt=(end_date.date() + timedelta(days=1))
                                                    ).count()
                    
                    counts['rectify_completed'] = Document.objects.filter(rectify_agency_id=agency_id, 
                                                    rectify_completed_date__isnull=False,
                                                    rectify_completed_date__gte=start_date.date(),
                                                    rectify_completed_date__lt=(end_date.date() + timedelta(days=1))

                                                    ).count()
                    
                    counts['digitize_completed'] = Document.objects.filter(digitize_agency_id=agency_id,
                                                    digitize_completed_date__isnull=False,
                                                    digitize_completed_date__gte=start_date.date(),
                                                    digitize_completed_date__lt=(end_date.date() + timedelta(days=1))
                                                    ).count()
                    
                    counts['qc_completed'] = Document.objects.filter(qc_agency_id=agency_id, 
                                                    qc_completed_date__isnull=False,
                                                    qc_completed_date__gte=start_date.date(),
                                                    qc_completed_date__lt=(end_date.date() + timedelta(days=1))
                                                    ).count()
                    
                    counts['pdf_completed'] = Document.objects.filter(qc_agency_id=agency_id,
                                                    pdf_completed_date__isnull=False,
                                                    pdf_completed_date__gte=start_date.date(),
                                                    pdf_completed_date__lt=(end_date.date() + timedelta(days=1))
                                                    ).count()
                    
                    counts['shape_completed'] = Document.objects.filter(qc_agency_id=agency_id,
                                                    shape_completed_date__isnull=False,
                                                    shape_completed_date__gte=start_date.date(),
                                                    shape_completed_date__lt=(end_date.date() + timedelta(days=1))
                                                    ).count()
                    
                    counts['qc_allocated'] = Document.objects.filter(qc_agency_id=agency_id,
                                                current_status=13,
                                                qc_assign_date__gte=start_date.date(),
                                                qc_assign_date__lt=(end_date.date() + timedelta(days=1))
                                                ).count()
                    
                    counts['pdf_allocated'] = Document.objects.filter(qc_agency_id=agency_id, 
                                                current_status=18,
                                                pdf_assign_date__gte=start_date.date(),
                                                pdf_assign_date__lt=(end_date.date() + timedelta(days=1))
                                                ).count()
                    
                    counts['shape_allocated'] = Document.objects.filter(qc_agency_id=agency_id,
                                                current_status=23,
                                                shape_assign_date__gte=start_date.date(),
                                                shape_assign_date__lt=(end_date.date() + timedelta(days=1))
                                                ).count()
                else:

                    counts['scan_uploaded'] = Document.objects.filter(rectify_agency_id=agency_id, current_status=1).count()
                    counts['polygon_count'] = Document.objects.filter(digitize_agency_id=agency_id).aggregate(total_amount=Sum('polygon_count'))['total_amount']
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
    

class TodayMapTypeWiseDocView(APIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    # This API User Base Count Display
    def get(self, request,taluka_code=None):
        agency = User.objects.filter(id=self.request.user.id).values_list('agency',flat=True)
        team_ids = User.objects.filter(id=self.request.user.id).values_list('agency__team', flat=True)


        if User.objects.filter(id=self.request.user.id, user_role__role_name="Super Admin"):
            maptype = MapType.objects.all().order_by('-date_created')
        elif User.objects.filter(id=self.request.user.id, user_role__role_name="Agency Admin"):
            maptype = MapType.objects.all().order_by('-date_created')

        else:
            maptype = []

        counts_by_maptype = []

        for maptype_obj in maptype:
            maptype_id = maptype_obj.id
            map_code = maptype_obj.map_code
            mapname_english = maptype_obj.mapname_english
            mapname_marathi = maptype_obj.mapname_marathi

            counts = {
                
                'digitize_polygon_count':0,
                'qc_polygon_count':0,
                'scan_uploaded':0,
                'rectify_completed': 0,
                'digitize_completed': 0,
                'qc_completed': 0,
                'pdf_completed': 0,
                'shape_completed': 0,
            }
           
            today = datetime.now().date()
            if User.objects.filter(id=self.request.user.id, user_role__role_name="Super Admin"):
                counts['scan_uploaded'] = Document.objects.filter(map_code=map_code, current_status=1,scan_uploaded_date__date=today).count()
               
               
              
                counts['digitize_polygon_count'] = Document.objects.filter(map_code=map_code,digitize_completed_date__date=today).aggregate(total_amount=Sum('polygon_count'))['total_amount'] or 0
                counts['qc_polygon_count'] = Document.objects.filter(map_code=map_code,qc_completed_date__date=today).aggregate(total_amount=Sum('qc_polygon_count'))['total_amount'] or 0
                counts['rectify_completed'] = Document.objects.filter(map_code=map_code, rectify_completed_date__isnull=False,rectify_completed_date__date=today).count()
                counts['digitize_completed'] = Document.objects.filter(map_code=map_code, digitize_completed_date__isnull=False,digitize_completed_date__date=today).count()
                counts['qc_completed'] = Document.objects.filter(map_code=map_code, qc_completed_date__isnull=False,qc_completed_date__date=today).count()
                counts['pdf_completed'] = Document.objects.filter(map_code=map_code, pdf_completed_date__isnull=False,pdf_completed_date__date=today).count()
                counts['shape_completed'] = Document.objects.filter(map_code=map_code, shape_completed_date__isnull=False,shape_completed_date__date=today).count()


            elif User.objects.filter(id=self.request.user.id, user_role__role_name="Team Admin"):
                counts['scan_uploaded'] = Document.objects.filter(team_id__in=team_ids,map_code=map_code, current_status=1,scan_uploaded_date__date=today).count()
               
               
              
                counts['digitize_polygon_count'] = Document.objects.filter(team_id__in=team_ids,map_code=map_code,digitize_completed_date__date=today).aggregate(total_amount=Sum('polygon_count'))['total_amount'] or 0
                counts['qc_polygon_count'] = Document.objects.filter(team_id__in=team_ids,map_code=map_code,qc_completed_date__date=today).aggregate(total_amount=Sum('qc_polygon_count'))['total_amount'] or 0
                counts['rectify_completed'] = Document.objects.filter(team_id__in=team_ids,map_code=map_code, rectify_completed_date__isnull=False,rectify_completed_date__date=today).count()
                counts['digitize_completed'] = Document.objects.filter(team_id__in=team_ids,map_code=map_code, digitize_completed_date__isnull=False,digitize_completed_date__date=today).count()
                counts['qc_completed'] = Document.objects.filter(team_id__in=team_ids,map_code=map_code, qc_completed_date__isnull=False,qc_completed_date__date=today).count()
                counts['pdf_completed'] = Document.objects.filter(team_id__in=team_ids,map_code=map_code, pdf_completed_date__isnull=False,pdf_completed_date__date=today).count()
                counts['shape_completed'] = Document.objects.filter(team_id__in=team_ids,map_code=map_code, shape_completed_date__isnull=False,shape_completed_date__date=today).count()


              
            
            elif User.objects.filter(id=self.request.user.id, user_role__role_name="Agency Admin"):
                counts['scan_uploaded'] = Document.objects.filter(digitize_agency_id__in=agency,map_code=map_code, current_status=1,scan_uploaded_date__date=today).count()                
               
                counts['digitize_polygon_count'] = Document.objects.filter(digitize_agency_id__in=agency,map_code=map_code,digitize_completed_date__date=today).aggregate(total_amount=Sum('polygon_count'))['total_amount'] or 0
                counts['qc_polygon_count'] = Document.objects.filter(map_code=map_code,qc_completed_date__date=today).aggregate(total_amount=Sum('qc_polygon_count'))['total_amount'] or 0
                counts['rectify_completed'] = Document.objects.filter(rectify_agency_id__in=agency,map_code=map_code,rectify_completed_date__isnull=False,rectify_completed_date__date=today).count()
                counts['digitize_completed'] = Document.objects.filter(digitize_agency_id__in=agency,map_code=map_code, digitize_completed_date__isnull=False,digitize_completed_date__date=today).count()
                counts['qc_completed'] = Document.objects.filter(qc_agency_id__in=agency,map_code=map_code, qc_completed_date__isnull=False,qc_completed_date__date=today).count()
                counts['pdf_completed'] = Document.objects.filter(qc_agency_id__in=agency,map_code=map_code, pdf_completed_date__isnull=False,pdf_completed_date__date=today).count()
                counts['shape_completed'] = Document.objects.filter(qc_agency_id__in=agency,map_code=map_code, shape_completed_date__isnull=False,shape_completed_date__date=today).count()

                
            
          


            counts_by_maptype.append({
                'maptype_id': maptype_id,
                'map_code':map_code,
                'mapname_english':mapname_english,
                'mapname_marathi':mapname_marathi,
                **counts,
            })

        response_data = {
            'counts_by_maptype': counts_by_maptype,
            'status': True
        }

        return Response(data=response_data, status=status.HTTP_200_OK)