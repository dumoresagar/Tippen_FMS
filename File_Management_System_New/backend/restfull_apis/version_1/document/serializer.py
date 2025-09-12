from django.utils.translation import gettext as _
from rest_framework import serializers
from core.models import Document,District,Taluka,Village
from users.models import User,Agency
from django.core.exceptions import ValidationError
from os.path import splitext
import os

class DistrictNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ['district_name']

class TalukaNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Taluka
        fields = ['taluka_name']

class VillageNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Village
        fields = ['village_name']
class UploadDocumentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Document
        fields = "__all__"


class UploadScanDocumentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Document
        fields = "__all__"

    def validate_scan_upload(self, value):
        """
        Custom validation to check if a file with the same name already exists.
        """
        if self.instance:
            # If updating an existing object, allow the same file to be re-uploaded
            return value
        
        filename = value.name
        base_filename,_ = os.path.splitext(filename)
        code = base_filename.split("_")[0]

        village_code = filename[7:13]
        maptype_code = filename[13:15]
        static_map_code = "09"

        # Check if a document with the same scan_upload already exists in the database
        existing_document = Document.objects.filter(barcode_number__exact=code).first()
        if existing_document:
            raise serializers.ValidationError(f"{filename} A document with the same scan_upload already exists.")
        elif maptype_code == static_map_code:
            existing_village_maptype = Document.objects.filter(village_code=village_code,map_code=maptype_code).first()
            if existing_village_maptype:
                raise serializers.ValidationError(f"{filename} This Village Map-Code Already Exists.")
        
        return value

class GetDistrictSerialzier(serializers.ModelSerializer):
    class Meta:
        model=District

class FilterVillageSerialzer(serializers.ModelSerializer):
    taluka__taluka_name = serializers.SerializerMethodField(read_only=True)
    taluka__district__district_name= serializers.SerializerMethodField(read_only=True)
    taluka__taluka_code = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Village
        fields = "__all__"

    def get_taluka__taluka_code(self,obj):
        if obj and obj.taluka:
            return obj.taluka.taluka_code
        else:
            return None
        
    def get_taluka__taluka_name(self,obj):
        if obj and obj.taluka:
            return obj.taluka.taluka_name
        else:
            return None
    def get_taluka__district__district_name(self,obj):
        if obj and obj.taluka and obj.taluka.district:
            return obj.taluka.district.district_name
        else:
            return None
        
class ScanDocumentListSerializer(serializers.ModelSerializer):
    scan_by_username = serializers.SerializerMethodField(read_only=True)
    rectify_by_username = serializers.SerializerMethodField(read_only=True)
    digitize_by_username = serializers.SerializerMethodField(read_only=True)
    qc_by_username = serializers.SerializerMethodField(read_only=True)
    pdf_by_username = serializers.SerializerMethodField(read_only=True)
    shape_by_username = serializers.SerializerMethodField(read_only=True)
    current_status = serializers.SerializerMethodField(read_only=True)
    district_name = serializers.SerializerMethodField('district',read_only=True)
    taluka_name = serializers.SerializerMethodField('taluka',read_only=True)
    village_name = serializers.SerializerMethodField('village',read_only=True)

    class Meta:
        model = Document
        fields = ['id','agency_id','district_name','taluka_name','taluka_code','village_name','scan_upload','barcode_number','file_name','district_code','village_code','map_code','scan_uploaded_by','scan_uploaded_date','current_status','remarks','scan_by_username','rectify_by_username','digitize_by_username','qc_by_username','pdf_by_username','shape_by_username']

    
   
    def district(self,obj):
        try:
            query_set = District.objects.get(district_code=obj.district_code)
            return DistrictNameSerializer(query_set).data
        except District.DoesNotExist:
            return None
    
    def taluka(self, obj):
        try:
            query_set = Taluka.objects.get(taluka_code=obj.taluka_code)
            return TalukaNameSerializer(query_set).data
        except Taluka.DoesNotExist:
            return None

    
    def village(self,obj):
        try:
            query_set = Village.objects.get(village_code=obj.village_code)
            return VillageNameSerializer(query_set).data
        except Village.DoesNotExist:
            return None
    
    def get_current_status(self,obj):
        if obj and obj.current_status:
            return obj.current_status.status
        else:
            return None
        
    def get_scan_by_username(self,obj):
        if obj and obj.scan_uploaded_by:
            return obj.scan_uploaded_by.username
        else:
            return None
    
    def get_rectify_by_username(self,obj):
        if obj and obj.rectify_by:
            return obj.rectify_by.username
        else:
            return None
    
    def get_digitize_by_username(self,obj):
        if obj and obj.digitize_by:
            return obj.digitize_by.username
        else:
            return None
    
    def get_qc_by_username(self,obj):
        if obj and obj.qc_by:
            return obj.qc_by.username
        else:
            return None
    
    def get_pdf_by_username(self,obj):
        if obj and obj.pdf_by:
            return obj.pdf_by.username
        else:
            return None
        
    def get_shape_by_username(self,obj):
        if obj and obj.shape_by:
            return obj.shape_by.username
        else:
            return None

