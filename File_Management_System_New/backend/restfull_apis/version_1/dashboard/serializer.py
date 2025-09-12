from django.utils.translation import gettext as _
from rest_framework import serializers
from core.models import Document,District,Taluka,Village,PaginationMaster
from users.models import User,Agency
from django.core.exceptions import ValidationError
from django.db.models import Sum
from datetime import timedelta

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
        
class RectifyListSerialzer(serializers.ModelSerializer):
    location = serializers.SerializerMethodField('location_name',read_only=True)
    current_status = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Document
        fields = [ "id","location","barcode_number","file_name" ,"district_code","village_code","map_code",
                   "rectify_agency_id","rectify_upload" ,"rectify_by","rectify_assign_date","rectify_completed_date",
                   "current_status","remarks"]
    
    def location_name(self, obj):
        query_set = Village.objects.filter(village_code=obj.village_code)

        return FilterVillageSerialzer(query_set,many=True).data
    
    def get_current_status(self,obj):
        if obj and obj.current_status:
            return obj.current_status.status
        else:
            return None
        

class DistrictListSerialzer(serializers.ModelSerializer):
    total_notfound_district_count = serializers.SerializerMethodField('total_notfound_district',read_only=True)
    total_scan_uploaded_count = serializers.SerializerMethodField('total_scan_uploaded',read_only=True)
    scan_uploaded_count = serializers.SerializerMethodField('scan_uploaded',read_only=True)
    rectify_allocated_count = serializers.SerializerMethodField('rectify_allocated',read_only=True)
    rectify_inprocess_count = serializers.SerializerMethodField('rectify_inprocess',read_only=True)
    rectify_completed_count = serializers.SerializerMethodField('rectify_completed',read_only=True)
    rectify_rejected_count = serializers.SerializerMethodField('rectify_rejected',read_only=True)
    rectify_onhold_count = serializers.SerializerMethodField('rectify_onhold',read_only=True)
    digitize_allocated_count = serializers.SerializerMethodField('digitize_allocated',read_only=True)
    digitize_inprocess_count = serializers.SerializerMethodField('digitize_inprocess',read_only=True)
    digitize_completed_count = serializers.SerializerMethodField('digitize_completed',read_only=True)
    digitize_rejected_count = serializers.SerializerMethodField('digitize_rejected',read_only=True)
    digitize_onhold_count = serializers.SerializerMethodField('digitize_onhold',read_only=True)
    qc_allocated_count = serializers.SerializerMethodField('qc_allocated',read_only=True)
    qc_inprocess_count = serializers.SerializerMethodField('qc_inprocess',read_only=True)
    qc_completed_count = serializers.SerializerMethodField('qc_completed',read_only=True)
    qc_rejected_count = serializers.SerializerMethodField('qc_rejected',read_only=True)
    qc_onhold_count = serializers.SerializerMethodField('qc_onhold',read_only=True)
    pdf_completed_count = serializers.SerializerMethodField('pdf_completed',read_only=True)
    shape_completed_count = serializers.SerializerMethodField('shape_completed',read_only=True)
    polygon_count = serializers.SerializerMethodField('polygon_count_completed',read_only=True)
    
    bel_scan_uploaded_count = serializers.SerializerMethodField('bel_scan_uploaded',read_only=True)
    bel_draft_uploaded_count = serializers.SerializerMethodField('bel_draft_uploaded',read_only=True)
    bel_gov_scan_qc_approved_count = serializers.SerializerMethodField('bel_gov_scan_qc_approved',read_only=True)
    bel_gov_draft_qc_approved_count = serializers.SerializerMethodField('bel_gov_draft_qc_approved',read_only=True)



    class Meta:
        model = District
        fields = "__all__"

    def bel_scan_uploaded(self, obj):
        agency = User.objects.filter(id=self.context['request'].user.id).values_list('agency',flat=True)
        team_ids = User.objects.filter(id=self.context['request'].user.id).values_list('agency__team', flat=True)

        if User.objects.filter(id=self.context['request'].user.id, user_role__role_name="Super Admin").exists():
            query_set =Document.objects.filter(district_code=obj.district_code,bel_scan_uploaded=True).count()

        elif User.objects.filter(id=self.context['request'].user.id, user_role__role_name="Team Admin").exists():
            query_set =Document.objects.filter(team_id__in=team_ids,district_code=obj.district_code,bel_scan_uploaded=True).count()

        elif User.objects.filter(id=self.context['request'].user.id, user_role__role_name="Agency Admin").exists():
            query_set =Document.objects.filter(rectify_agency_id__in=agency,district_code=obj.district_code,bel_scan_uploaded=True).count()

        return query_set
    
    def bel_draft_uploaded(self, obj):
        agency = User.objects.filter(id=self.context['request'].user.id).values_list('agency',flat=True)
        team_ids = User.objects.filter(id=self.context['request'].user.id).values_list('agency__team', flat=True)

        if User.objects.filter(id=self.context['request'].user.id, user_role__role_name="Super Admin").exists():
            query_set =Document.objects.filter(district_code=obj.district_code,bel_draft_uploaded=True).count()
        
        elif User.objects.filter(id=self.context['request'].user.id, user_role__role_name="Team Admin").exists():
            query_set =Document.objects.filter(team_id__in=team_ids,district_code=obj.district_code,bel_draft_uploaded=True).count()
      
        elif User.objects.filter(id=self.context['request'].user.id, user_role__role_name="Agency Admin").exists():
            query_set =Document.objects.filter(rectify_agency_id__in=agency,district_code=obj.district_code,bel_draft_uploaded=True).count()

        return query_set
    
    def bel_gov_scan_qc_approved(self, obj):
        agency = User.objects.filter(id=self.context['request'].user.id).values_list('agency',flat=True)
        team_ids = User.objects.filter(id=self.context['request'].user.id).values_list('agency__team', flat=True)

        if User.objects.filter(id=self.context['request'].user.id, user_role__role_name="Super Admin").exists():
            query_set =Document.objects.filter(district_code=obj.district_code,bel_gov_scan_qc_approved=True).count()

        elif User.objects.filter(id=self.context['request'].user.id, user_role__role_name="Team Admin").exists():
            query_set =Document.objects.filter(team_id__in=team_ids,district_code=obj.district_code,bel_gov_scan_qc_approved=True).count()
      
        elif User.objects.filter(id=self.context['request'].user.id, user_role__role_name="Agency Admin").exists():
            query_set =Document.objects.filter(rectify_agency_id__in=agency,district_code=obj.district_code,bel_gov_scan_qc_approved=True).count()

        return query_set
    
    def bel_gov_draft_qc_approved(self, obj):
        agency = User.objects.filter(id=self.context['request'].user.id).values_list('agency',flat=True)
        team_ids = User.objects.filter(id=self.context['request'].user.id).values_list('agency__team', flat=True)
     
        if User.objects.filter(id=self.context['request'].user.id, user_role__role_name="Super Admin").exists():
            query_set =Document.objects.filter(district_code=obj.district_code,bel_gov_draft_qc_approved=True).count()

        elif User.objects.filter(id=self.context['request'].user.id, user_role__role_name="Team Admin").exists():
            query_set =Document.objects.filter(team_id__in=team_ids,district_code=obj.district_code,bel_gov_draft_qc_approved=True).count()
      
        elif User.objects.filter(id=self.context['request'].user.id, user_role__role_name="Agency Admin").exists():
            query_set =Document.objects.filter(rectify_agency_id__in=agency,district_code=obj.district_code,bel_gov_draft_qc_approved=True).count()

        return query_set

    def total_notfound_district(self,obj):
        district_obj= District.objects.all().values_list('district_code',flat=True)
        query_set = Document.objects.exclude(district_code__in=district_obj).count()
        return query_set
    
    def total_scan_uploaded(self,obj):
        agency = User.objects.filter(id=self.context['request'].user.id).values_list('agency',flat=True)
        team_ids = User.objects.filter(id=self.context['request'].user.id).values_list('agency__team', flat=True)

        if User.objects.filter(id=self.context['request'].user.id, user_role__role_name="Super Admin").exists():
            query_set = Document.objects.filter(district_code=obj.district_code).count()
        
        elif User.objects.filter(id=self.context['request'].user.id, user_role__role_name="Team Admin").exists():
            query_set = Document.objects.filter(team_id__in=team_ids,district_code=obj.district_code).count()

        elif User.objects.filter(id=self.context['request'].user.id, user_role__role_name="Agency Admin").exists():
            query_set =  Document.objects.filter(rectify_agency_id__in=agency,district_code=obj.district_code).count()

        return query_set
    
    
    def scan_uploaded(self, obj):
        agency = User.objects.filter(id=self.context['request'].user.id).values_list('agency',flat=True)
        team_ids = User.objects.filter(id=self.context['request'].user.id).values_list('agency__team', flat=True)

        if User.objects.filter(id=self.context['request'].user.id, user_role__role_name="Super Admin").exists():
            query_set = Document.objects.filter(district_code=obj.district_code,current_status=1).count()
        
        elif User.objects.filter(id=self.context['request'].user.id, user_role__role_name="Team Admin").exists():
            query_set = Document.objects.filter(team_id__in=team_ids,district_code=obj.district_code,current_status=1).count()

        elif User.objects.filter(id=self.context['request'].user.id, user_role__role_name="Agency Admin").exists():
            query_set =  Document.objects.filter(team_id__in=team_ids,district_code=obj.district_code,current_status=1).count()
        
        return query_set

    def polygon_count_completed(self, obj):
        agency = User.objects.filter(id=self.context['request'].user.id).values_list('agency',flat=True)
        team_ids = User.objects.filter(id=self.context['request'].user.id).values_list('agency__team', flat=True)

        if User.objects.filter(id=self.context['request'].user.id, user_role__role_name="Super Admin").exists():
            query_set =Document.objects.filter(district_code=obj.district_code).aggregate(total_amount=Sum('polygon_count'))['total_amount']
        
        elif User.objects.filter(id=self.context['request'].user.id, user_role__role_name="Team Admin").exists():
            query_set =Document.objects.filter(team_id__in=team_ids,district_code=obj.district_code).aggregate(total_amount=Sum('polygon_count'))['total_amount']

        elif User.objects.filter(id=self.context['request'].user.id, user_role__role_name="Agency Admin").exists():
            query_set =Document.objects.filter(rectify_agency_id__in=agency,district_code=obj.district_code).aggregate(total_amount=Sum('polygon_count'))['total_amount']

        return query_set
    
    def rectify_allocated(self, obj):
        agency = User.objects.filter(id=self.context['request'].user.id).values_list('agency',flat=True)
        if User.objects.filter(id=self.context['request'].user.id, user_role__role_name="Super Admin").exists():
            query_set = Document.objects.filter(district_code=obj.district_code,current_status=3).count()

        elif User.objects.filter(id=self.context['request'].user.id, user_role__role_name="Agency Admin").exists():
            query_set = Document.objects.filter(rectify_agency_id__in=agency,district_code=obj.district_code,current_status=3).count()

        return query_set
    
    def rectify_inprocess(self, obj):
        agency = User.objects.filter(id=self.context['request'].user.id).values_list('agency',flat=True)
        if User.objects.filter(id=self.context['request'].user.id, user_role__role_name="Super Admin").exists():
            query_set = Document.objects.filter(district_code=obj.district_code,current_status=4).count()

        elif User.objects.filter(id=self.context['request'].user.id, user_role__role_name="Agency Admin").exists():
            query_set = Document.objects.filter(rectify_agency_id__in=agency,district_code=obj.district_code,current_status=4).count()

        return query_set
    
    def rectify_completed(self, obj):
        agency = User.objects.filter(id=self.context['request'].user.id).values_list('agency',flat=True)
        team_ids = User.objects.filter(id=self.context['request'].user.id).values_list('agency__team', flat=True)

        if User.objects.filter(id=self.context['request'].user.id, user_role__role_name="Super Admin").exists():
            query_set = Document.objects.filter(district_code=obj.district_code,rectify_completed_date__isnull=False).count()
        
        elif User.objects.filter(id=self.context['request'].user.id, user_role__role_name="Team Admin").exists():
            query_set =Document.objects.filter(team_id__in=team_ids,district_code=obj.district_code,rectify_completed_date__isnull=False).count()

        elif User.objects.filter(id=self.context['request'].user.id, user_role__role_name="Agency Admin").exists():
            query_set = Document.objects.filter(rectify_agency_id__in=agency,district_code=obj.district_code,rectify_completed_date__isnull=False).count()

        return query_set
    
    def rectify_rejected(self, obj):
        agency = User.objects.filter(id=self.context['request'].user.id).values_list('agency',flat=True)
        if User.objects.filter(id=self.context['request'].user.id, user_role__role_name="Super Admin").exists():
            query_set = Document.objects.filter(district_code=obj.district_code,current_status=6).count()

        elif User.objects.filter(id=self.context['request'].user.id, user_role__role_name="Agency Admin").exists():
            query_set = Document.objects.filter(rectify_agency_id__in=agency,district_code=obj.district_code,current_status=6).count()

        return query_set
    def rectify_onhold(self, obj):
        agency = User.objects.filter(id=self.context['request'].user.id).values_list('agency',flat=True)
        if User.objects.filter(id=self.context['request'].user.id, user_role__role_name="Super Admin").exists():
            query_set = Document.objects.filter(district_code=obj.district_code,current_status=7).count()

        elif User.objects.filter(id=self.context['request'].user.id, user_role__role_name="Agency Admin").exists():
            query_set = Document.objects.filter(rectify_agency_id__in=agency,district_code=obj.district_code,current_status=7).count()

        return query_set
    

    def digitize_allocated(self, obj):
        agency = User.objects.filter(id=self.context['request'].user.id).values_list('agency',flat=True)
        if User.objects.filter(id=self.context['request'].user.id, user_role__role_name="Super Admin").exists():
            query_set = Document.objects.filter(district_code=obj.district_code,current_status=8).count()

        elif User.objects.filter(id=self.context['request'].user.id, user_role__role_name="Agency Admin").exists():
            query_set = Document.objects.filter(digitize_agency_id__in=agency,district_code=obj.district_code,current_status=8).count()

        return query_set
    
    def digitize_inprocess(self, obj):
        agency = User.objects.filter(id=self.context['request'].user.id).values_list('agency',flat=True)
        if User.objects.filter(id=self.context['request'].user.id, user_role__role_name="Super Admin").exists():
            query_set = Document.objects.filter(district_code=obj.district_code,current_status=9).count()

        elif User.objects.filter(id=self.context['request'].user.id, user_role__role_name="Agency Admin").exists():
            query_set = Document.objects.filter(digitize_agency_id__in=agency,district_code=obj.district_code,current_status=9).count()

        return query_set
    
    def digitize_completed(self, obj):
        agency = User.objects.filter(id=self.context['request'].user.id).values_list('agency',flat=True)
        team_ids = User.objects.filter(id=self.context['request'].user.id).values_list('agency__team', flat=True)

        if User.objects.filter(id=self.context['request'].user.id, user_role__role_name="Super Admin").exists():
            query_set = Document.objects.filter(district_code=obj.district_code,digitize_completed_date__isnull=False).count()
        
        elif User.objects.filter(id=self.context['request'].user.id, user_role__role_name="Team Admin").exists():
            query_set =Document.objects.filter(team_id__in=team_ids,district_code=obj.district_code,digitize_completed_date__isnull=False).count()

        elif User.objects.filter(id=self.context['request'].user.id, user_role__role_name="Agency Admin").exists():
            query_set = Document.objects.filter(digitize_agency_id__in=agency,district_code=obj.district_code,digitize_completed_date__isnull=False).count()

        return query_set
    
    def digitize_rejected(self, obj):
        agency = User.objects.filter(id=self.context['request'].user.id).values_list('agency',flat=True)
        if User.objects.filter(id=self.context['request'].user.id, user_role__role_name="Super Admin").exists():
            query_set = Document.objects.filter(district_code=obj.district_code,current_status=11).count()

        elif User.objects.filter(id=self.context['request'].user.id, user_role__role_name="Agency Admin").exists():
            query_set = Document.objects.filter(digitize_agency_id__in=agency,district_code=obj.district_code,current_status=11).count()

        return query_set
    def digitize_onhold(self, obj):
        agency = User.objects.filter(id=self.context['request'].user.id).values_list('agency',flat=True)
        if User.objects.filter(id=self.context['request'].user.id, user_role__role_name="Super Admin").exists():
            query_set = Document.objects.filter(district_code=obj.district_code,current_status=12).count()

        elif User.objects.filter(id=self.context['request'].user.id, user_role__role_name="Agency Admin").exists():
            query_set = Document.objects.filter(digitize_agency_id__in=agency,district_code=obj.district_code,current_status=12).count()

        return query_set
     

    def qc_allocated(self, obj):
        agency = User.objects.filter(id=self.context['request'].user.id).values_list('agency',flat=True)
        if User.objects.filter(id=self.context['request'].user.id, user_role__role_name="Super Admin").exists():
            query_set = Document.objects.filter(district_code=obj.district_code,current_status=13).count()

        elif User.objects.filter(id=self.context['request'].user.id, user_role__role_name="Agency Admin").exists():
            query_set = Document.objects.filter(qc_agency_id__in=agency,district_code=obj.district_code,current_status=13).count()

        return query_set
    
    def qc_inprocess(self, obj):
        agency = User.objects.filter(id=self.context['request'].user.id).values_list('agency',flat=True)
        if User.objects.filter(id=self.context['request'].user.id, user_role__role_name="Super Admin").exists():
            query_set = Document.objects.filter(district_code=obj.district_code,current_status=14).count()

        elif User.objects.filter(id=self.context['request'].user.id, user_role__role_name="Agency Admin").exists():
            query_set = Document.objects.filter(qc_agency_id__in=agency,district_code=obj.district_code,current_status=14).count()

        return query_set
    
    def qc_completed(self, obj):
        agency = User.objects.filter(id=self.context['request'].user.id).values_list('agency',flat=True)
        team_ids = User.objects.filter(id=self.context['request'].user.id).values_list('agency__team', flat=True)

        if User.objects.filter(id=self.context['request'].user.id, user_role__role_name="Super Admin").exists():
            query_set = Document.objects.filter(district_code=obj.district_code,qc_completed_date__isnull=False).count()
        
        elif User.objects.filter(id=self.context['request'].user.id, user_role__role_name="Team Admin").exists():
            query_set =Document.objects.filter(team_id__in=team_ids,district_code=obj.district_code,qc_completed_date__isnull=False).count()
     
        elif User.objects.filter(id=self.context['request'].user.id, user_role__role_name="Agency Admin").exists():
            query_set = Document.objects.filter(qc_agency_id__in=agency,district_code=obj.district_code,qc_completed_date__isnull=False).count()

        return query_set
    
    def qc_rejected(self, obj):
        agency = User.objects.filter(id=self.context['request'].user.id).values_list('agency',flat=True)
        if User.objects.filter(id=self.context['request'].user.id, user_role__role_name="Super Admin").exists():
            query_set = Document.objects.filter(district_code=obj.district_code,current_status=16).count()

        elif User.objects.filter(id=self.context['request'].user.id, user_role__role_name="Agency Admin").exists():
            query_set = Document.objects.filter(qc_agency_id__in=agency,district_code=obj.district_code,current_status=16).count()

        return query_set
    
    def qc_onhold(self, obj):
        agency = User.objects.filter(id=self.context['request'].user.id).values_list('agency',flat=True)
        if User.objects.filter(id=self.context['request'].user.id, user_role__role_name="Super Admin").exists():
            query_set = Document.objects.filter(district_code=obj.district_code,current_status=17).count()

        elif User.objects.filter(id=self.context['request'].user.id, user_role__role_name="Agency Admin").exists():
            query_set = Document.objects.filter(qc_agency_id__in=agency,district_code=obj.district_code,current_status=17).count()

        return query_set
    
    
    def pdf_completed(self, obj):
        agency = User.objects.filter(id=self.context['request'].user.id).values_list('agency',flat=True)
        team_ids = User.objects.filter(id=self.context['request'].user.id).values_list('agency__team', flat=True)

        if User.objects.filter(id=self.context['request'].user.id, user_role__role_name="Super Admin").exists():
            query_set = Document.objects.filter(district_code=obj.district_code,pdf_completed_date__isnull=False).count()
        
        elif User.objects.filter(id=self.context['request'].user.id, user_role__role_name="Team Admin").exists():
            query_set =Document.objects.filter(team_id__in=team_ids,district_code=obj.district_code,pdf_completed_date__isnull=False).count()
     
        elif User.objects.filter(id=self.context['request'].user.id, user_role__role_name="Agency Admin").exists():
            query_set = Document.objects.filter(qc_agency_id__in=agency,district_code=obj.district_code,pdf_completed_date__isnull=False).count()

        return query_set
    
    def shape_completed(self, obj):
        agency = User.objects.filter(id=self.context['request'].user.id).values_list('agency',flat=True)
        team_ids = User.objects.filter(id=self.context['request'].user.id).values_list('agency__team', flat=True)

        if User.objects.filter(id=self.context['request'].user.id, user_role__role_name="Super Admin").exists():
            query_set = Document.objects.filter(district_code=obj.district_code,shape_completed_date__isnull=False).count()
        
        elif User.objects.filter(id=self.context['request'].user.id, user_role__role_name="Team Admin").exists():
            query_set =Document.objects.filter(team_id__in=team_ids,district_code=obj.district_code,shape_completed_date__isnull=False).count()
     
        elif User.objects.filter(id=self.context['request'].user.id, user_role__role_name="Agency Admin").exists():
            query_set = Document.objects.filter(qc_agency_id__in=agency,district_code=obj.district_code,shape_completed_date__isnull=False).count()

        return query_set


class UpdateUserPaginationcountSerialzier(serializers.ModelSerializer):
    class Meta:
        model = PaginationMaster
        fields = "__all__"