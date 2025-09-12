from django.urls import path
from .api import *


app_name = "document"

urlpatterns = [
    path("scan-upload-document/", UploadScanDocumentGenericAPI.as_view(), name="scan-upload-document"),
    path("rectify-upload-document/<int:pk>/", UploadRectifyDocumentGenericAPI.as_view(), name="rectify-upload-document"),
    path("digitize-upload-document/<int:pk>/", UploadDigitizeDocumentGenericAPI.as_view(), name="digitize-upload-document"),
    path("qc-upload-document/<int:pk>/", UploadQcDocumentGenericAPI.as_view(), name="qc-upload-document"),
    path("pdf-upload-document/<int:pk>/", UploadPdfDocumentGenericAPI.as_view(), name="pdf-upload-document"),
    path("shape-upload-document/<int:pk>/", UploadShapeDocumentGenericAPI.as_view(), name="shape-upload-document"),

    
    path("user-list/", UserListView.as_view(), name="user-list"),#
    path("agency-list/", AgencyListView.as_view(), name="agency-list"),#
    path("agency-wise-user-list/", AgencyWiseListView.as_view(), name="agency-wise-user-list"),#

    path("scan-document-list/", ScanDocumentListView.as_view(), name="scan-document-list"),
    path("rectify-document-list/", ScanRectifyListView.as_view(), name="rectify-document-list"),
    path("digitize-document-list/", ScanDigitizeListView.as_view(), name="digitize-document-list"),#
    path("qc-document-list/", ScanQcListView.as_view(), name="qc-document-list"),#
    path("pdf-document-list/", ScanPdfListView.as_view(), name="pdf-document-list"),#
    path("notfound-scan-document-list/", NotFoundScanDocumentListView.as_view(), name="notfound-scan-document-list"),

    path("rectify-bulk/", UpdateFileCreateView.as_view(),name="rectify-bulk"),
    path("scan-upload-bulk/", ScanUploadDocumentView.as_view(),name="scan-upload-bulk"),
    path("digitize-upload-bulk/", UploadDigitizeView.as_view(),name="digitize-upload-bulk"),
    path("qc-upload-bulk/", UploadQcView.as_view(),name="qc-upload-bulk"),
    path("pdf-upload-bulk/", UploadPdfView.as_view(),name="pdf-upload-bulk"),#
    path("shape-upload-bulk/", UploadShapeView.as_view(),name="shape-upload-bulk"),#

    path("re-scan-upload-bulk/", ReuploadScanFileCreateView.as_view(), name="re-scan-upload-bulk"),
    path("rectify-bulk/<str:action>/", UpdateRectifyFileCreateView.as_view(),name="rectify-bulk"),
    path("digitize-upload-bulk/<str:action>/", UpdateDigitizeFileCreateView.as_view(),name="digitize-upload-bulk"),
    path("qc-upload-bulk/<str:action>/", UpdateQCFileCreateView.as_view(),name="qc-upload-bulk"),
    path("pdf-upload-bulk/<str:action>/", UpdatePdfFileCreateView.as_view(),name="pdf-upload-bulk"),
    path("shape-upload-bulk/<str:action>/", UpdateShapeFileCreateView.as_view(),name="shape-upload-bulk"),


    path("scan-assignto-agency-bulk/<int:agency_id>/<str:action>/", ScanAssignToAgencyView.as_view(),name="scan-assignto-agency-bulk"),
    path("rectify-assignto-agency-bulk/<int:agency_id>/", RectifyAssignToAgencyView.as_view(),name="rectify-assignto-agency-bulk"),#
    path("digitize-assignto-agency-bulk/<int:agency_id>/", DigitizeAssignToAgencyView.as_view(),name="digitize-assignto-agency-bulk"),#

    path("scan-assignto-agencyuser-bulk/<int:user_id>/", ScanAssignToAgencyUserView.as_view(),name="scan-assignto-agencyuser-bulk"),#
    path("rectify-assignto-agencyuser-bulk/<int:user_id>/", RectifyAssignToAgencyUserView.as_view(),name="rectify-assignto-agencyuser-bulk"),#
    path("digitize-assignto-agencyuser-bulk/<int:user_id>/", DigitizeAssignToAgencyUserView.as_view(),name="digitize-assignto-agencyuser-bulk"),#

    path('scan-download/<int:document_id>/',scan_download_file, name='scan-download_file'),
    path('rectify-download/<int:document_id>/',rectify_download_file, name='rectify-download_file'),
    path('digitize-download/<int:document_id>/',digitize_download_file, name='digitize-download_file'),
    path('qc-download/<int:document_id>/',qc_download_file, name='qc-download_file'),
    path('pdf-download/<int:document_id>/',pdf_download_file, name='pdf-download_file'),
    path('shape-download/<int:document_id>/',shape_download_file, name='shape-download_file'),
    path('qc-user-rectify-download/<int:document_id>/',qc_user_rectify_download_file, name='qc-user-rectify-download_file'),

    path('rectify-download/<str:action>/', rectify_download_multiple_files, name='rectify-download-multiple-files'),

    path("document-update-remark/", UploadDocumentRemarkGenericAPI.as_view(), name="document-update-remark"),
    path("all-document-list/", AllDocumentListView.as_view(), name="all-document-list"),


    path("digitize-upload-autoscript/<str:action>/", AutoUploadDigitizeFileCreateView.as_view(), name="all-document-list"),
    path("qc-upload-autoscript/<str:action>/", AutoUploadQCFileCreateView.as_view(), name="all-document-list"),
    path("agency-wise-count/", AgencyWiseWiseDashboardView.as_view(), name="agency-wise-count"),
    path("export-scan-document/", ExportFileScanDocumentListView.as_view(), name="export-scan-document"),
    path("correct-notfound-scan-file/", CorrectNotFoundScanFileCreateView.as_view(), name="all-document-list"),
    path("bel-scan-uploaded/<str:action>/", BelScanUploadedAPIVIew.as_view(), name="bel-scan-uploaded"),
    path("re-assign-document-list/", ReAssignDocumentListView.as_view(), name="all-document-list"),


    path('download/rectify-exefile/', download_exe_file, name='download_exe_file'),
    path('document-barcode/<int:document_id>/', BarcodeScanUploadAPIView.as_view(), name='document_barcode_api'),

    path('delete-document/<int:pk>/', DeleteDocumentAPIView.as_view(), name='delete-document'),

    path("backto-scan-document/<str:action>/", ExchangeScanAssignToAgencyView.as_view(),name="backto-scan-document"),
    path("backto-scanupload-document-list/", ExchangeAssignAgencyDocumentListView.as_view(), name="backyp-scanupload-document-list"),

]