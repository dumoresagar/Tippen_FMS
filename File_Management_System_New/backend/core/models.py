from django.db import models
from django.utils.translation import gettext_lazy as _
import os
from os.path import splitext
from django.core.files.storage import default_storage

class BaseModelMixin(models.Model):

    """
    Base model mixin. Date of create and date of update and soft-delete
    """

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    is_deleted = False

    class Meta:
        abstract = True

ACTIVE_CHOICES = (
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    )

BEL_STATUS = (
        ('0', '0'),
        ('1', '1'),
        ('2', '2')
    )
class MapType(BaseModelMixin):
    map_code = models.CharField(max_length=30,blank=True, null=True)
    mapname_english = models.CharField(max_length=100,blank=True,null=True)
    mapname_marathi = models.CharField(max_length=100,blank=True,null=True)


    class Meta:
        verbose_name = _("MapType")
        verbose_name_plural = _("MapType")
    
    def __str__(self):
        return f"{self.pk},{self.map_code}"


class District(BaseModelMixin):
    district_code = models.CharField(max_length=30, unique=True, null=True, blank=True)
    district_name = models.CharField(max_length=30,blank=True,null=True)


    class Meta:
        verbose_name = _("District")
        verbose_name_plural = _("District")
    
    def __str__(self):
        return f"{self.pk},{self.district_code},{self.district_name}"


class Taluka(BaseModelMixin):
    district= models.ForeignKey(District,on_delete=models.CASCADE,blank=True,null=True,related_name='district_id')
    taluka_code = models.CharField(max_length=30, unique=True, null=True, blank=True)
    taluka_name = models.CharField(max_length=30,blank=True,null=True)


    class Meta:
        verbose_name = _("Taluka")
        verbose_name_plural = _("Taluka")
    
    def __str__(self):
        return f"{self.pk},{self.taluka_code}"

class Village(BaseModelMixin):
    taluka = models.ForeignKey(Taluka,on_delete=models.CASCADE,blank=True,null=True,related_name='taluka_id')
    village_code = models.CharField(max_length=30, unique=True, null=True, blank=True)
    village_name = models.CharField(max_length=100,blank=True,null=True)


    class Meta:
        verbose_name = _("Village")
        verbose_name_plural = _("Village")
    
    def __str__(self):
        return f"{self.pk},{self.village_code}"
    
class TeamDistrictMaster(BaseModelMixin):
    team = models.ForeignKey('users.TeamMaster',on_delete=models.CASCADE,blank=True,null=True,related_name='team_district')
    district_id = models.ManyToManyField(District,blank=True,related_name='user_department')

    class Meta:
        verbose_name = _("Team District")
        verbose_name_plural = _("Team District")
    
    def __str__(self):
        return f"{self.pk},{self.team}"  
    
class DocumentStatus(BaseModelMixin):
    status = models.CharField(max_length=30,blank=True,null=True)
    class Meta:
        verbose_name = _("Document_Status")
        verbose_name_plural = _("Document_Status")
    
    def __str__(self):
        return f"{self.pk},{self.status}"

class Department(BaseModelMixin):
    department_name = models.CharField(max_length=30,blank=True,null=True)
    created_by = models.CharField(max_length=30,blank=True,null=True)
    active_status = models.CharField(blank=True, default='Active',max_length=8, choices=ACTIVE_CHOICES)
    
    class Meta:
        verbose_name = _("Department")
        verbose_name_plural = _("Department")
    
    def __str__(self):
        return f"{self.pk},{self.department_name}"



def dynamic_scan_upload_path(instance, filename):
    # Extract the district, taluka, and village codes from the filename
    district_code = filename[:3]
    taluka_code = filename[3:7]
    village_code = filename[7:13]
    maptype_code = filename[13:15]

    try:
        # Get the district name from the District model
        district = District.objects.get(district_code=district_code)
        district_name = district.district_name
    except Exception:
        district_name = ''

    try:
        # Get the taluka name from the Taluka model
        taluka = Taluka.objects.get(taluka_code=taluka_code)
        taluka_name = taluka.taluka_name
    except Exception:
        taluka_name = ''

    try:
        # Get the village name from the Village model
        village = Village.objects.get(village_code=village_code)
        village_name = village.village_name
        if '.' in village_name:
            village_name = village_name.replace('.', '')
    except Exception:
        village_name = ''
    
    try:
        # Get the village name from the MapType model
        map_type_code = MapType.objects.get(map_code=maptype_code)
        maptype_name = map_type_code.map_code
    except Exception:
        maptype_name = ''

    # Define the base directory where uploads will be stored
    base_dir = 'uploads'

    # Create the full directory path based on the codes and names
    district_dir = os.path.join(base_dir,"scan", f"{district_code}_{district_name}")
    taluka_dir = os.path.join(district_dir, f"{taluka_code}_{taluka_name}")
    village_dir = os.path.join(taluka_dir, f"{village_code}_{village_name}")
    maptype_dir = os.path.join(village_dir, f"{maptype_code}")

    # Create the directories if they don't exist
    for directory in [base_dir, district_dir, taluka_dir, village_dir, maptype_dir]:
        if not os.path.exists(directory):
            os.makedirs(directory)
        else:
            # If the folder already exists, delete the old file
            old_file_path = os.path.join(maptype_dir, filename)
            if default_storage.exists(old_file_path):
                default_storage.delete(old_file_path)

    # If any of the district, taluka, or village names are empty, save in NotFound folder
    if not district_name or not taluka_name or not village_name or not maptype_name:
        not_found_dir = os.path.join(base_dir, 'NotFound')
        if not os.path.exists(not_found_dir):
            os.makedirs(not_found_dir)
        return os.path.join(not_found_dir, filename)

    # Return the final path for the uploaded file
    return os.path.join(maptype_dir, filename)

