# from django.test import TestCase

# # Create your tests here.
#  if action == 'approved':
#             data = request.FILES.getlist('files')
#             total_len = 0

#             for file in data:
#                 filename = file.name
#                 base_filename,file_extension = os.path.splitext(filename)
#                 code = base_filename.split("_")[0]

#                 try:
#                     # Get the existing object based on the barcode
#                     obj = Document.objects.get(barcode_number=code,scan_uploaded_date__isnull=False,current_status__in=[1,3,4,7,11])
#                     new_filename = f"{base_filename}{file_extension}"


#                     # Create a SimpleUploadedFile with the file data
#                     uploaded_file = SimpleUploadedFile(name=new_filename, content=file.read())

#                     # Create a dictionary with the data to update
#                     rectify_obj = self.request.user.id
#                     rectify_agency_id = self.request.user.agency.id
#                     agency_team_id = self.request.user.agency.team.id
#                     completed_date = datetime.now()
#                     if obj.current_status.id == 11:
#                         update_data = {
#                             'rectify_agency_id': rectify_agency_id,
#                             'team_id': agency_team_id,
#                             'rectify_upload': uploaded_file,  # Pass the uploaded file data
#                             "rectify_by": rectify_obj,
#                             "rectify_completed_date": completed_date,
#                             "current_status": 31
#                         }
#                     else:
#                         update_data = {
#                             'rectify_agency_id': rectify_agency_id,
#                             'team_id': agency_team_id,
#                             'rectify_upload': uploaded_file,  # Pass the uploaded file data
#                             "rectify_by": rectify_obj,
#                             "rectify_completed_date": completed_date,
#                             "current_status": 5
#                         }


#                     serializer = self.get_serializer(obj, data=update_data, partial=True)
#                     if serializer.is_valid():
#                         serializer.save()
#                         total_len += 1
#                     else:
#                         print(f"Error validating data for code {code}: {serializer.errors}")

#                 except Document.DoesNotExist:
#                     print(f"Object with barcode {code} does not exist.")

#             return Response({"message": f"{total_len} Rectify Files Updated"}, status=status.HTTP_200_OK)