class NotScanDocumentListSerializer(serializers.ModelSerializer):
    current_status = serializers.SerializerMethodField(read_only=True)
    district_name = serializers.SerializerMethodField('district',read_only=True)
    taluka_name = serializers.SerializerMethodField('taluka',read_only=True)
    village_name = serializers.SerializerMethodField('village',read_only=True)

    class Meta:
        model = Document
        fields = ['id','agency_id','scan_upload','district_name','taluka_name','taluka_code','village_name','barcode_number',
                  'file_name','district_code','village_code','map_code','scan_uploaded_by','scan_uploaded_date','current_status',
                  'remarks']
                
    
   
    def district(self,obj):
        try:
            query_set = District.objects.get(district_code=obj.district_code)
            return DistrictNameSerializer(query_set).data
        except District.DoesNotExist:
            return None
    
    def taluka(self, obj):
        try:
            query_set = Taluka.objects.get(taluka_code=obj.taluka_code)
            return TalukaNameSerializer(query_set).data
        except Taluka.DoesNotExist:
            return None

    
    def village(self,obj):
        try:
            query_set = Village.objects.get(village_code=obj.village_code)
            return VillageNameSerializer(query_set).data
        except Village.DoesNotExist:
            return None
    
    def get_current_status(self,obj):
        if obj and obj.current_status:
            return obj.current_status.status
        else:
            return None
        
class RectifyDocumentListSerializer(serializers.ModelSerializer):
    scan_by_username = serializers.SerializerMethodField(read_only=True)
    rectify_by_username = serializers.SerializerMethodField(read_only=True)
    digitize_by_username = serializers.SerializerMethodField(read_only=True)
    qc_by_username = serializers.SerializerMethodField(read_only=True)
    pdf_by_username = serializers.SerializerMethodField(read_only=True)
    shape_by_username = serializers.SerializerMethodField(read_only=True)
    current_status = serializers.SerializerMethodField(read_only=True)
    district_name = serializers.SerializerMethodField('district',read_only=True)
    taluka_name = serializers.SerializerMethodField('taluka',read_only=True)
    village_name = serializers.SerializerMethodField('village',read_only=True)

    class Meta:
        model = Document
        fields = [ "id","scan_upload",'district_name','taluka_name','village_name',"barcode_number","file_name" ,"district_code","village_code","map_code","scan_uploaded_by",
                   "scan_uploaded_date","rectify_agency_id","rectify_upload" ,"rectify_by","rectify_assign_date","rectify_completed_date",
                    "digitize_agency_id","digitize_upload","digitize_by","polygon_count","digitize_assign_date","digitize_completed_date",
                    "qc_agency_id","qc_upload","qc_by","qc_assign_date","qc_completed_date","pdf_upload","pdf_by","pdf_assign_date",
                    "pdf_completed_date","shape_upload","shape_by","shape_assign_date","shape_completed_date","current_status","remarks",
                    'scan_by_username','rectify_by_username','digitize_by_username','qc_by_username','pdf_by_username','shape_by_username']
    
   
    def district(self,obj):
        try:
            query_set = District.objects.get(district_code=obj.district_code)
            return DistrictNameSerializer(query_set).data
        except District.DoesNotExist:
            return None
    
    def taluka(self, obj):
        try:
            query_set = Taluka.objects.get(taluka_code=obj.taluka_code)
            return TalukaNameSerializer(query_set).data
        except Taluka.DoesNotExist:
            return None

    
    def village(self,obj):
        try:
            query_set = Village.objects.get(village_code=obj.village_code)
            return VillageNameSerializer(query_set).data
        except Village.DoesNotExist:
            return None
    
    def get_current_status(self,obj):
        if obj and obj.current_status:
            return obj.current_status.status
        else:
            return None
        
    def get_scan_by_username(self,obj):
        if obj and obj.scan_uploaded_by:
            return obj.scan_uploaded_by.username
        else:
            return None
    
    def get_rectify_by_username(self,obj):
        if obj and obj.rectify_by:
            return obj.rectify_by.username
        else:
            return None
    
    def get_digitize_by_username(self,obj):
        if obj and obj.digitize_by:
            return obj.digitize_by.username
        else:
            return None
    
    def get_qc_by_username(self,obj):
        if obj and obj.qc_by:
            return obj.qc_by.username
        else:
            return None
    
    def get_pdf_by_username(self,obj):
        if obj and obj.pdf_by:
            return obj.pdf_by.username
        else:
            return None
        
    def get_shape_by_username(self,obj):
        if obj and obj.shape_by:
            return obj.shape_by.username
        else:
            return None
        