def dynamic_rectify_upload_path(instance, filename):
    # Extract the district, taluka, and village codes from the filename
    district_code = filename[:3]
    taluka_code = filename[3:7]
    village_code = filename[7:13]
    maptype_code = filename[13:15]

    try:
        # Get the district name from the District model
        district = District.objects.get(district_code=district_code)
        district_name = district.district_name
    except Exception:
        district_name = ''

    try:
        # Get the taluka name from the Taluka model
        taluka = Taluka.objects.get(taluka_code=taluka_code)
        taluka_name = taluka.taluka_name
    except Exception:
        taluka_name = ''

    try:
        # Get the village name from the Village model
        village = Village.objects.get(village_code=village_code)
        village_name = village.village_name
        if '.' in village_name:
            village_name = village_name.replace('.', '')
    except Exception:
        village_name = ''
    
    try:
        # Get the village name from the MapType model
        map_type_code = MapType.objects.get(map_code=maptype_code)
        maptype_name = map_type_code.map_code
    except Exception:
        maptype_name = ''

    # Define the base directory where uploads will be stored
    base_dir = 'uploads'

    # Create the full directory path based on the codes and names
    district_dir = os.path.join(base_dir,"rectify", f"{district_code}_{district_name}")
    taluka_dir = os.path.join(district_dir, f"{taluka_code}_{taluka_name}")
    village_dir = os.path.join(taluka_dir, f"{village_code}_{village_name}")
    maptype_dir = os.path.join(village_dir, f"{maptype_code}")

    # Create the directories if they don't exist
    for directory in [base_dir, district_dir, taluka_dir, village_dir, maptype_dir]:
        if not os.path.exists(directory):
            os.makedirs(directory)
        else:
            # If the folder already exists, delete the old file
            old_file_path = os.path.join(maptype_dir, filename)
            if default_storage.exists(old_file_path):
                default_storage.delete(old_file_path)

    # If any of the district, taluka, or village names are empty, save in NotFound folder
    if not district_name or not taluka_name or not village_name or not maptype_name:
        not_found_dir = os.path.join(base_dir, 'NotFound')
        if not os.path.exists(not_found_dir):
            os.makedirs(not_found_dir)
        return os.path.join(not_found_dir, filename)

    # Return the final path for the uploaded file
    return os.path.join(maptype_dir, filename)

def dynamic_digitize_upload_path(instance, filename):
    # Extract the district, taluka, and village codes from the filename
    district_code = filename[:3]
    taluka_code = filename[3:7]
    village_code = filename[7:13]
    maptype_code = filename[13:15]

    try:
        # Get the district name from the District model
        district = District.objects.get(district_code=district_code)
        district_name = district.district_name
    except Exception:
        district_name = ''

    try:
        # Get the taluka name from the Taluka model
        taluka = Taluka.objects.get(taluka_code=taluka_code)
        taluka_name = taluka.taluka_name
    except Exception:
        taluka_name = ''

    try:
        # Get the village name from the Village model
        village = Village.objects.get(village_code=village_code)
        village_name = village.village_name
        if '.' in village_name:
            village_name = village_name.replace('.', '')
    except Exception:
        village_name = ''
    
    try:
        # Get the village name from the MapType model
        map_type_code = MapType.objects.get(map_code=maptype_code)
        maptype_name = map_type_code.map_code
    except Exception:
        maptype_name = ''

    # Define the base directory where uploads will be stored
    base_dir = 'uploads'

    # Create the full directory path based on the codes and names
    district_dir = os.path.join(base_dir,"digitize", f"{district_code}_{district_name}")
    taluka_dir = os.path.join(district_dir, f"{taluka_code}_{taluka_name}")
    village_dir = os.path.join(taluka_dir, f"{village_code}_{village_name}")
    maptype_dir = os.path.join(village_dir, f"{maptype_code}")

    # Create the directories if they don't exist
    for directory in [base_dir, district_dir, taluka_dir, village_dir, maptype_dir]:
        if not os.path.exists(directory):
            os.makedirs(directory)
        else:
            # If the folder already exists, delete the old file
            old_file_path = os.path.join(maptype_dir, filename)
            if default_storage.exists(old_file_path):
                default_storage.delete(old_file_path)

    # If any of the district, taluka, or village names are empty, save in NotFound folder
    if not district_name or not taluka_name or not village_name or not maptype_name:
        not_found_dir = os.path.join(base_dir, 'NotFound')
        if not os.path.exists(not_found_dir):
            os.makedirs(not_found_dir)
        return os.path.join(not_found_dir, filename)

    # Return the final path for the uploaded file
    return os.path.join(maptype_dir, filename)

def dynamic_qc_upload_path(instance, filename):
    # Extract the district, taluka, and village codes from the filename
    district_code = filename[:3]
    taluka_code = filename[3:7]
    village_code = filename[7:13]
    maptype_code = filename[13:15]

    try:
        # Get the district name from the District model
        district = District.objects.get(district_code=district_code)
        district_name = district.district_name
    except Exception:
        district_name = ''

    try:
        # Get the taluka name from the Taluka model
        taluka = Taluka.objects.get(taluka_code=taluka_code)
        taluka_name = taluka.taluka_name
    except Exception:
        taluka_name = ''

    try:
        # Get the village name from the Village model
        village = Village.objects.get(village_code=village_code)
        village_name = village.village_name
        if '.' in village_name:
            village_name = village_name.replace('.', '')
    except Exception:
        village_name = ''
    
    try:
        # Get the village name from the MapType model
        map_type_code = MapType.objects.get(map_code=maptype_code)
        maptype_name = map_type_code.map_code
    except Exception:
        maptype_name = ''

    # Define the base directory where uploads will be stored
    base_dir = 'uploads'

    # Create the full directory path based on the codes and names
    district_dir = os.path.join(base_dir,"qc", f"{district_code}_{district_name}")
    taluka_dir = os.path.join(district_dir, f"{taluka_code}_{taluka_name}")
    village_dir = os.path.join(taluka_dir, f"{village_code}_{village_name}")
    maptype_dir = os.path.join(village_dir, f"{maptype_code}")

    # Create the directories if they don't exist
    for directory in [base_dir, district_dir, taluka_dir, village_dir, maptype_dir]:
        if not os.path.exists(directory):
            os.makedirs(directory)
        else:
            # If the folder already exists, delete the old file
            old_file_path = os.path.join(maptype_dir, filename)
            if default_storage.exists(old_file_path):
                default_storage.delete(old_file_path)

    # If any of the district, taluka, or village names are empty, save in NotFound folder
    if not district_name or not taluka_name or not village_name or not maptype_name:
        not_found_dir = os.path.join(base_dir, 'NotFound')
        if not os.path.exists(not_found_dir):
            os.makedirs(not_found_dir)
        return os.path.join(not_found_dir, filename)

    # Return the final path for the uploaded file
    return os.path.join(maptype_dir, filename)

