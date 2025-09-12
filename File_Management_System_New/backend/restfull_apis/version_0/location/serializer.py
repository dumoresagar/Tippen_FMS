from django.utils.translation import gettext as _
from rest_framework import serializers
from core.models import District,MapType,Taluka,Village,PreScanningDocument,PreDraftingReport,AgencyInventry,Document
from rest_framework.validators import ValidationError
import os

class CreateDistrictSerializer(serializers.ModelSerializer):

    class Meta:
        model = District
        fields = "__all__"


class CreateMapTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = MapType
        fields = "__all__"

class CreateTalukaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Taluka
        fields = "__all__"

class RetriveTalukaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Taluka
        fields = "__all__"

class CreateVillageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Village
        fields = "__all__"

class RetriveVillageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Village
        fields = "__all__"


class PostPreScanningDocumentSerializer(serializers.ModelSerializer):

    class Meta:
        model = PreScanningDocument
        fields = "__all__"

    def validate_mis_date(self, value):
        taluka_id = self.initial_data.get('taluka_id')  # Fetching the taluka_id from the incoming data
        if taluka_id is not None and PreScanningDocument.objects.filter(taluka_id=taluka_id, mis_date=value).exists():
            raise ValidationError("mis_date must be unique for each taluka")

        return value

class PreScanningDocumentSerializer(serializers.ModelSerializer):
    district_name = serializers.SerializerMethodField(read_only=True)
    taluka_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = PreScanningDocument
        fields = "__all__"

    def get_district_name(self,obj):
        if obj and obj.district_id:
            return obj.district_id.district_name
        else:
            return None
    
    def get_taluka_name(self,obj):
        if obj and obj.taluka_id:
            return obj.taluka_id.taluka_name
        else:
            return None


class PostPreDraftingReportSerializer(serializers.ModelSerializer):

    class Meta:
        model = PreDraftingReport
        fields = "__all__"
    
    def validate_pre_drafting_date(self, value):
        taluka_id = self.initial_data.get('taluka_id')  # Fetching the taluka_id from the incoming data
        if taluka_id is not None and PreDraftingReport.objects.filter(taluka_id=taluka_id, pre_drafting_date=value).exists():
            raise ValidationError("pre drafting date must be unique for each taluka")

        return value

class PreDraftingReportSerializer(serializers.ModelSerializer):
    district_name = serializers.SerializerMethodField(read_only=True)
    taluka_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = PreDraftingReport
        fields = "__all__"
    
    def get_district_name(self,obj):
        if obj and obj.district_id:
            return obj.district_id.district_name
        else:
            return None
    
    def get_taluka_name(self,obj):
        if obj and obj.taluka_id:
            return obj.taluka_id.taluka_name
        else:
            return None


class AgencyInventrySerializer(serializers.ModelSerializer):

    class Meta:
        model = AgencyInventry
        fields = "__all__"



from datetime import datetime,date, time, timedelta
from django.db.models import Sum
class PreScanReportSerializer(serializers.ModelSerializer):
    taluka_name = serializers.SerializerMethodField(read_only=True)
    total_day_count = serializers.SerializerMethodField('get_total_day_count', read_only=True)

    class Meta:
        model = PreScanningDocument
        fields = ['scanning_complete_count','taluka_name','mis_date','total_day_count']
    
    def get_taluka_name(self,obj):
        if obj and obj.taluka_id:
            return obj.taluka_id.taluka_name
        else:
            return None
    
    def get_total_day_count(self,obj):
        return 1

class PreScanReportSerializerV1(serializers.ModelSerializer):
    taluka_name = serializers.SerializerMethodField(read_only=True)
    total_day_count = serializers.SerializerMethodField('get_total_day_count', read_only=True)
    mis_date = serializers.SerializerMethodField('get_mis_date',read_only=True)
    scanning_complete_count = serializers.SerializerMethodField('get_scanning_complete_count',read_only=True)

    class Meta:
        model = PreScanningDocument
        fields = ['scanning_complete_count','taluka_name','mis_date','total_day_count']
    
    def get_taluka_name(self,obj):
        if obj and obj.taluka_id:
            return obj.taluka_id.taluka_name
        else:
            return None
    
    def get_total_day_count(self,obj):
        return 0
    
    def get_mis_date(self,obj):
        today = datetime.now().date()
        return today
    
    def get_scanning_complete_count(self,obj):
        return 0
    