class DigitizeDocumentListSerializer(serializers.ModelSerializer):
    scan_by_username = serializers.SerializerMethodField(read_only=True)
    rectify_by_username = serializers.SerializerMethodField(read_only=True)
    digitize_by_username = serializers.SerializerMethodField(read_only=True)
    qc_by_username = serializers.SerializerMethodField(read_only=True)
    pdf_by_username = serializers.SerializerMethodField(read_only=True)
    shape_by_username = serializers.SerializerMethodField(read_only=True)
    current_status = serializers.SerializerMethodField(read_only=True)
    district_name = serializers.SerializerMethodField('district',read_only=True)
    taluka_name = serializers.SerializerMethodField('taluka',read_only=True)
    village_name = serializers.SerializerMethodField('village',read_only=True)
    class Meta:
        model = Document
        fields = [ "id","scan_upload",'district_name','taluka_name','village_name',"barcode_number","file_name" ,"district_code","village_code","map_code","scan_uploaded_by",
                   "scan_uploaded_date","rectify_agency_id","rectify_upload" ,"rectify_by","rectify_assign_date","rectify_completed_date",
                    "digitize_agency_id","digitize_upload","digitize_by","polygon_count","digitize_assign_date","digitize_completed_date",
                    "qc_agency_id","qc_upload","qc_by","qc_assign_date","qc_completed_date","pdf_upload","pdf_by","pdf_assign_date",
                    "pdf_completed_date","shape_upload","shape_by","shape_assign_date","shape_completed_date","current_status","remarks",
                    'scan_by_username','rectify_by_username','digitize_by_username','qc_by_username','pdf_by_username','shape_by_username']
    
  
    def district(self,obj):
        try:
            query_set = District.objects.get(district_code=obj.district_code)
            return DistrictNameSerializer(query_set).data
        except District.DoesNotExist:
            return None
    
    def taluka(self, obj):
        try:
            query_set = Taluka.objects.get(taluka_code=obj.taluka_code)
            return TalukaNameSerializer(query_set).data
        except Taluka.DoesNotExist:
            return None

    
    def village(self,obj):
        try:
            query_set = Village.objects.get(village_code=obj.village_code)
            return VillageNameSerializer(query_set).data
        except Village.DoesNotExist:
            return None
    
    def get_current_status(self,obj):
        if obj and obj.current_status:
            return obj.current_status.status
        else:
            return None
        
    def get_scan_by_username(self,obj):
        if obj and obj.scan_uploaded_by:
            return obj.scan_uploaded_by.username
        else:
            return None
    
    def get_rectify_by_username(self,obj):
        if obj and obj.rectify_by:
            return obj.rectify_by.username
        else:
            return None
    
    def get_digitize_by_username(self,obj):
        if obj and obj.digitize_by:
            return obj.digitize_by.username
        else:
            return None
    
    def get_qc_by_username(self,obj):
        if obj and obj.qc_by:
            return obj.qc_by.username
        else:
            return None
    
    def get_pdf_by_username(self,obj):
        if obj and obj.pdf_by:
            return obj.pdf_by.username
        else:
            return None
        
    def get_shape_by_username(self,obj):
        if obj and obj.shape_by:
            return obj.shape_by.username
        else:
            return None