def dynamic_pdf_upload_path(instance, filename):
    # Extract the district, taluka, and village codes from the filename
    district_code = filename[:3]
    taluka_code = filename[3:7]
    village_code = filename[7:13]
    maptype_code = filename[13:15]

    try:
        # Get the district name from the District model
        district = District.objects.get(district_code=district_code)
        district_name = district.district_name
    except Exception:
        district_name = ''

    try:
        # Get the taluka name from the Taluka model
        taluka = Taluka.objects.get(taluka_code=taluka_code)
        taluka_name = taluka.taluka_name
    except Exception:
        taluka_name = ''

    try:
        # Get the village name from the Village model
        village = Village.objects.get(village_code=village_code)
        village_name = village.village_name
        if '.' in village_name:
            village_name = village_name.replace('.', '')
    except Exception:
        village_name = ''
    
    try:
        # Get the village name from the MapType model
        map_type_code = MapType.objects.get(map_code=maptype_code)
        maptype_name = map_type_code.map_code
    except Exception:
        maptype_name = ''

    # Define the base directory where uploads will be stored
    base_dir = 'uploads'

    # Create the full directory path based on the codes and names
    district_dir = os.path.join(base_dir,"pdf", f"{district_code}_{district_name}")
    taluka_dir = os.path.join(district_dir, f"{taluka_code}_{taluka_name}")
    village_dir = os.path.join(taluka_dir, f"{village_code}_{village_name}")
    maptype_dir = os.path.join(village_dir, f"{maptype_code}")

    # Create the directories if they don't exist
    for directory in [base_dir, district_dir, taluka_dir, village_dir, maptype_dir]:
        if not os.path.exists(directory):
            os.makedirs(directory)
        else:
            # If the folder already exists, delete the old file
            old_file_path = os.path.join(maptype_dir, filename)
            if default_storage.exists(old_file_path):
                default_storage.delete(old_file_path)

    # If any of the district, taluka, or village names are empty, save in NotFound folder
    if not district_name or not taluka_name or not village_name or not maptype_name:
        not_found_dir = os.path.join(base_dir, 'NotFound')
        if not os.path.exists(not_found_dir):
            os.makedirs(not_found_dir)
        return os.path.join(not_found_dir, filename)

    # Return the final path for the uploaded file
    return os.path.join(maptype_dir, filename)

def dynamic_shape_upload_path(instance, filename):
    # Extract the district, taluka, and village codes from the filename
    district_code = filename[:3]
    taluka_code = filename[3:7]
    village_code = filename[7:13]
    maptype_code = filename[13:15]

    try:
        # Get the district name from the District model
        district = District.objects.get(district_code=district_code)
        district_name = district.district_name
    except Exception:
        district_name = ''

    try:
        # Get the taluka name from the Taluka model
        taluka = Taluka.objects.get(taluka_code=taluka_code)
        taluka_name = taluka.taluka_name
    except Exception:
        taluka_name = ''

    try:
        # Get the village name from the Village model
        village = Village.objects.get(village_code=village_code)
        village_name = village.village_name
        if '.' in village_name:
            village_name = village_name.replace('.', '')
    except Exception:
        village_name = ''
    
    try:
        # Get the village name from the MapType model
        map_type_code = MapType.objects.get(map_code=maptype_code)
        maptype_name = map_type_code.map_code
    except Exception:
        maptype_name = ''

    # Define the base directory where uploads will be stored
    base_dir = 'uploads'

    # Create the full directory path based on the codes and names
    district_dir = os.path.join(base_dir,"shape", f"{district_code}_{district_name}")
    taluka_dir = os.path.join(district_dir, f"{taluka_code}_{taluka_name}")
    village_dir = os.path.join(taluka_dir, f"{village_code}_{village_name}")
    maptype_dir = os.path.join(village_dir, f"{maptype_code}")

    # Create the directories if they don't exist
    for directory in [base_dir, district_dir, taluka_dir, village_dir, maptype_dir]:
        if not os.path.exists(directory):
            os.makedirs(directory)
        else:
            # If the folder already exists, delete the old file
            old_file_path = os.path.join(maptype_dir, filename)
            if default_storage.exists(old_file_path):
                default_storage.delete(old_file_path)

    # If any of the district, taluka, or village names are empty, save in NotFound folder
    if not district_name or not taluka_name or not village_name or not maptype_name:
        not_found_dir = os.path.join(base_dir, 'NotFound')
        if not os.path.exists(not_found_dir):
            os.makedirs(not_found_dir)
        return os.path.join(not_found_dir, filename)

    # Return the final path for the uploaded file
    return os.path.join(maptype_dir, filename)

def gov_dynamic_upload_path(instance, filename):
    # Extract the district, taluka, and village codes from the filename
    district_code = filename[:3]
    taluka_code = filename[3:7]
    village_code = filename[7:13]
    maptype_code = filename[13:15]

    try:
        # Get the district name from the District model
        district = District.objects.get(district_code=district_code)
        district_name = district.district_name
    except Exception:
        district_name = ''

    try:
        # Get the taluka name from the Taluka model
        taluka = Taluka.objects.get(taluka_code=taluka_code)
        taluka_name = taluka.taluka_name
    except Exception:
        taluka_name = ''

    try:
        # Get the village name from the Village model
        village = Village.objects.get(village_code=village_code)
        village_name = village.village_name
        if '.' in village_name:
            village_name = village_name.replace('.', '')
    except Exception:
        village_name = ''
    
    try:
        # Get the village name from the MapType model
        map_type_code = MapType.objects.get(map_code=maptype_code)
        maptype_name = map_type_code.map_code
    except Exception:
        maptype_name = ''

    # Define the base directory where uploads will be stored
    base_dir = 'uploads'

    # Create the full directory path based on the codes and names
    district_dir = os.path.join(base_dir,"Govt_Approval", f"{district_code}_{district_name}")
    taluka_dir = os.path.join(district_dir, f"{taluka_code}_{taluka_name}")
    village_dir = os.path.join(taluka_dir, f"{village_code}_{village_name}")
    maptype_dir = os.path.join(village_dir, f"{maptype_code}")

    # Create the directories if they don't exist
    for directory in [base_dir, district_dir, taluka_dir, village_dir, maptype_dir]:
        if not os.path.exists(directory):
            os.makedirs(directory)
        else:
            # If the folder already exists, delete the old file
            old_file_path = os.path.join(maptype_dir, filename)
            if default_storage.exists(old_file_path):
                default_storage.delete(old_file_path)

    # If any of the district, taluka, or village names are empty, save in NotFound folder
    if not district_name or not taluka_name or not village_name or not maptype_name:
        not_found_dir = os.path.join(base_dir, 'NotFound')
        if not os.path.exists(not_found_dir):
            os.makedirs(not_found_dir)
        return os.path.join(not_found_dir, filename)

    # Return the final path for the uploaded file
    return os.path.join(maptype_dir, filename)


