# views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, authentication
from core.models import Document, MissingDocument
from .serializer import BarcodeSerializer
from rest_framework.authentication import TokenAuthentication

class BaseBarcodeUpdateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_document(self, barcode):
        return Document.objects.filter(barcode_number=barcode)

    def handle_missing(self, barcode):
        MissingDocument.objects.update_or_create(barcode_number=barcode)


# 1. Bel Scan Uploaded
class BelScanUploadedAPIView(BaseBarcodeUpdateAPIView):
    def put(self, request):
        serializer = BarcodeSerializer(data=request.data)
        if serializer.is_valid():
            barcode = serializer.validated_data['barcode_number']
            try:
                queryset = self.get_document(barcode)

                if not queryset.exists():
                    # 🟥 Barcode not found at all
                    return Response(
                        {"message": f"Barcode '{barcode}' not found."},
                        status=status.HTTP_404_NOT_FOUND
                    )

                # ✅ Barcode found, now check for rectify_completed_date
                documents = queryset.filter(rectify_completed_date__isnull=False)

                if documents.exists():
                    documents.update(bel_scan_uploaded=True, chk_bel_scan_uploaded="0")
                else:
                    queryset.update(chk_bel_scan_uploaded="2")

                return Response(
                    {"message": "Bel Scan updated successfully."},
                    status=status.HTTP_200_OK
                )

            except Exception as e:
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




# 2. Bel Gov Scan QC Approved

class BelGovScanQCApprovedAPIView(BaseBarcodeUpdateAPIView):
    def put(self, request):
        serializer = BarcodeSerializer(data=request.data)
        if serializer.is_valid():
            barcode = serializer.validated_data['barcode_number']
            try:
                queryset = self.get_document(barcode)

                if not queryset.exists():
                    # 🟥 Barcode not found at all
                    return Response(
                        {"message": f"Barcode '{barcode}' not found."},
                        status=status.HTTP_404_NOT_FOUND
                    )

                # ✅ Barcode found, now check for rectify_completed_date
                documents = queryset.filter(rectify_completed_date__isnull=False, bel_scan_uploaded=True)

                if documents.exists():
                    documents.update(bel_gov_scan_qc_approved=True, chk_bel_gov_scan_qc_approved="0")
                else:
                    queryset.update(chk_bel_gov_scan_qc_approved="2")

                return Response(
                    {"message": "Bel Scan QC Approved updated successfully."},
                    status=status.HTTP_200_OK
                )

            except Exception as e:
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# 3. Bel Draft Uploaded


class BelDraftUploadedAPIView(BaseBarcodeUpdateAPIView):
    def put(self, request):
        serializer = BarcodeSerializer(data=request.data)
        if serializer.is_valid():
            barcode = serializer.validated_data['barcode_number']
            try:
                queryset = self.get_document(barcode)

                if not queryset.exists():
                    # 🟥 Barcode not found at all
                    return Response(
                        {"message": f"Barcode '{barcode}' not found."},
                        status=status.HTTP_404_NOT_FOUND
                    )

                # ✅ Barcode found, now check for rectify_completed_date
                documents = queryset.filter(pdf_completed_date__isnull=False, bel_gov_scan_qc_approved=True)

                if documents.exists():
                    documents.update(bel_draft_uploaded=True,bel_scan_uploaded=True,bel_gov_scan_qc_approved=True,chk_bel_draft_uploaded="0")
                else:
                    queryset.update(chk_bel_draft_uploaded="2")

                return Response(
                    {"message": "Bel Draft updated successfully"},
                    status=status.HTTP_200_OK
                )

            except Exception as e:
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 4. Bel Gov Draft QC Approved


class BelGovDraftQCApprovedAPIView(BaseBarcodeUpdateAPIView):
    def put(self, request):
        serializer = BarcodeSerializer(data=request.data)
        if serializer.is_valid():
            barcode = serializer.validated_data['barcode_number']
            try:
                queryset = self.get_document(barcode)

                if not queryset.exists():
                    # 🟥 Barcode not found at all
                    return Response(
                        {"message": f"Barcode '{barcode}' not found."},
                        status=status.HTTP_404_NOT_FOUND
                    )

                # ✅ Barcode found, now check for rectify_completed_date
                documents = queryset.filter(pdf_completed_date__isnull=False, bel_draft_uploaded=True)

                if documents.exists():
                    documents.update( bel_gov_draft_qc_approved=True,bel_draft_uploaded=True,bel_scan_uploaded=True,bel_gov_scan_qc_approved=True,chk_bel_gov_draft_qc_approved="0")
                else:
                    queryset.update(chk_bel_gov_draft_qc_approved="2")

                return Response(
                    {"message": "Bel Gov Draft QC updated successfully"},
                    status=status.HTTP_200_OK
                )

            except Exception as e:
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)