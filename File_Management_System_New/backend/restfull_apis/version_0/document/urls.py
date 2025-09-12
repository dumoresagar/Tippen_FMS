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
    path("update-agency-list/", UpdateAgencyListView.as_view(), name="update-agency-list"),#

    path("agency-wise-user-list/", AgencyWiseListView.as_view(), name="agency-wise-user-list"),#
    path("districtadmin-wise-user-list/", DistrictAdminWiseListView.as_view(), name="districtadmin-wise-user-list"),#


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
    path("govtqc-assignto-agency-bulk/<int:agency_id>/", GovtQCAssignToAgencyView.as_view(),name="govtqc-assignto-agency-bulk"),#
    path("topology-assignto-agency-bulk/<int:agency_id>/", TopologyAssignToAgencyView.as_view(),name="topology-assignto-agency-bulk"),#
    path("shape-assignto-agency-bulk/<int:agency_id>/", ShapeFileAssignToAgencyView.as_view(),name="shape-assignto-agency-bulk"),#




    path("scan-assignto-agencyuser-bulk/<int:user_id>/", ScanAssignToAgencyUserView.as_view(),name="scan-assignto-agencyuser-bulk"),#
    path("rectify-assignto-agencyuser-bulk/<int:user_id>/", RectifyAssignToAgencyUserView.as_view(),name="rectify-assignto-agencyuser-bulk"),#
    path("digitize-assignto-agencyuser-bulk/<int:user_id>/", DigitizeAssignToAgencyUserView.as_view(),name="digitize-assignto-agencyuser-bulk"),#
    path("govtqc-assignto-agencyuser-bulk/<int:user_id>/", GovtQCAssignToAgencyUserView.as_view(),name="govtqc-assignto-agencyuser-bulk"),#
    path("topology-assignto-agencyuser-bulk/<int:user_id>/", TopologyFileAssignToAgencyUserView.as_view(),name="topology-assignto-agencyuser-bulk"),#
    path("shape-assignto-agencyuser-bulk/<int:user_id>/", ShapeFileAssignToAgencyUserView.as_view(),name="shape-assignto-agencyuser-bulk"),#

    path("scan-reassignto-agencyuser-bulk/<int:user_id>/", ScanReAssignToAgencyUserView.as_view(),name="scan-reassignto-agencyuser-bulk"),#
    path("rectify-reassignto-agencyuser-bulk/<int:user_id>/", RectifyReAssignToAgencyUserView.as_view(),name="rectify-reassignto-agencyuser-bulk"),#
    path("digitize-reassignto-agencyuser-bulk/<int:user_id>/", DigitizeReAssignToAgencyUserView.as_view(),name="digitize-reassignto-agencyuser-bulk"),#



    path('scan-download/<int:document_id>/',scan_download_file, name='scan-download_file'),
    path('rectify-download/<int:document_id>/',rectify_download_file, name='rectify-download_file'),
    path('topology_rectify_download_file/<int:document_id>/',topology_rectify_download_file, name='topology_rectify_download_file'),
    path('digitize-download/<int:document_id>/',digitize_download_file, name='digitize-download_file'),
    path('qc-download/<int:document_id>/',qc_download_file, name='qc-download_file'),
    path('pdf-download/<int:document_id>/',pdf_download_file, name='pdf-download_file'),
    path('shape-download/<int:document_id>/',shape_download_file, name='shape-download_file'),
    path('gov-pdf-completed-download/<int:document_id>/',gov_pdf_completed_download_file, name='gov-pdf-completed-download'), ##
    path('qc-user-rectify-download/<int:document_id>/',qc_user_rectify_download_file, name='qc-user-rectify-download_file'),
    path('toplogy-download/<int:document_id>/',topology_completed_download_file, name='topology-download_file'),


    path('rectify-download/<str:action>/', rectify_download_multiple_files, name='rectify-download-multiple-files'),


    path("document-update-remark/", UploadDocumentRemarkGenericAPI.as_view(), name="document-update-remark"),
    path("all-document-list/", AllDocumentListView.as_view(), name="all-document-list"),
    path("missing-polygon-document-list/", MissingPolygonCountDocumentListView.as_view(), name="missing-polygon-document-list"),


    path("digitize-upload-autoscript/<str:action>/", AutoUploadDigitizeFileCreateView.as_view(), name="all-document-list"),
    path("qc-upload-autoscript/<str:action>/", AutoUploadQCFileCreateView.as_view(), name="all-document-list"),
    path("agency-wise-count/", AgencyWiseWiseDashboardView.as_view(), name="agency-wise-count"),
    path("correct-notfound-scan-file/", CorrectNotFoundScanFileCreateView.as_view(), name="all-document-list"),
    path("bel-scan-uploaded/<str:action>/", BelScanUploadedAPIVIew.as_view(), name="bel-scan-uploaded"),
    path("re-assign-document-list/", ReAssignDocumentListView.as_view(), name="all-document-list"),

    path("rectify-agencyid-fill-up/", RectifyAgencyIdFillUpDocumentListView.as_view(), name="rectify-agencyid-fill-up"),

    path('download/rectify-exefile/', download_exe_file, name='download_exe_file'),
    path('document-barcode/<int:document_id>/', BarcodeScanUploadAPIView.as_view(), name='document_barcode_api'),

    path('delete-document/<int:pk>/', DeleteDocumentAPIView.as_view(), name='delete-document'),

    path("backto-scan-document/<str:action>/", ExchangeScanAssignToAgencyView.as_view(),name="backto-scan-document"),
    path("backto-scanupload-document-list/", ExchangeAssignAgencyDocumentListView.as_view(), name="backyp-scanupload-document-list"),

    path("compare/", CompareBarcodeView.as_view(), name="compare"),
    path("compare-rectify/", CompareRectifyBarcodeView.as_view(), name="compare-rectify"),
    path("compare-digitize/", CompareDigitzeBarcodeView.as_view(), name="compare-digitize"),
    path("compare-qc/", CompareQCBarcodeView.as_view(), name="compare-qc"),

    path("get-documentid/", GetDocumentIDView.as_view(), name="get-documentid"),

    path("govt-qc-upload-bulk/", GovtQCFileCreateView.as_view(),name="govt-qc-upload-bulk"),
    path("govt-pdf-upload-bulk/", GovtPdfFileCreateView.as_view(),name="govt-pdf-upload-bulk"),
    path("topo-dwg-upload-bulk/<str:action>/", TopoDwgFileUploadView.as_view(),name="topo-dwg-upload-bulk"),

    
    path("govt-pending-document-list/", GovtPendingListView.as_view(), name="govt-pending-document-list"),
    path("govt-pdf-pending-document-list/", GovtPDFPendingListView.as_view(), name="govt-pdf-pending-document-list"),
    path("govt-qc-pdf-complete-document-list/", GovtQcCompleteListView.as_view(), name="govt-qc-pdf-complete-document-list"),
    path("topology-complete-document-list/", TopologyCompleteListView.as_view(), name="topology-complete-document-list"),


    path("govt-qc-assign-districtadmin/<int:user_id>/", GovtQcAssignDistrictAdmin.as_view(),name="govt-qc-assign-districtadmin"),

    path("read_barcode_details_api/<int:barcode>/",Read_Barcode_Details_Api.as_view(),name="read_barcode_details_api"),

    path("missing-document-barcode/",MissingDocumentListView.as_view(),name="missing-document-barcode"),

    path("file-path-document/<str:action>/", GetDocumentPath.as_view(), name="file-path-document"),
    path("new-file-path-document/<str:action>/", NewGetDocumentPath.as_view(), name="new-file-path-document"),

    path("two-excle-compare/", TwoCSVFileCompareBarcodeView.as_view(), name="two-excle-compare"),

    path("compare-nine-thirty/", CompareNineThirtyBarcodearcodeView.as_view(), name="compare-nine-thirty"),

    path("file-path-download/<str:action>/", GetDocumentDownloadURL.as_view(), name="file-path-download"),

    path("update-govt-qc-user/<int:barcode_number>/", UpdateGovtUserGenericAPI.as_view(), name="update-govt-qc-user"),
    path("update-filename/<int:barcode_number>/", UpdateBarcodeFilenameGenericAPI.as_view(), name="update-filename"),



    path("village_wise_get_count_of_map_code_9_13/<str:village_code>/", VillageWiseNineThirteenCountView.as_view(), name="village_wise_get_count_of_map_code_9_13"),
    path("taluka_wise_get_count_of_map_code_9_13/<str:taluka_code>/", TalukaVillageWiseNineThirteenCountView.as_view(), name="taluka_wise_get_count_of_map_code_9_13"),

    path('download-qc-files/', DownloadQCFilesAPIView.as_view(), name='download-qc-files'),

    path('rectify-digitize-qc-files/<str:action>/', RectifyDigitizeUploadFileView.as_view(), name='rectify-digitize-qc-files'),

    path('delete-bulk-document/', delete_bulk_document, name='delete-bulk-document'),
    path('delete-bulk-barcode/', delete_bulk_barcode, name='delete-bulk-barcode'),


    path('file-document-path/<str:action>/', FilePathDocumentDownloadURL.as_view(), name='file-document-path'),

    path('new-document-delete/', NewDeleteDocumentAPIView.as_view(), name='new-document-delete'),

    path('qc-mismatch-data/<int:agency>/', MisMatchQCDocument.as_view(), name='qc-mismatch-data'),
    path('digitize-mismatch-data/<int:agency>/', MisMatchDigitizeDocument.as_view(), name='digitize-mismatch-data'),
    path('rectify-mismatch-data/<int:agency>/', MisMatchRectifyDocument.as_view(), name='rectify-mismatch-data'),
    path('wrongh-filename-data/', WronghFileName.as_view(), name='wrongh-filename-data'),
    path('duplicate-barcodes/', DuplicateBarcodeAPIView.as_view(), name='duplicate-barcodes'),
    path('twentyno-duplicate-barcodes/', TwentyNoBarcodeAPIView.as_view(), name='twentyno-duplicate-barcodes'),
    path('twentytwono-duplicate-barcodes/', TwentyTwoNoBarcodeAPIView.as_view(), name='twentytwono-duplicate-barcodes'),
    
    path("tippen-scan-upload-bulk/", TippenScanUploadDocumentView.as_view(),name="tippen-scan-upload-bulk"),
    path("tippen-ditize-bulk/<str:action>/", UpdateTippenDigitizeFileCreateView.as_view(),name="tippen-ditize-bulk"),
    path("tippen-govqc-upload-bulk/<str:action>/", UpdateTippenGovQCFileCreateView.as_view(),name="tippen-govqc-upload-bulk"),
    
   
    path("tippen-scan-document-list/", TippenScanDocumentListView.as_view(), name="tippen-scan-document-list"),






]