class DistrcitWiseTalukaTodalTodaySerialzier(serializers.ModelSerializer):
    taluka_name = serializers.SerializerMethodField('taluka',read_only=True)
    all = serializers.SerializerMethodField('alltaluka',read_only=True)

    class Meta:
        model = District
        fields = "__all__"

    def taluka(self,obj):
        today = datetime.now().date()
        query_set = PreScanningDocument.objects.filter(district_id=obj.id,mis_date=today).distinct('taluka_id')
        if query_set.exists():
            return PreScanReportSerializer(query_set,many=True).data
        else:
            query_set = PreScanningDocument.objects.filter(district_id=obj.id).distinct('taluka_id')
            return PreScanReportSerializerV1(query_set,many=True).data


    
    def alltaluka(self,obj):
        start_date = self.context['request'].query_params.get('start_date',None)
        end_date = self.context['request'].query_params.get('end_date',None)

        counts_by_district_prescan=[]

        if start_date and end_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')


            total_scanning_complete_count=PreScanningDocument.objects.filter(district_id=obj.id,
                                                mis_date__gte=start_date.date(),
                                                mis_date__lt=(end_date.date()+ timedelta(days=1))                                   
                                                ).aggregate(total_scanning_complete_count=Sum('scanning_complete_count'))['total_scanning_complete_count'] or 0
            mis_date_count =PreScanningDocument.objects.filter(district_id=obj.id,
                                                mis_date__gte=start_date.date(),
                                                mis_date__lt=(end_date.date()+ timedelta(days=1))                                  
                                                )
            total_day = mis_date_count.values_list('mis_date', flat=True).distinct()

            counts_by_district_prescan.append({
                'from_date': start_date.strftime('%Y-%m-%d'),
                'end_date':end_date.strftime('%Y-%m-%d'),
                'total_day':total_day.count(),
                'scanning_complete_count':total_scanning_complete_count,
            })
            return counts_by_district_prescan
        else:
            total_scanning_complete_count=PreScanningDocument.objects.filter(district_id=obj.id,
                                    ).aggregate(total_scanning_complete_count=Sum('scanning_complete_count'))['total_scanning_complete_count'] or 0
            mis_date_count=PreScanningDocument.objects.filter(district_id=obj.id)

            total_day = mis_date_count.values_list('mis_date', flat=True).distinct()

            
            counts_by_district_prescan.append({
                'from_date': "All date",
                'end_date': "All date",
                'total_day':total_day.count(),
                'scanning_complete_count':total_scanning_complete_count,
            })
            return counts_by_district_prescan

#############################################
        

class PreDraftReportSerializer(serializers.ModelSerializer):
    taluka_name = serializers.SerializerMethodField(read_only=True)
    total_day_count = serializers.SerializerMethodField('get_total_day_count', read_only=True)

    class Meta:
        model = PreDraftingReport
        fields = ['drafting_map_count','taluka_name','pre_drafting_date','total_day_count']
    
    def get_taluka_name(self,obj):
        if obj and obj.taluka_id:
            return obj.taluka_id.taluka_name
        else:
            return None
    
    def get_total_day_count(self,obj):
        return 1

class PreDraftReportSerializerV1(serializers.ModelSerializer):
    taluka_name = serializers.SerializerMethodField(read_only=True)
    total_day_count = serializers.SerializerMethodField('get_total_day_count', read_only=True)
    pre_drafting_date = serializers.SerializerMethodField('get_pre_drafting_date',read_only=True)
    drafting_map_count = serializers.SerializerMethodField('get_drafting_map_count',read_only=True)

    class Meta:
        model = PreDraftingReport
        fields = ['drafting_map_count','taluka_name','pre_drafting_date','total_day_count']
    
    def get_taluka_name(self,obj):
        if obj and obj.taluka_id:
            return obj.taluka_id.taluka_name
        else:
            return None
    
    def get_total_day_count(self,obj):
        return 0
    
    def get_pre_drafting_date(self,obj):
        today = datetime.now().date()
        return today
    
    def get_drafting_map_count(self,obj):
        return 0
    