class QcDocumentListSerializer(serializers.ModelSerializer):
    scan_by_username = serializers.SerializerMethodField(read_only=True)
    rectify_by_username = serializers.SerializerMethodField(read_only=True)
    digitize_by_username = serializers.SerializerMethodField(read_only=True)
    qc_by_username = serializers.SerializerMethodField(read_only=True)
    pdf_by_username = serializers.SerializerMethodField(read_only=True)
    shape_by_username = serializers.SerializerMethodField(read_only=True)
    current_status = serializers.SerializerMethodField(read_only=True)
    district_name = serializers.SerializerMethodField('district',read_only=True)
    taluka_name = serializers.SerializerMethodField('taluka',read_only=True)
    village_name = serializers.SerializerMethodField('village',read_only=True)
    class Meta:
        model = Document
        fields = [ "id","scan_upload",'district_name','taluka_name','village_name',"barcode_number","file_name" ,"district_code","village_code","map_code","scan_uploaded_by",
                   "scan_uploaded_date","rectify_agency_id","rectify_upload" ,"rectify_by","rectify_assign_date","rectify_completed_date",
                    "digitize_agency_id","digitize_upload","digitize_by","polygon_count","digitize_assign_date","digitize_completed_date",
                    "qc_agency_id","qc_upload","qc_by","qc_assign_date","qc_completed_date","pdf_upload","pdf_by","pdf_assign_date",
                    "pdf_completed_date","shape_upload","shape_by","shape_assign_date","shape_completed_date","current_status","remarks",
                    'scan_by_username','rectify_by_username','digitize_by_username','qc_by_username','pdf_by_username','shape_by_username']
    
    
    def district(self,obj):
        try:
            query_set = District.objects.get(district_code=obj.district_code)
            return DistrictNameSerializer(query_set).data
        except District.DoesNotExist:
            return None
    
    def taluka(self, obj):
        try:
            query_set = Taluka.objects.get(taluka_code=obj.taluka_code)
            return TalukaNameSerializer(query_set).data
        except Taluka.DoesNotExist:
            return None

    
    def village(self,obj):
        try:
            query_set = Village.objects.get(village_code=obj.village_code)
            return VillageNameSerializer(query_set).data
        except Village.DoesNotExist:
            return None
    
    def get_current_status(self,obj):
        if obj and obj.current_status:
            return obj.current_status.status
        else:
            return None
    
    def get_scan_by_username(self,obj):
        if obj and obj.scan_uploaded_by:
            return obj.scan_uploaded_by.username
        else:
            return None
    
    def get_rectify_by_username(self,obj):
        if obj and obj.rectify_by:
            return obj.rectify_by.username
        else:
            return None
    
    def get_digitize_by_username(self,obj):
        if obj and obj.digitize_by:
            return obj.digitize_by.username
        else:
            return None
    
    def get_qc_by_username(self,obj):
        if obj and obj.qc_by:
            return obj.qc_by.username
        else:
            return None
    
    def get_pdf_by_username(self,obj):
        if obj and obj.pdf_by:
            return obj.pdf_by.username
        else:
            return None
        
    def get_shape_by_username(self,obj):
        if obj and obj.shape_by:
            return obj.shape_by.username
        else:
            return None
        

class PdfDocumentListSerializer(serializers.ModelSerializer):
    current_status = serializers.SerializerMethodField(read_only=True)
    district_name = serializers.SerializerMethodField('district',read_only=True)
    taluka_name = serializers.SerializerMethodField('taluka',read_only=True)
    village_name = serializers.SerializerMethodField('village',read_only=True)
    class Meta:
        model = Document
        fields = [ "id","scan_upload",'district_name','taluka_name','village_name',"barcode_number","file_name" ,"district_code","village_code","map_code","scan_uploaded_by",
                   "scan_uploaded_date","rectify_agency_id","rectify_upload" ,"rectify_by","rectify_assign_date","rectify_completed_date",
                    "digitize_agency_id","digitize_upload","digitize_by","polygon_count","digitize_assign_date","digitize_completed_date",
                    "qc_agency_id","qc_upload","qc_by","qc_assign_date","qc_completed_date","pdf_upload","pdf_by","pdf_assign_date",
                    "pdf_completed_date","shape_upload","shape_by","shape_assign_date","shape_completed_date","current_status","remarks"]
    
    
    def district(self,obj):
        try:
            query_set = District.objects.get(district_code=obj.district_code)
            return DistrictNameSerializer(query_set).data
        except District.DoesNotExist:
            return None
    
    def taluka(self, obj):
        try:
            query_set = Taluka.objects.get(taluka_code=obj.taluka_code)
            return TalukaNameSerializer(query_set).data
        except Taluka.DoesNotExist:
            return None

    
    def village(self,obj):
        try:
            query_set = Village.objects.get(village_code=obj.village_code)
            return VillageNameSerializer(query_set).data
        except Village.DoesNotExist:
            return None
    
    def get_current_status(self,obj):
        if obj and obj.current_status:
            return obj.current_status.status
        else:
            return None
        

