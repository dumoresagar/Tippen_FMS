from django.shortcuts import render
from django.views.generic import TemplateView


class HomePageView(TemplateView):

    template_name = 'index.html'

import json         
from .models import Village,Taluka
from django.http import HttpResponse

def ExperimentScript(request):
    with open('data.json', 'r') as f:
        data = json.load(f)
        created_query = 0
        for item in data:

            talu = Taluka.objects.get(taluka_code=item['taluka_code'])
            item['taluka'] = talu
            item['village_code'] = item.pop('village_code')
            item['village_name'] = item.pop('village_name')


    
            obj = Village.objects.create(

                taluka = item.get('taluka'),
                village_code = item.get('village_code'),
                village_name = item.get('village_name'),

            )
            obj.save()
            print("BBBBBBBBBBBBBBBBBBBB",obj.id)
            created_query += 1
    return HttpResponse(str({"created_query":created_query}),status=200)

# import os

# def dynamic_upload_path(instance, filename):
#     # Extract the district, taluka, and village codes from the filename
#     district_code = filename[:3]
#     taluka_code = filename[3:7]
#     village_code = filename[7:13]
#     print("Distrct Code",district_code)
#     print("Taluka Code",taluka_code)
#     print("Village Code",village_code)
    
#     district_name = District.objects.filter(district_code=district_code).values('district_name')
#     print("AAAAAAAAAAAAAAAAAa",district_name)

#     taluka_name = Taluka.objects.filter(taluka_code=district_code).values('taluka_name')
#     print("BBBBBBBBBBBBBBBB",taluka_name)

#     village_name = Village.objects.filter(village_code=district_code).values('village_name')
#     print("CCCCCCCCCCCCCCC",village_name)



#     # Define the base directory where uploads will be stored
#     base_dir = 'uploads'

#     # Create the full directory path based on the codes
#     district_dir = os.path.join(base_dir, district_name)
#     taluka_dir = os.path.join(district_dir, taluka_name)
#     village_dir = os.path.join(taluka_dir, village_name)

#     # Create the directories if they don't exist
#     for directory in [base_dir, district_dir, taluka_dir, village_dir]:
#         if not os.path.exists(directory):
#             os.makedirs(directory)

#     # Return the final path for the uploaded file
#     return os.path.join(village_dir, filename)

from rest_framework import generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from core.models import KumbhAsset,JsonDataMaster
from .serializers import KumbhAssetSerializer,AssetQuationAnswerSerializer,CreateKumbhAssetSerializer,UpdateKumbhAssetSerializer
from rest_framework import status
from rest_framework.views import APIView


class CreateKumbhAssetGenericAPI(generics.GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (AllowAny,)
    serializer_class = CreateKumbhAssetSerializer

    def post(self, request, format=None):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            test = KumbhAsset.objects.filter(id=serializer.data.get('id')).last()
            KumbhAsset.objects.filter(id=test.id).update(qr_code=serializer.data.get('qr_code'))          
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class GetAssetDetailsGenericAPI(generics.GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (AllowAny,)
    serializer_class = KumbhAssetSerializer

    def get(self, request, *args, **kwargs):
        try:

            asset_info = KumbhAsset.objects.get(asset_code=kwargs.get('asset_code'))
            data = KumbhAssetSerializer(asset_info).data
            return Response({"data":data,"message": "Success"},status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"data": {"message": str(e)}, "status": status.HTTP_204_NO_CONTENT})
        

class KumbhAssetGenericAPI(generics.GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (AllowAny,)
    serializer_class = UpdateKumbhAssetSerializer
    
    def put(self, request, *args, **kwargs):
        try:
            asset_obj = KumbhAsset.objects.get(id=kwargs.get("pk"))
        except KumbhAsset.DoesNotExist:
            return Response({"msg": "Record does not exist"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(asset_obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            test = KumbhAsset.objects.filter(id=serializer.data.get('id')).last()
            KumbhAsset.objects.filter(id=test.id).update(asset_image=serializer.data.get('asset_image'))
            return Response({"data": serializer.data, "message": "Success", "status": True})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ListAssetAPIView(generics.ListCreateAPIView):
    queryset = KumbhAsset.objects.all().order_by('-date_created')
    serializer_class = KumbhAssetSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (AllowAny,)

    def list(self, request):
        try:
            details = self.get_queryset()
            serializer = KumbhAssetSerializer(details, many=True)
            return Response({"data": serializer.data, "message": "Success"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"data": {"message": str(e)}, "status": status.HTTP_500_INTERNAL_SERVER_ERROR})
        
class CreateAssetQuationAnswerGenericAPI(generics.GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (AllowAny,)
    serializer_class = AssetQuationAnswerSerializer

    def get(self, request, *args, **kwargs):
        try:

            asset_quetions_info = JsonDataMaster.objects.filter(asset_id=kwargs.get('pk')).order_by('-date_created')
            data = AssetQuationAnswerSerializer(asset_quetions_info,many=True).data
            return Response({"data":data,"message": "Success"},status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"data": {"message": str(e)}, "status": status.HTTP_204_NO_CONTENT})

    def post(self, request, format=None):
        serializer = AssetQuationAnswerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

import os
from django.conf import settings
from django.shortcuts import render

def list_media_documents(request):
    media_path = settings.MEDIA_ROOT
    document_extensions = {".csv",".pdf", ".doc", ".docx", ".xls", ".xlsx", ".txt"}  # Allowed file extensions

    document_list = []
    for root, _, files in os.walk(media_path):
        for file in files:
            if any(file.lower().endswith(ext) for ext in document_extensions):
                relative_path = os.path.relpath(os.path.join(root, file), media_path)
                document_list.append(f"{settings.MEDIA_URL}{relative_path}")

    return render(request, "documents_list.html", {"document_list": document_list})