def dynamic_toplogy_upload_path(instance, filename):
    # Extract the district, taluka, and village codes from the filename
    district_code = filename[:3]
    taluka_code = filename[3:7]
    village_code = filename[7:13]
    maptype_code = filename[13:15]

    try:
        # Get the district name from the District model
        district = District.objects.get(district_code=district_code)
        district_name = district.district_name
    except Exception:
        district_name = ''

    try:
        # Get the taluka name from the Taluka model
        taluka = Taluka.objects.get(taluka_code=taluka_code)
        taluka_name = taluka.taluka_name
    except Exception:
        taluka_name = ''

    try:
        # Get the village name from the Village model
        village = Village.objects.get(village_code=village_code)
        village_name = village.village_name
        if '.' in village_name:
            village_name = village_name.replace('.', '')
    except Exception:
        village_name = ''
    
    try:
        # Get the village name from the MapType model
        map_type_code = MapType.objects.get(map_code=maptype_code)
        maptype_name = map_type_code.map_code
    except Exception:
        maptype_name = ''

    # Define the base directory where uploads will be stored
    base_dir = 'uploads'

    # Create the full directory path based on the codes and names
    district_dir = os.path.join(base_dir,"topology", f"{district_code}_{district_name}")
    taluka_dir = os.path.join(district_dir, f"{taluka_code}_{taluka_name}")
    village_dir = os.path.join(taluka_dir, f"{village_code}_{village_name}")
    maptype_dir = os.path.join(village_dir, f"{maptype_code}")

    # Create the directories if they don't exist
    for directory in [base_dir, district_dir, taluka_dir, village_dir, maptype_dir]:
        if not os.path.exists(directory):
            os.makedirs(directory)
        else:
            # If the folder already exists, delete the old file
            old_file_path = os.path.join(maptype_dir, filename)
            if default_storage.exists(old_file_path):
                default_storage.delete(old_file_path)

    # If any of the district, taluka, or village names are empty, save in NotFound folder
    if not district_name or not taluka_name or not village_name or not maptype_name:
        not_found_dir = os.path.join(base_dir, 'NotFound')
        if not os.path.exists(not_found_dir):
            os.makedirs(not_found_dir)
        return os.path.join(not_found_dir, filename)

    # Return the final path for the uploaded file
    return os.path.join(maptype_dir, filename)


class Document(BaseModelMixin):
    team_id = models.ForeignKey('users.TeamMaster',on_delete=models.CASCADE,blank=True,null=True,related_name='document_team_id')
    agency_id = models.ForeignKey('users.Agency',on_delete=models.CASCADE,blank=True,null=True,related_name='agency_document')
    scan_upload = models.FileField(upload_to=dynamic_scan_upload_path,blank=True,null=True)
    barcode_number = models.CharField(max_length=25, unique=True,null=True, blank=True)
    file_name = models.CharField(max_length=30, null=True, blank=True)
    district_code = models.CharField(max_length=5, null=True, blank=True)
    village_code = models.CharField(max_length=7, null=True, blank=True)
    taluka_code = models.CharField(max_length=7, null=True, blank=True)
    map_code = models.CharField(max_length=5, null=True, blank=True)
    scan_uploaded_by = models.ForeignKey('users.User',on_delete=models.CASCADE,blank=True,null=True,related_name="scanby_user")
    scan_uploaded_date = models.DateTimeField(blank=True,null=True)
    rectify_agency_id = models.ForeignKey('users.Agency',on_delete=models.CASCADE,blank=True,null=True,related_name='rectify_agency_id')
    rectify_upload = models.FileField(upload_to=dynamic_rectify_upload_path,blank=True,null=True)
    rectify_by =models.ForeignKey('users.User',on_delete=models.CASCADE,blank=True,null=True,related_name="rectifyby_user")
    rectify_assign_date = models.DateTimeField(blank=True,null=True)
    rectify_completed_date = models.DateTimeField(blank=True,null=True)
    digitize_agency_id = models.ForeignKey('users.Agency',on_delete=models.CASCADE,blank=True,null=True,related_name='digitize_agency_id')
    digitize_upload = models.FileField(upload_to=dynamic_digitize_upload_path,blank=True,null=True)
    digitize_by = models.ForeignKey('users.User',on_delete=models.CASCADE,blank=True,null=True,related_name="digitizeby_user")
    polygon_count = models.IntegerField(blank=True,default=0)
    qc_polygon_count = models.IntegerField(blank=True,default=0)
    digitize_assign_date = models.DateTimeField(blank=True,null=True)
    digitize_completed_date = models.DateTimeField(blank=True,null=True)
    qc_agency_id = models.ForeignKey('users.Agency',on_delete=models.CASCADE,blank=True,null=True,related_name='qc_agency_id')
    qc_upload = models.FileField(upload_to=dynamic_qc_upload_path,blank=True,null=True)
    qc_by = models.ForeignKey('users.User',on_delete=models.CASCADE,blank=True,null=True,related_name="qcby_user")
    qc_assign_date = models.DateTimeField(blank=True,null=True)
    qc_completed_date = models.DateTimeField(blank=True,null=True)
    pdf_upload = models.FileField(upload_to=dynamic_pdf_upload_path,blank=True,null=True)
    pdf_by = models.ForeignKey('users.User',on_delete=models.CASCADE,blank=True,null=True,related_name="pdfby_user")
    pdf_assign_date = models.DateTimeField(blank=True,null=True)
    pdf_completed_date = models.DateTimeField(blank=True,null=True)
    shape_agency_id = models.ForeignKey('users.Agency',on_delete=models.CASCADE,blank=True,null=True,related_name='shape_agency_id')
    shape_upload = models.FileField(upload_to=dynamic_shape_upload_path,blank=True,null=True)
    shape_by = models.ForeignKey('users.User',on_delete=models.CASCADE,blank=True,null=True,related_name="shapeby_user")
    shape_assign_date = models.DateTimeField(blank=True,null=True)
    shape_completed_date = models.DateTimeField(blank=True,null=True)
    gov_approve_agency_id = models.ForeignKey('users.Agency',on_delete=models.CASCADE,blank=True,null=True,related_name='gov_approve_agency_id')
    gov_qc_upload = models.FileField(upload_to=gov_dynamic_upload_path,blank=True,null=True,max_length=255)
    gov_pdf_upload = models.FileField(upload_to=gov_dynamic_upload_path,blank=True,null=True,max_length=255)
    gov_qc_by = models.ForeignKey('users.User',on_delete=models.CASCADE,blank=True,null=True,related_name="gov_qc_by")
    gov_qc_assign_date = models.DateTimeField(blank=True,null=True)
    gov_qc_completed_date = models.DateTimeField(blank=True,null=True)
    gov_pdf_completed_date = models.DateTimeField(blank=True,null=True)
    current_status = models.ForeignKey(DocumentStatus,on_delete=models.CASCADE,blank=True,null=True)
    remarks = models.CharField(max_length=200, null=True, blank=True)
    digitize_remarks = models.CharField(max_length=200, null=True, blank=True)
    qc_remarks = models.CharField(max_length=200, null=True, blank=True)
    bel_scan_uploaded = models.BooleanField(default=False,blank=True, null=True)
    bel_draft_uploaded = models.BooleanField(default=False,blank=True, null=True)
    bel_gov_scan_qc_approved = models.BooleanField(default=False,blank=True, null=True)
    bel_gov_draft_qc_approved = models.BooleanField(default=False,blank=True, null=True)
    chk_bel_scan_uploaded = models.CharField(max_length=2, default='0',choices=BEL_STATUS, blank=True)
    chk_bel_draft_uploaded = models.CharField(max_length=2,default='0',choices=BEL_STATUS, blank=True)
    chk_bel_gov_scan_qc_approved = models.CharField(max_length=2,default='0',choices=BEL_STATUS, blank=True)
    chk_bel_gov_draft_qc_approved = models.CharField(max_length=2, default='0',choices=BEL_STATUS, blank=True)
    drafting_topology = models.BooleanField(default=False,blank=True,null=True)
    drafting_qc_topology = models.BooleanField(default=False,blank=True,null=True)
    topology_agency_id = models.ForeignKey('users.Agency',on_delete=models.CASCADE,blank=True,null=True,related_name='topology_agency_id')
    toplogy_upload = models.FileField(upload_to=dynamic_toplogy_upload_path,blank=True,null=True)
    topology_by = models.ForeignKey('users.User',on_delete=models.CASCADE,blank=True,null=True,related_name="topology_by")
    topology_assign_date = models.DateTimeField(blank=True,null=True)
    topology_completed_date = models.DateTimeField(blank=True,null=True)
    class Meta:
        verbose_name = _("Document")
        verbose_name_plural = _("Document")
    
    def __str__(self):
        return f"{self.pk}"
    
    def save(self, *args, **kwargs):
        if self.scan_upload:
            filename = self.scan_upload.name
            # Check if the fields are already set
            if not self.barcode_number:
                base_filename, _ = os.path.splitext(filename)
                self.barcode_number = base_filename.split("_")[0]
            if not self.file_name:
                self.file_name = filename
            if not self.district_code:
                self.district_code = filename[:3]
            if not self.village_code:
                self.village_code = filename[7:13]
            if not self.taluka_code:
                self.taluka_code = filename[3:7]
            if not self.map_code:
                self.map_code = filename[13:15]
        super(Document, self).save(*args, **kwargs)