class PreDraftDistrcitWiseTalukaTodalTodaySerialzier(serializers.ModelSerializer):
    taluka_name = serializers.SerializerMethodField('taluka',read_only=True)
    all = serializers.SerializerMethodField('alltaluka',read_only=True)

    class Meta:
        model = District
        fields = "__all__"

    def taluka(self,obj):
        today = datetime.now().date()
        query_set = PreDraftingReport.objects.filter(district_id=obj.id,pre_drafting_date=today).distinct('taluka_id')
        if query_set.exists():
            return PreDraftReportSerializer(query_set,many=True).data
        else:
            query_set = PreDraftingReport.objects.filter(district_id=obj.id).distinct('taluka_id')
            return PreDraftReportSerializerV1(query_set,many=True).data


    
    def alltaluka(self,obj):
        start_date = self.context['request'].query_params.get('start_date',None)
        end_date = self.context['request'].query_params.get('end_date',None)

        counts_by_district_prescan=[]

        if start_date and end_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')


            total_drafting_map_count=PreDraftingReport.objects.filter(district_id=obj.id,
                                                pre_drafting_date__gte=start_date.date(),
                                                pre_drafting_date__lt=(end_date.date()+ timedelta(days=1))                                   
                                                ).aggregate(total_drafting_map_count=Sum('drafting_map_count'))['total_drafting_map_count'] or 0
            pre_drafting_date_count =PreDraftingReport.objects.filter(district_id=obj.id,
                                                pre_drafting_date__gte=start_date.date(),
                                                pre_drafting_date__lt=(end_date.date()+ timedelta(days=1))                                  
                                                )
            total_day = pre_drafting_date_count.values_list('pre_drafting_date', flat=True).distinct()

            counts_by_district_prescan.append({
                'from_date': start_date.strftime('%Y-%m-%d'),
                'end_date':end_date.strftime('%Y-%m-%d'),
                'total_day':total_day.count(),
                'drafting_map_count':total_drafting_map_count,
            })
            return counts_by_district_prescan
        else:
            total_drafting_map_count=PreDraftingReport.objects.filter(district_id=obj.id,
                                    ).aggregate(total_drafting_map_count=Sum('drafting_map_count'))['total_drafting_map_count'] or 0
            pre_drafting_date_count=PreDraftingReport.objects.filter(district_id=obj.id)

            total_day = pre_drafting_date_count.values_list('pre_drafting_date', flat=True).distinct()

            
            counts_by_district_prescan.append({
                'from_date': "All date",
                'end_date': "All date",
                'total_day':total_day.count(),
                'drafting_map_count':total_drafting_map_count,
            })
            return counts_by_district_prescan
        

class PolygonUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Document
        fields = "__all__"



class NewDistrictNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ['district_name']

class NewTalukaNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Taluka
        fields = ['taluka_name']

class NewVillageNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Village
        fields = ['village_name']
class DocumentLocationListSerialzer(serializers.ModelSerializer):
   
    district_name = serializers.SerializerMethodField('district',read_only=True)
    taluka_name = serializers.SerializerMethodField('taluka',read_only=True)
    village_name = serializers.SerializerMethodField('village',read_only=True)
   
    class Meta:
        model = Document
        fields = ['id','barcode_number','district_name','taluka_name','village_name']

        
    def district(self,obj):
        try:
            query_set = District.objects.get(district_code=obj.district_code)
            return NewDistrictNameSerializer(query_set).data
        except District.DoesNotExist:
            return None
    
    def taluka(self, obj):
        try:
            query_set = Taluka.objects.get(taluka_code=obj.taluka_code)
            return NewTalukaNameSerializer(query_set).data
        except Taluka.DoesNotExist:
            return None

    
    def village(self,obj):
        try:
            query_set = Village.objects.get(village_code=obj.village_code)
            return NewVillageNameSerializer(query_set).data
        except Village.DoesNotExist:
            return None
        
class ExtensionDocumentSerializer(serializers.ModelSerializer):
    scan_upload_extension = serializers.SerializerMethodField()
    file_name_extension = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = ['id', 'scan_upload_extension', 'file_name_extension']

    def get_scan_upload_extension(self, obj):
        return os.path.splitext(obj.scan_upload.name)[1] if obj.scan_upload else None

    def get_file_name_extension(self, obj):
        return os.path.splitext(obj.file_name)[1] if obj.file_name else None


class RectifyExtensionDocumentSerializer(serializers.ModelSerializer):
    rectify_upload_extension = serializers.SerializerMethodField()
    file_name_extension = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = ['id', 'rectify_upload_extension', 'file_name_extension']

    def get_rectify_upload_extension(self, obj):
        return os.path.splitext(obj.rectify_upload.name)[1] if obj.rectify_upload else None

    def get_file_name_extension(self, obj):
        return os.path.splitext(obj.file_name)[1] if obj.file_name else None
    


class DigitizeExtensionDocumentSerializer(serializers.ModelSerializer):
    digitize_upload_extension = serializers.SerializerMethodField()
    file_name_extension = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = ['id', 'digitize_upload_extension', 'file_name_extension']

    def get_digitize_upload_extension(self, obj):
        return os.path.splitext(obj.digitize_upload.name)[1] if obj.digitize_upload else None

    def get_file_name_extension(self, obj):
        return os.path.splitext(obj.file_name)[1] if obj.file_name else None
    


class BarcodeSerializer(serializers.Serializer):
    barcode_number = serializers.CharField()
