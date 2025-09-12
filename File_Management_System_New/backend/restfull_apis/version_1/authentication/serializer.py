from django.utils.translation import gettext as _
from django.contrib.auth.password_validation import validate_password
from django.utils.http import url_has_allowed_host_and_scheme, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings

from rest_framework import serializers
from rest_auth.serializers import PasswordChangeSerializer, PasswordResetSerializer, PasswordResetConfirmSerializer
from users.models import User,Agency
from .serializer_forms import (CustomPasswordResetForm,)



class RegisterSerializer(serializers.ModelSerializer):

    email = serializers.EmailField(required=True)
    # password = serializers.CharField(validators=[validate_password])
    address=serializers.CharField(required=True)
    mobile_number=serializers.CharField(required=True)
    aadhar_no=serializers.CharField(required=True)
    agency = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ["id","username","first_name","last_name","email","address","mobile_number","aadhar_no","agency"]
        # fields ="__all__"

    def validate_email(self, email):
        if User.objects.filter(email__iexact=email):
            raise serializers.ValidationError(_('A user with that email already exists.'))
        return email
    
    def create(self, validated_data):
        agency_name = validated_data.pop('agency')
        address = validated_data.pop('address')
        mobile_number = validated_data.pop('mobile_number')
        aadhar_no = validated_data.pop('aadhar_no')


        # Create Agency
        agency = Agency.objects.create(agency_name=agency_name,address=address,mobile_number=mobile_number,aadhar_no=aadhar_no)
        user = User.objects.create_user(**validated_data)

        # Assign the agency instance to the user's 'agency' attribute
        user.agency = agency
        user.save()

        return user

class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields ="__all__"
    
  



class UserDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'is_active',)


class CustomPasswordChangeSerializer(PasswordChangeSerializer):

    pass


class CustomPasswordResetSerializer(PasswordResetSerializer):

    email = serializers.EmailField()
    password_reset_form_class = CustomPasswordResetForm

    def get_email_options(self):
        """Override this method to change default e-mail options"""
        return {}

    def validate_email(self, value):
        # Create PasswordResetForm with the serializer
        self.reset_form = self.password_reset_form_class(data=self.initial_data)
        if not self.reset_form.is_valid():
            raise serializers.ValidationError(self.reset_form.errors)
        return value

    def save(self):
        request = self.context.get('request')
        # Set some values to trigger the send_email method.
        opts = {
            'use_https': request.is_secure(),
            'from_email': getattr(settings, 'DEFAULT_FROM_EMAIL'),
            'request': request,
        }

        opts.update(self.get_email_options())
        self.reset_form.save(**opts)

class CustomPasswordResetConfirmSerializer(PasswordResetConfirmSerializer):

    new_password2 = serializers.CharField(validators=[validate_password], required=True)

    def validate(self, attrs):

        self._errors = {}
        try:
            uid = urlsafe_base64_decode(attrs['uid']).decode()
            self.user = User._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError({'uid': ['Invalid value']})

        self.custom_validation(attrs)
        self.set_password_form = self.set_password_form_class(user=self.user, data=attrs)

        if not self.set_password_form.is_valid():
            raise serializers.ValidationError(self.set_password_form.errors)

        if not default_token_generator.check_token(self.user, attrs['token']):
            raise serializers.ValidationError({'token': ['Invalid value']})

        return attrs
    
class RegisterAgencyUserSerializer(serializers.ModelSerializer):

    email = serializers.EmailField(required=True)
    # password = serializers.CharField(validators=[validate_password])
    address=serializers.CharField(required=True)
    mobile_number=serializers.CharField(required=True)
    aadhar_no=serializers.CharField(required=True)

    class Meta:
        model = User
        fields ="__all__"

    def validate_email(self, email):
        if User.objects.filter(email__iexact=email):
            raise serializers.ValidationError(_('A user with that email already exists.'))
        return email


class RegisterDistrictSerializer(serializers.ModelSerializer):

    email = serializers.EmailField(required=True)
    address=serializers.CharField(required=True)
    mobile_number=serializers.CharField(required=True)
    aadhar_no=serializers.CharField(required=True)

    class Meta:
        model = User
        fields ="__all__"


    def validate_email(self, email):
        if User.objects.filter(email__iexact=email):
            raise serializers.ValidationError(_('A user with that email already exists.'))
        return email