class UserListSerializer(serializers.ModelSerializer):
    user_role = serializers.SerializerMethodField(read_only=True)
    agency = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ['id','first_name','last_name','username','user_role','address','mobile_number','aadhar_no','active_status','agency','department','email']
    
    
    def get_user_role(self,obj):
        if obj and obj.user_role:
            return obj.user_role.role_name
        else:
            return None
    
    def get_agency(self,obj):
        if obj and obj.agency:
            return obj.agency.agency_name
        else:
            return None
        

class AgencyUserSerialzier(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username','email']
class AgencyListSerializer(serializers.ModelSerializer):
    user_details = serializers.SerializerMethodField("user",read_only=True)

    class Meta:
        model = Agency
        fields = "__all__"

    def user(self,obj):
        try:
            query_set = User.objects.filter(agency=obj.id,user_role__role_name="Agency Admin")
            return AgencyUserSerialzier(query_set,many=True).data
        except User.DoesNotExist:
            return None




class AllDocumentListSerialzer(serializers.ModelSerializer):
    scan_by_username = serializers.SerializerMethodField(read_only=True)
    rectify_by_username = serializers.SerializerMethodField(read_only=True)
    digitize_by_username = serializers.SerializerMethodField(read_only=True)
    qc_by_username = serializers.SerializerMethodField(read_only=True)
    pdf_by_username = serializers.SerializerMethodField(read_only=True)
    shape_by_username = serializers.SerializerMethodField(read_only=True)
    rectify_agency_name = serializers.SerializerMethodField(read_only=True)
    digitize_agency_name = serializers.SerializerMethodField(read_only=True)
    qc_agency_name = serializers.SerializerMethodField(read_only=True)
    current_status = serializers.SerializerMethodField(read_only=True)
    district_name = serializers.SerializerMethodField('district',read_only=True)
    taluka_name = serializers.SerializerMethodField('taluka',read_only=True)
    village_name = serializers.SerializerMethodField('village',read_only=True)
    class Meta:
        model = Document
        fields = "__all__"
    
    
    
    def district(self,obj):
        try:
            query_set = District.objects.get(district_code=obj.district_code)
            return DistrictNameSerializer(query_set).data
        except District.DoesNotExist:
            return None
    
    def taluka(self, obj):
        try:
            query_set = Taluka.objects.get(taluka_code=obj.taluka_code)
            return TalukaNameSerializer(query_set).data
        except Taluka.DoesNotExist:
            return None

    
    def village(self,obj):
        try:
            query_set = Village.objects.get(village_code=obj.village_code)
            return VillageNameSerializer(query_set).data
        except Village.DoesNotExist:
            return None

    
    def get_rectify_agency_name(self,obj):
        if obj and obj.rectify_agency_id:
            return obj.rectify_agency_id.agency_name
        else:
            return None
    
    def get_digitize_agency_name(self,obj):
        if obj and obj.digitize_agency_id:
            return obj.digitize_agency_id.agency_name
        else:
            return None
        
    def get_qc_agency_name(self,obj):
        if obj and obj.qc_agency_id:
            return obj.qc_agency_id.agency_name
        else:
            return None
    
    def get_scan_by_username(self,obj):
        if obj and obj.scan_uploaded_by:
            return obj.scan_uploaded_by.username
        else:
            return None
    
    def get_rectify_by_username(self,obj):
        if obj and obj.rectify_by:
            return obj.rectify_by.username
        else:
            return None
    
    def get_digitize_by_username(self,obj):
        if obj and obj.digitize_by:
            return obj.digitize_by.username
        else:
            return None
    
    def get_qc_by_username(self,obj):
        if obj and obj.qc_by:
            return obj.qc_by.username
        else:
            return None
    
    def get_pdf_by_username(self,obj):
        if obj and obj.pdf_by:
            return obj.pdf_by.username
        else:
            return None
        
    def get_shape_by_username(self,obj):
        if obj and obj.shape_by:
            return obj.shape_by.username
        else:
            return None
        
    def get_current_status(self,obj):
        if obj and obj.current_status:
            return obj.current_status.status
        else:
            return None
