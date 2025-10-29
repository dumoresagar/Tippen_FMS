from django.contrib import admin
from django import forms
from import_export.admin import ImportExportModelAdmin
from . import models
# Register your models here.

class MapTypeAdminForm(forms.ModelForm):

    class Meta:
        model = models.MapType
        fields = "__all__"


class MapTypeAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    form =MapTypeAdminForm 
    list_display = [
        "map_code",
        "mapname_english",
        "mapname_marathi",
    ]

class DistrictAdminForm(forms.ModelForm):

    class Meta:
        model = models.District
        fields = "__all__"


class DistrictAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    form =DistrictAdminForm 
    list_display = [
        "district_code",
        "district_name",
    ]

class TalukaAdminForm(forms.ModelForm):

    class Meta:
        model = models.Taluka
        fields = "__all__"


class TalukaAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    form =TalukaAdminForm 
    list_display = [
        "district",
        "taluka_code",
        "taluka_name",
    ]

class VillageAdminForm(forms.ModelForm):

    class Meta:
        model = models.Village
        fields = "__all__"


class VillageAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    form =VillageAdminForm 
    list_display = [
        "taluka",
        "village_code",
        "village_name",
    ]
class DocumentStatusAdminForm(forms.ModelForm):

    class Meta:
        model = models.DocumentStatus
        fields = "__all__"


class DocumentStatusAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    form =DocumentStatusAdminForm 
    list_display = [
        "status",
       
    ]

class DocumentAdminForm(forms.ModelForm):

    class Meta:
        model = models.Document
        fields = "__all__"


class DocumentAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    form =DocumentAdminForm 
    list_display = [
        "id",
        "scan_upload",
        "barcode_number",
        "rectify_agency_id",
        "current_status",
        "polygon_count",
        "remarks",
        "digitize_remarks",
        "qc_remarks",
        "rectify_upload"
       
    ]
    search_fields = ['barcode_number','district_code','village_code','taluka_code']



class PaginationMasterAdminForm(forms.ModelForm):

    class Meta:
        model = models.PaginationMaster
        fields = "__all__"


class PaginationMasterAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    form =PaginationMasterAdminForm 
    list_display = [
        "id",
        "pagination_user",
        "page_size"
       
    ]


class PreScanningDocumentAdminForm(forms.ModelForm):

    class Meta:
        model = models.PreScanningDocument
        fields = "__all__"

class PreScanningDocumentAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    form =PreScanningDocumentAdminForm 
    list_display = [
        "id",
        "district_id",
        "taluka_id",
        "map_type_code",
        "doc_received_count",
        "pre_scanning_count",
        "scanning_complete_count",
        "rescanning_count",
        "document_return",
        "number_of_people_present",
        "document_rejected",
        "mis_date",
        "remark"
       
    ]

    def map_type_code(self, obj):
        return [map_type_code for map_type_code in obj.map_type_code.all()]
    
    map_type_code.allow_tags = True
    map_type_code.short_description = 'map_type_code'

class DistrictTalukaAdminAdminForm(forms.ModelForm):

    class Meta:
        model = models.DistrictTalukaAdmin
        fields = "__all__"

class DistrictTalukaAdminAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    form =DistrictTalukaAdminAdminForm 
    list_display = [
        "id",
        "user_id",
        "district_id",
        "taluka_id"
       
    ]

class TeamDistrictMasterAdminForm(forms.ModelForm):

    class Meta:
        model = models.TeamDistrictMaster
        fields = "__all__"

class TeamDistrictMasterAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    form =TeamDistrictMasterAdminForm 
    list_display = [
        "id",
        "team",
        "district_id"       
    ]
    def district_id(self, obj):
        return [district_id for district_id in obj.district_id.all()]
    
    district_id.allow_tags = True
    district_id.short_description = 'district_id'



class PreDraftingReportAdminForm(forms.ModelForm):

    class Meta:
        model = models.PreDraftingReport
        fields = "__all__"

class PreDraftingReportAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    form =PreDraftingReportAdminForm 
    list_display = [
        "id",
        "district_id",
        "taluka_id",
        "map_type_code",
        "drafting_map_count",
        "correction_uploading_map_count",
        "pre_drafting_date",
        "remark"
       
    ]

    def map_type_code(self, obj):
        return [map_type_code for map_type_code in obj.map_type_code.all()]
    
    map_type_code.allow_tags = True
    map_type_code.short_description = 'map_type_code'

class AgencyInventrydminForm(forms.ModelForm):

    class Meta:
        model = models.AgencyInventry
        fields = "__all__"

class AgencyInventryAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    form =AgencyInventrydminForm 
    list_display = [
        "id",
        "agency_id",
        "allocated_pc",
        "allocated_laptop"
       
    ]

class MissingDocumentAdminForm(forms.ModelForm):
    
    class Meta:
        model = models.MissingDocument
        fields = "__all__"

class MissingDocumentAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    form = MissingDocumentAdminForm
    list_display = [
        "id",
        "barcode_number"
    ]


class TippenDocumentAdminForm(forms.ModelForm):

    class Meta:
        model = models.TippenDocument
        fields = "__all__"


class TippenDocumentAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    form =TippenDocumentAdminForm 
    list_display = [
        "id",
        "tippen_scan_upload",
        "barcode_number",
        "current_status",
        "tippen_polygon_count",
        "tippen_digitize_remarks",
        "tippen_uploaded_by",
        "tippen_digitize_agency_id",
        "tippen_digitize_by",
        "tippen_qc_agency_id",
        "tippen_qc_upload",
        "tippen_qc_by",
        "tippen_qc_remarks",
        "current_status"

       
    ]
    search_fields = ['barcode_number','district_code','village_code','taluka_code']

admin.site.register(models.MapType,MapTypeAdmin)
admin.site.register(models.District,DistrictAdmin)
admin.site.register(models.Taluka,TalukaAdmin)
admin.site.register(models.Village,VillageAdmin)
admin.site.register(models.Document,DocumentAdmin)
admin.site.register(models.DocumentStatus,DocumentStatusAdmin)
admin.site.register(models.Department)
admin.site.register(models.PaginationMaster,PaginationMasterAdmin)
admin.site.register(models.PreScanningDocument,PreScanningDocumentAdmin)
admin.site.register(models.DistrictTalukaAdmin,DistrictTalukaAdminAdmin)
admin.site.register(models.TeamDistrictMaster,TeamDistrictMasterAdmin)
admin.site.register(models.PreDraftingReport,PreDraftingReportAdmin)
admin.site.register(models.AgencyInventry,AgencyInventryAdmin)
admin.site.register(models.MissingDocument,MissingDocumentAdmin)
admin.site.register(models.TippenDocument,TippenDocumentAdmin)
