from django.utils.translation import gettext as _
from rest_framework import serializers
from core.models import KumbhAsset,JsonDataMaster

class CreateKumbhAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = KumbhAsset
        fields = "__all__"
    
    # def to_representation(self, instance):
    #     representation = super().to_representation(instance)
    #     # Modify the qr_code to show only the filename
    #     qr_code = representation.get('qr_code')
    #     if qr_code:
    #         representation['qr_code'] = qr_code.split('/')[-1]
    #     return representation
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        # Modify the qr_code to show only the filename
        qr_code = representation.get('qr_code')
        if qr_code:
            representation['qr_code'] = qr_code.split('/')[-1]

        # Add qr_image parameter based on qr_code
        qr_image_url = None
        if qr_code:
            qr_image_url = f"/media/{representation['qr_code']}"  # Replace with actual logic to get the QR image URL
        
        representation['qr_image'] = qr_image_url

        return representation
    
class UpdateKumbhAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = KumbhAsset
        fields = "__all__"
    
    def save(self, *args, **kwargs):
        # Check if an asset image is provided
        asset_image = self.validated_data.get('asset_image')
        
        # If an asset image is provided, it should be saved
        if asset_image:
            instance = super().save(*args, **kwargs)
            instance.asset_image.save(asset_image.name, asset_image)
        else:
            instance = super().save(*args, **kwargs)
        
        return instance
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Modify the asset_image to show only the filename
        asset_image = representation.get('asset_image')
        if asset_image:
            representation['asset_image'] = asset_image.split('/')[-1]
        return representation

class KumbhAssetSerializer(serializers.ModelSerializer):
    asset_id = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = KumbhAsset
        fields = "__all__"
    
    def get_asset_id(self,obj):
        if obj and obj.id:
            return obj.id
        else:
            return None
    
    
class AssetQuationAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = JsonDataMaster
        fields = "__all__"