class PaginationMaster(BaseModelMixin):
    pagination_user = models.ForeignKey('users.User',on_delete=models.CASCADE,blank=True,null=True,related_name="pagination_user")
    page_size = models.IntegerField(blank=True,null=True, default=20)

    class Meta:
        verbose_name = _("Pagination Master")
        verbose_name_plural = _("Pagination Master")
    
    def __str__(self):
        return f"{self.pk}"
    

class PreScanningDocument(BaseModelMixin):
    district_id = models.ForeignKey(District,on_delete=models.CASCADE,blank=True,null=True,related_name="prescan_district_id")
    taluka_id = models.ForeignKey(Taluka,on_delete=models.CASCADE,blank=True,null=True,related_name="prescan_taluka_id")
    map_type_code = models.ManyToManyField(MapType,blank=True,related_name='prescan_maptype_code')
    doc_received_count = models.IntegerField(blank=True,null=True)
    pre_scanning_count = models.IntegerField(blank=True,null=True)
    scanning_complete_count = models.IntegerField(blank=True,null=True)
    rescanning_count = models.IntegerField(blank=True,null=True)
    document_return = models.IntegerField(blank=True,null=True)
    number_of_people_present = models.IntegerField(blank=True,null=True)
    document_rejected = models.IntegerField(blank=True,null=True)
    mis_date = models.DateField(blank=True,null=True)
    remark = models.CharField(max_length=100,blank=True,null=True)



    class Meta:
        verbose_name = _("PreScanning Document")
        verbose_name_plural = _("PreScanning Document")
    
    def __str__(self):
        return f"{self.pk}"


class DistrictTalukaAdmin(BaseModelMixin):
    user_id = models.ForeignKey('users.User',on_delete=models.CASCADE,blank=True,null=True,related_name="admin_user")                                                                                                                
    district_id = models.ForeignKey(District,on_delete=models.CASCADE,blank=True,null=True,related_name="admin_district_id")
    taluka_id = models.ForeignKey(Taluka,on_delete=models.CASCADE,blank=True,null=True,related_name="admin_taluka_id")    



    class Meta:
        verbose_name = _("District Taluka Admin")
        verbose_name_plural = _("District Taluka Admin")
    
    def __str__(self):
        return f"{self.pk}" 
    

class PreDraftingReport(BaseModelMixin):
    district_id = models.ForeignKey(District,on_delete=models.CASCADE,blank=True,null=True,related_name="predrafting_district_id")
    taluka_id = models.ForeignKey(Taluka,on_delete=models.CASCADE,blank=True,null=True,related_name="predrafting_taluka_id")
    map_type_code = models.ManyToManyField(MapType,blank=True,related_name='predrafting_maptype_code')
    drafting_map_count = models.IntegerField(blank=True,null=True)
    correction_uploading_map_count = models.IntegerField(blank=True,null=True)
    pre_drafting_date = models.DateField(blank=True,null=True)
    remark = models.CharField(max_length=100,blank=True,null=True)

    class Meta:
        verbose_name = _("Pre-Drafting Report")
        verbose_name_plural = _("Pre-Drafting Report")
    
    def __str__(self):
        return f"{self.pk}"
    

