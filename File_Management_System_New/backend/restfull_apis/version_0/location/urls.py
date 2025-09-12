from django.urls import path, include
from .api import *
from .bel import (
    BelScanUploadedAPIView,
    BelGovScanQCApprovedAPIView,
    BelDraftUploadedAPIView,
    BelGovDraftQCApprovedAPIView,
)


app_name = "location"

urlpatterns = [
    path("create-district/", PostDistrictAPIView.as_view(), name="post-district"),
    path("update-district/<int:pk>/", UpdateDistrictAPIView.as_view(), name="update-delete-district"),
    path("get-district/<int:pk>/", RetriveDistrictAPIView.as_view(), name="get-district"),
    path("district-list/", ListDistrictAPIView.as_view(), name="district-list"),

    path("create-maptype/", PostMapTypeAPIView.as_view(), name="post-maptype"),
    path("update-maptype/<int:pk>/", UpdateMapTypeAPIView.as_view(), name="update-delete-maptype"),
    path("get-maptype/<int:pk>/", RetriveMapTypeAPIView.as_view(), name="get-maptype"),
    path("maptype-list/", ListMapTypeAPIView.as_view(), name="maptype-list"),


    path("create-taluka/", PostTalukaAPIView.as_view(), name="post-taluka"),
    path("update-taluka/<int:pk>/", UpdateTalukaAPIView.as_view(), name="update-delete-taluka"),
    path("get-taluka/<int:pk>/", RetriveTalukaAPIView.as_view(), name="get-taluka"),

    path("create-village/", PostVillageAPIView.as_view(), name="post-village"),
    path("update-village/<int:pk>/", UpdateVillageAPIView.as_view(), name="update-delete-village"),
    path("get-village/<int:pk>/", RetriveVillageAPIView.as_view(), name="get-village"),

    path("create-prescan-document/", PostPreScanningDocumentAPIView.as_view(), name="create-prescan-document"),
    path("update-prescan-document/<int:pk>/", PostPreScanningDocumentAPIView.as_view(), name="update-prescan-document"),
    path("get-prescan-document/<int:pk>/", RetrivePreScanningDocumentAPIView.as_view(), name="get-prescan-document"),
    path("districtwise-prescan/", DistrictWisePreScanningDocumentView.as_view(), name="districtwise-prescan"),
    path("prescan-list/<int:pk>/", PreScanninfDocumentListAPI.as_view(), name="prescan-list"),

    path('download_sql/', download_postgres_sql, name='download_sql'),

    path("create-predraft-report/", PostPreDraftingReportAPIView.as_view(), name="create-predraft-report"),
    path("update-predraft-report/<int:pk>/", PostPreDraftingReportAPIView.as_view(), name="update-predraft-report"),
    path("get-predraft-report/<int:pk>/", RetrivePreDraftingReportAPIView.as_view(), name="get-predraft-report"),
    path("districtwise-predraft-report/", DistrictWisePreDraftingReportView.as_view(), name="districtwise-predraft-report"),
    path("predraft-report-list/<int:pk>/", PreDraftingReportListAPI.as_view(), name="predraft-report-list"),

    path("create-agency-inventry/", PostAgencyInventryAPIView.as_view(), name="create-agency-inventry"),
    path("update-agency-inventry/<int:pk>/", PostAgencyInventryAPIView.as_view(), name="update-agency-inventry"),
    path("get-agency-inventry/<int:pk>/", GetAgencyInventryAPIView.as_view(), name="get-agency-inventry"),

    path("prescan-district-taluka-total-today/",PreScanningDistrictTalukaTotalToday.as_view(), name="prescan-district-taluka-total-today"),
    path("predraft-district-taluka-total-today/",PreDraftingDistrictTalukaTotalToday.as_view(), name="predraft-district-taluka-total-today"),

    path("dynamsoft-productkey/", DynamsoftProductKey.as_view(), name="dynamsoft-productkey"),
    path("update_polygon_count/<str:action>/", UpdatePolygonCount.as_view(), name="update_polygon_count"),
    path("barcode-location/<int:barcode>/", DocumentLocationList.as_view(), name="barcode-location"),
    path('mismatched-extension/', MismatchedFileExtensionsView.as_view(), name='mismatched-extension'),
    path('rectify-mismatched-extension/', RectifyMismatchedFileExtensionsView.as_view(), name='rectify-mismatched-extension'),
    path('digitize-mismatched-extension/', DigitizeMismatchedFileExtensionsView.as_view(), name='digitize-mismatched-extension'),
    path('digitize-count-filenotexits/', DigitizeCountFileFileView.as_view(), name='digitize-count-filenotexits'),
    path('qc-count-filenotexits/', QCCountFileFileView.as_view(), name='qc-count-filenotexits'),
    path('barcode-ninety-digit-file/', BarcodeNinetyDigitFileView.as_view(), name='barcode-ninety-digit-file'),
    path('barcode-twentyonedigit-file/', BarcodeTwentyOneDigitFileView.as_view(), name='barcode-twentyonedigit-file'),


    path('bel-scan-uploaded/', BelScanUploadedAPIView.as_view()),
    path('bel-gov-scan-qc-approved/', BelGovScanQCApprovedAPIView.as_view()),
    path('bel-draft-uploaded/', BelDraftUploadedAPIView.as_view()),
    path('bel-gov-draft-qc-approved/', BelGovDraftQCApprovedAPIView.as_view()),



]