class AgencyInventry(BaseModelMixin):
    agency_id = models.ForeignKey('users.Agency',on_delete=models.CASCADE,blank=True,null=True,related_name='agency_inventry_id')
    allocated_pc =  models.IntegerField(blank=True,null=True)
    allocated_laptop =  models.IntegerField(blank=True,null=True)

    class Meta:
        verbose_name = _("Agency Inventry")
        verbose_name_plural = _("Agency Inventry")

    def __str__(self):
        return f"{self.id}"
    
class MissingDocument(BaseModelMixin):
    barcode_number = models.CharField(max_length=25, unique=True,null=True, blank=True)
    bel_current_status = models.CharField(max_length=30,null=True, blank=True)


    class Meta:
        verbose_name = _("Missing Document")
        verbose_name_plural = _("Missing Document")

    def __str__(self):
        return f"{self.id}"

##########################################################################
 
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image
import json
from urllib.parse import quote
from django.conf import settings
from django.db.models import JSONField

import uuid

Asset_Type = (
        ('sanitizedType', 'sanitizedType'),
        ('tentageType', 'tentageType')
    )

Vendor = (
        ('Vendor 1', 'Vendor 1'),
        ('Vendor 2', 'Vendor 2'),
        ('Vendor 3', 'Vendor 3'),
        ('Vendor 4', 'Vendor 4'),
        ('Vendor 5', 'Vendor 5'),
        ('Vendor 6', 'Vendor 6'),
    )

class KumbhAsset(BaseModelMixin):
    asset_name = models.CharField(max_length=30,null=True,blank=True)
    asset_code = models.CharField(max_length=30,null=True,blank=True)
    asset_desc = models.TextField(null=True,blank=True)
    asset_type = models.CharField(blank=True, default='',max_length=30, choices=Asset_Type)
    vendor =models.CharField(blank=True, default='',max_length=30, choices=Vendor)
    qr_code = models.ImageField(null=True,blank=True)
    asset_image = models.ImageField(null=True,blank=True)
    geo_latitude= models.CharField(max_length=30,null=True,blank=True)
    geo_longitute = models.CharField(max_length=30,null=True,blank=True)
    sector_no = models.CharField(max_length=30,null=True,blank=True)

    class Meta:
        verbose_name = _("Kumbh Asset")
        verbose_name_plural = _("Kumbh Asset")

    def __str__(self):
        return f"{self.id}"
    
    # def save(self, *args, **kwargs):
    #     request = kwargs.pop('request', None)  # Pop the request if passed
    #     if not self.asset_code:
    #         super(KumbhAsset, self).save(*args, **kwargs)
    #         self.asset_code = f"ASSET-{self.id}"

    #     # Prepare the data in JSON format with full URLs
    #     if request:
    #         asset_image_url = request.build_absolute_uri(self.asset_image.url) if self.asset_image else ''
    #         qr_code_url = request.build_absolute_uri(self.qr_code.url) if self.qr_code else ''
    #     else:
    #         asset_image_url = f"http://192.168.1.141:8001{quote(self.asset_image.url)}" if self.asset_image else ''
    #         qr_code_url = f"http://192.168.1.141:8001{quote(self.qr_code.url)}" if self.qr_code else ''

    #     qr_data = json.dumps({
    #         "assets_id": self.id or '',
    #         "assets_name": self.asset_name or '',
    #         "assets_code": self.asset_code or '',
    #         "assets_photo": asset_image_url,
    #         "assets_qr_code": qr_code_url,
    #         "assets_description": self.asset_desc or '',
    #         "asset_type": self.asset_type or '',
    #         "assets_vendor": self.vendor or '',
    #         "assets_latitude": self.geo_latitude or '',
    #         "assets_longitude": self.geo_longitute or '',
    #         "sector_no": self.sector_no or ''
    #     })

    #     qr = qrcode.QRCode(
    #         version=1,
    #         error_correction=qrcode.constants.ERROR_CORRECT_L,
    #         box_size=10,
    #         border=4,
    #     )
    #     qr.add_data(qr_data)
    #     qr.make(fit=True)

    #     img = qr.make_image(fill_color="black", back_color="white")

    #     img_io = BytesIO()
    #     img.save(img_io, format='PNG')
    #     img_io.seek(0)
    #     self.qr_code.save(f"{self.asset_code}.png", File(img_io), save=False)

    #     super(KumbhAsset, self).save(*args, **kwargs)


    def generate_unique_asset_code(self):
        """Generate a unique asset code."""
        while True:
            asset_code = f"ASSET-{uuid.uuid4().hex[:8].upper()}"
            if not KumbhAsset.objects.filter(asset_code=asset_code).exists():
                return asset_code

    def save(self, *args, **kwargs):
        # Ensure asset_code is unique and set
        if not self.asset_code:
            self.asset_code = self.generate_unique_asset_code()

        # Only save QR code if it does not already exist
        if not self.pk:  # If this is a new instance
            super(KumbhAsset, self).save(*args, **kwargs)

        # Prepare the data in JSON format with full URLs
        asset_image_url = self.asset_image.url if self.asset_image else ''
        qr_code_url = self.qr_code.url if self.qr_code else ''
        
        qr_data = json.dumps({
            "assets_id": self.id or '',
            "assets_name": self.asset_name or '',
            "assets_code": self.asset_code or '',
            "assets_photo": asset_image_url,
            "assets_qr_code": qr_code_url,
            "assets_description": self.asset_desc or '',
            "asset_type": self.asset_type or '',
            "assets_vendor": self.vendor or '',
            "assets_latitude": self.geo_latitude or '',
            "assets_longitude": self.geo_longitute or '',
            "sector_no": self.sector_no or ''
        })

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        img_io = BytesIO()
        img.save(img_io, format='PNG')
        img_io.seek(0)

        if not self.qr_code:
            self.qr_code.save(f"{self.asset_code}.png", File(img_io), save=False)

        # Save again to ensure qr_code is saved properly
        if not self.pk:
            super(KumbhAsset, self).save(*args, **kwargs)

class JsonDataMaster(BaseModelMixin):
    asset_id = models.IntegerField(blank=True,default=0)
    assetdata = JSONField(blank=True)
    

    class Meta:
        verbose_name = _("Asset Quetions Answer")
        verbose_name_plural =_("Asset Quetions Answer")

    def __str__(self):
        return f"{self.pk}"



class Complaint(BaseModelMixin):
    complaint_number = models.CharField(max_length=100,blank=True,null=True)
    image_url = models.ImageField(upload_to='data/known_faces', blank=True, null=True)

    class Meta:
        verbose_name = _("Complaint")
        verbose_name_plural = _("Complaint")
    
    def __str__(self):
        return f"{self.pk}"
    
    def save(self, *args, **kwargs):
        if self.image_url and self.complaint_number:
            # Get the file extension
            file_extension = os.path.splitext(self.image_url.name)[1]
            # Set the image URL with complaint_number as filename
            self.image_url.name = f"{self.complaint_number}{file_extension}"
        super(Complaint, self).save(*args, **kwargs)


def dynamic_tippen_scan_upload_path(instance, filename):
    # Extract the district, taluka, and village codes from the filename
    district_code = filename[:3]
    taluka_code = filename[3:7]
    village_code = filename[7:13]
    maptype_code = filename[13:15]

    try:
        # Get the district name from the District model
        district = District.objects.get(district_code=district_code)
        district_name = district.district_name
    except Exception:
        district_name = ''

    try:
        # Get the taluka name from the Taluka model
        taluka = Taluka.objects.get(taluka_code=taluka_code)
        taluka_name = taluka.taluka_name
    except Exception:
        taluka_name = ''

    try:
        # Get the village name from the Village model
        village = Village.objects.get(village_code=village_code)
        village_name = village.village_name
        if '.' in village_name:
            village_name = village_name.replace('.', '')
    except Exception:
        village_name = ''
    
    try:
        # Get the village name from the MapType model
        map_type_code = MapType.objects.get(map_code=maptype_code)
        maptype_name = map_type_code.map_code
    except Exception:
        maptype_name = ''

    # Define the base directory where uploads will be stored
    base_dir = 'uploads'

    # Create the full directory path based on the codes and names
    district_dir = os.path.join(base_dir,"TippenScan", f"{district_code}_{district_name}")
    taluka_dir = os.path.join(district_dir, f"{taluka_code}_{taluka_name}")
    village_dir = os.path.join(taluka_dir, f"{village_code}_{village_name}")
    maptype_dir = os.path.join(village_dir, f"{maptype_code}")

    # Create the directories if they don't exist
    for directory in [base_dir, district_dir, taluka_dir, village_dir, maptype_dir]:
        if not os.path.exists(directory):
            os.makedirs(directory)
        else:
            # If the folder already exists, delete the old file
            old_file_path = os.path.join(maptype_dir, filename)
            if default_storage.exists(old_file_path):
                default_storage.delete(old_file_path)

    # If any of the district, taluka, or village names are empty, save in NotFound folder
    if not district_name or not taluka_name or not village_name or not maptype_name:
        not_found_dir = os.path.join(base_dir, 'TippenNotFound')
        if not os.path.exists(not_found_dir):
            os.makedirs(not_found_dir)
        return os.path.join(not_found_dir, filename)

    # Return the final path for the uploaded file
    return os.path.join(maptype_dir, filename)

def dynamic_tippen_digitize_upload_path(instance, filename):
    # Extract the district, taluka, and village codes from the filename
    district_code = filename[:3]
    taluka_code = filename[3:7]
    village_code = filename[7:13]
    maptype_code = filename[13:15]

    try:
        # Get the district name from the District model
        district = District.objects.get(district_code=district_code)
        district_name = district.district_name
    except Exception:
        district_name = ''

    try:
        # Get the taluka name from the Taluka model
        taluka = Taluka.objects.get(taluka_code=taluka_code)
        taluka_name = taluka.taluka_name
    except Exception:
        taluka_name = ''

    try:
        # Get the village name from the Village model
        village = Village.objects.get(village_code=village_code)
        village_name = village.village_name
        if '.' in village_name:
            village_name = village_name.replace('.', '')
    except Exception:
        village_name = ''
    
    try:
        # Get the village name from the MapType model
        map_type_code = MapType.objects.get(map_code=maptype_code)
        maptype_name = map_type_code.map_code
    except Exception:
        maptype_name = ''

    # Define the base directory where uploads will be stored
    base_dir = 'uploads'

    # Create the full directory path based on the codes and names
    district_dir = os.path.join(base_dir,"TippenDigitize", f"{district_code}_{district_name}")
    taluka_dir = os.path.join(district_dir, f"{taluka_code}_{taluka_name}")
    village_dir = os.path.join(taluka_dir, f"{village_code}_{village_name}")
    maptype_dir = os.path.join(village_dir, f"{maptype_code}")

    # Create the directories if they don't exist
    for directory in [base_dir, district_dir, taluka_dir, village_dir, maptype_dir]:
        if not os.path.exists(directory):
            os.makedirs(directory)
        else:
            # If the folder already exists, delete the old file
            old_file_path = os.path.join(maptype_dir, filename)
            if default_storage.exists(old_file_path):
                default_storage.delete(old_file_path)

    # If any of the district, taluka, or village names are empty, save in NotFound folder
    if not district_name or not taluka_name or not village_name or not maptype_name:
        not_found_dir = os.path.join(base_dir, 'TippenNotFound')
        if not os.path.exists(not_found_dir):
            os.makedirs(not_found_dir)
        return os.path.join(not_found_dir, filename)

    # Return the final path for the uploaded file
    return os.path.join(maptype_dir, filename)

def dynamic_tippen_qc_upload_path(instance, filename):
    # Extract the district, taluka, and village codes from the filename
    district_code = filename[:3]
    taluka_code = filename[3:7]
    village_code = filename[7:13]
    maptype_code = filename[13:15]

    try:
        # Get the district name from the District model
        district = District.objects.get(district_code=district_code)
        district_name = district.district_name
    except Exception:
        district_name = ''

    try:
        # Get the taluka name from the Taluka model
        taluka = Taluka.objects.get(taluka_code=taluka_code)
        taluka_name = taluka.taluka_name
    except Exception:
        taluka_name = ''

    try:
        # Get the village name from the Village model
        village = Village.objects.get(village_code=village_code)
        village_name = village.village_name
        if '.' in village_name:
            village_name = village_name.replace('.', '')
    except Exception:
        village_name = ''
    
    try:
        # Get the village name from the MapType model
        map_type_code = MapType.objects.get(map_code=maptype_code)
        maptype_name = map_type_code.map_code
    except Exception:
        maptype_name = ''

    # Define the base directory where uploads will be stored
    base_dir = 'uploads'

    # Create the full directory path based on the codes and names
    district_dir = os.path.join(base_dir,"TippenQC", f"{district_code}_{district_name}")
    taluka_dir = os.path.join(district_dir, f"{taluka_code}_{taluka_name}")
    village_dir = os.path.join(taluka_dir, f"{village_code}_{village_name}")
    maptype_dir = os.path.join(village_dir, f"{maptype_code}")

    # Create the directories if they don't exist
    for directory in [base_dir, district_dir, taluka_dir, village_dir, maptype_dir]:
        if not os.path.exists(directory):
            os.makedirs(directory)
        else:
            # If the folder already exists, delete the old file
            old_file_path = os.path.join(maptype_dir, filename)
            if default_storage.exists(old_file_path):
                default_storage.delete(old_file_path)

    # If any of the district, taluka, or village names are empty, save in NotFound folder
    if not district_name or not taluka_name or not village_name or not maptype_name:
        not_found_dir = os.path.join(base_dir, 'TippenNotFound')
        if not os.path.exists(not_found_dir):
            os.makedirs(not_found_dir)
        return os.path.join(not_found_dir, filename)

    # Return the final path for the uploaded file
    return os.path.join(maptype_dir, filename)


def dynamic_backupfile_upload_path(instance, filename):
    # Extract the district, taluka, and village codes from the filename
    district_code = filename[:3]
    taluka_code = filename[3:7]
    village_code = filename[7:13]
    maptype_code = filename[13:15]

    try:
        # Get the district name from the District model
        district = District.objects.get(district_code=district_code)
        district_name = district.district_name
    except Exception:
        district_name = ''

    try:
        # Get the taluka name from the Taluka model
        taluka = Taluka.objects.get(taluka_code=taluka_code)
        taluka_name = taluka.taluka_name
    except Exception:
        taluka_name = ''

    try:
        # Get the village name from the Village model
        village = Village.objects.get(village_code=village_code)
        village_name = village.village_name
        if '.' in village_name:
            village_name = village_name.replace('.', '')
    except Exception:
        village_name = ''
    
    try:
        # Get the village name from the MapType model
        map_type_code = MapType.objects.get(map_code=maptype_code)
        maptype_name = map_type_code.map_code
    except Exception:
        maptype_name = ''

    # Define the base directory where uploads will be stored
    base_dir = 'uploads'

    # Create the full directory path based on the codes and names
    district_dir = os.path.join(base_dir,"BackupFile", f"{district_code}_{district_name}")
    taluka_dir = os.path.join(district_dir, f"{taluka_code}_{taluka_name}")
    village_dir = os.path.join(taluka_dir, f"{village_code}_{village_name}")
    maptype_dir = os.path.join(village_dir, f"{maptype_code}")

    # Create the directories if they don't exist
    for directory in [base_dir, district_dir, taluka_dir, village_dir, maptype_dir]:
        if not os.path.exists(directory):
            os.makedirs(directory)
        else:
            # If the folder already exists, delete the old file
            old_file_path = os.path.join(maptype_dir, filename)
            if default_storage.exists(old_file_path):
                default_storage.delete(old_file_path)

    # If any of the district, taluka, or village names are empty, save in NotFound folder
    if not district_name or not taluka_name or not village_name or not maptype_name:
        not_found_dir = os.path.join(base_dir, 'TippenNotFound')
        if not os.path.exists(not_found_dir):
            os.makedirs(not_found_dir)
        return os.path.join(not_found_dir, filename)

    # Return the final path for the uploaded file
    return os.path.join(maptype_dir, filename)

class TippenDocument(BaseModelMixin):
    tippen_scan_upload = models.FileField(upload_to=dynamic_tippen_scan_upload_path,blank=True,null=True)
    barcode_number = models.CharField(max_length=25, unique=True,null=True, blank=True)
    file_name = models.CharField(max_length=30, null=True, blank=True)
    district_code = models.CharField(max_length=5, null=True, blank=True)
    village_code = models.CharField(max_length=7, null=True, blank=True)
    taluka_code = models.CharField(max_length=7, null=True, blank=True)
    map_code = models.CharField(max_length=5, null=True, blank=True)
    tippen_uploaded_by = models.ForeignKey('users.User',on_delete=models.CASCADE,blank=True,null=True,related_name="tippenby_user")
    tippen_uploaded_date = models.DateTimeField(blank=True,null=True)
    tippen_digitize_agency_id = models.ForeignKey('users.Agency',on_delete=models.CASCADE,blank=True,null=True,related_name='tippendigitize_agency_id')
    tippen_digitize_upload = models.FileField(upload_to=dynamic_tippen_digitize_upload_path,blank=True,null=True)
    backup_file_upload = models.FileField(upload_to=dynamic_backupfile_upload_path,blank=True,null=True)
    tippen_digitize_by = models.ForeignKey('users.User',on_delete=models.CASCADE,blank=True,null=True,related_name="tippendigitizeby_user")
    tippen_polygon_count = models.IntegerField(blank=True,default=0)
    tippen_digitize_assign_date = models.DateTimeField(blank=True,null=True)
    tippen_digitize_completed_date = models.DateTimeField(blank=True,null=True)
    tippen_qc_agency_id = models.ForeignKey('users.Agency',on_delete=models.CASCADE,blank=True,null=True,related_name='tippenqc_agency_id')
    tippen_qc_upload = models.FileField(upload_to=dynamic_tippen_qc_upload_path,blank=True,null=True)
    tippen_qc_by = models.ForeignKey('users.User',on_delete=models.CASCADE,blank=True,null=True,related_name="tippenqcby_user")
    tippen_qc_assign_date = models.DateTimeField(blank=True,null=True)
    tippen_qc_completed_date = models.DateTimeField(blank=True,null=True)
    tippen_remarks = models.CharField(max_length=200, null=True, blank=True)
    current_status = models.ForeignKey(DocumentStatus,on_delete=models.CASCADE,blank=True,null=True)

    
    
    
    
    class Meta:
        verbose_name = _("Tippen Document")
        verbose_name_plural = _("Tippen Document")
    
    def __str__(self):
        return f"{self.pk}"
    
    def save(self, *args, **kwargs):
        if self.tippen_scan_upload:
            filename = self.tippen_scan_upload.name
            # Check if the fields are already set
            if not self.barcode_number:
                base_filename, _ = os.path.splitext(filename)
                self.barcode_number = base_filename.split("_")[0]
            if not self.file_name:
                self.file_name = filename
            if not self.district_code:
                self.district_code = filename[:3]
            if not self.village_code:
                self.village_code = filename[7:13]
            if not self.taluka_code:
                self.taluka_code = filename[3:7]
            if not self.map_code:
                self.map_code = filename[13:15]
        super(TippenDocument, self).save(*args, **kwargs)

