from django.utils.translation import gettext as _
from rest_framework import serializers
from users.models import User,Role
from django.contrib.auth import password_validation
from core.models import Department
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import EmailMessage
import os
from core.models import DistrictTalukaAdmin

class UserDetailSerializers(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'is_active', 'mobile_number', 'date_created', 'date_updated',
        )


class UserUpdateSerializers(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'email',)

    def validate_email(self, email):
        if not email:
            return email
        if User.objects.filter(email__iexact=email).exclude(id=self.instance.id):
            raise serializers.ValidationError(_('A user with that email already exists.'))
        return email

class UserLoginSerializer(serializers.Serializer):
    email = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=128, write_only=True, required=True)
    new_password1 = serializers.CharField(max_length=128, write_only=True, required=True)
    new_password2 = serializers.CharField(max_length=128, write_only=True, required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                _('Your old password was entered incorrectly. Please enter it again.')
            )
        return value

    def validate(self, data):
        if data['new_password1'] != data['new_password2']:
            raise serializers.ValidationError({'new_password2': _("The two password fields didn't match.")})
        password_validation.validate_password(data['new_password1'], self.context['request'].user)
        return data

    def save(self, **kwargs):
        password = self.validated_data['new_password1']
        user = self.context['request'].user
        user.set_password(password)
        user.save()
        return user


class Util:
  @staticmethod
  def send_email(data):
    email = EmailMessage(
      subject=data['subject'],
      body=data['body'],
      from_email=os.environ.get('EMAIL_FROM'),
      to=[data['to_email']]
    )
    email.send()

'''
# link = 'http://localhost:3000/horizontal/reset-password/api/version_0/users/reset-password/'+uid+'/'+token+'/'
'''
class SendPasswordResetEmailSerializer(serializers.Serializer):
  email = serializers.EmailField(max_length=255)
  class Meta:
    fields = ['email']

  def validate(self, attrs):
    email = attrs.get('email')
    if User.objects.filter(email=email).exists():
      user = User.objects.get(email = email)
      uid = urlsafe_base64_encode(force_bytes(user.id))
      # print('Encoded UID', uid)
      token = PasswordResetTokenGenerator().make_token(user)
      # print('Password Reset Token', token)
      link = 'http://localhost:3000/horizontal/reset-password/'+uid+'/'+token+'/'

      print('Password Reset Link', link)
      # Send EMail
      body = 'Click Following Link to Reset Your Password '+link
      data = {
        'subject':'Reset Your Password',
        'body':body,
        'to_email':user.email
      }
      Util.send_email(data)
      return attrs
    else:
      raise serializers.ValidationError('You are not a Registered User')


class UserPasswordResetSerializer(serializers.Serializer):
  password1 = serializers.CharField(max_length=255, style={'input_type':'password'}, write_only=True)
  password2 = serializers.CharField(max_length=255, style={'input_type':'password'}, write_only=True)
  class Meta:
    fields = ['password1', 'password2']

  def validate(self, attrs):
    try:
      password1 = attrs.get('password1')
      password2 = attrs.get('password2')
      uid = self.context.get('uid')
      token = self.context.get('token')
      if password1 != password2:
        raise serializers.ValidationError("Password and Confirm Password doesn't match")
      id = smart_str(urlsafe_base64_decode(uid))
      user = User.objects.get(id=id)
      if not PasswordResetTokenGenerator().check_token(user, token):
        raise serializers.ValidationError('Your Forget Password Link is Expired')
      user.set_password(password1)
      user.save()
      return attrs
    except DjangoUnicodeDecodeError as identifier:
      PasswordResetTokenGenerator().check_token(user, token)
      raise serializers.ValidationError('Your Forget Password Link is Expired')

from django.contrib.auth import authenticate

from rest_framework import serializers

class AdminLoginSerializer(serializers.Serializer):
 
    username = serializers.CharField(
        label="Username",
        write_only=True
    )
    password = serializers.CharField(
        label="Password",
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(request=self.context.get('request'),
                                username=username, password=password)
            if not user:
                msg = 'wrong username or password.'
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = 'Both "username" and "password" are required.'
            raise serializers.ValidationError(msg, code='authorization')
        attrs['user'] = user
        return attrs

class LoginSerializer(serializers.Serializer):
 
    username = serializers.CharField(
        label="Username",
        write_only=True
    )
    password = serializers.CharField(
        label="Password",
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(request=self.context.get('request'),
                                username=username, password=password)
            if not user:
                msg = 'wrong username or password.'
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = 'Both "username" and "password" are required.'
            raise serializers.ValidationError(msg, code='authorization')
        attrs['user'] = user
        return attrs
    

class UserRoleSerializer(serializers.ModelSerializer):
   
   class Meta:
      model = Role
      fields = ["id","role_name"]

class UserDepartmentSerialzier(serializers.ModelSerializer):
   class Meta:
      model = Department
      fields = ['id','department_name']

class GetDistrictTalukaAdminSerialzier(serializers.ModelSerializer):
    district_name = serializers.SerializerMethodField(read_only=True)
    taluka_name = serializers.SerializerMethodField(read_only=True)
    class Meta:
      model = DistrictTalukaAdmin
      fields = ['id','district_id','taluka_id','district_name','taluka_name']

    def get_district_name(self,obj):
        if obj and obj.district_id:
           return obj.district_id.district_name
        else:
           return None
      
    def get_taluka_name(self,obj):
        if obj and obj.taluka_id:
           return obj.taluka_id.taluka_name
        else:
           return None
class UserProfileDetailsSerializer(serializers.ModelSerializer):
    agency_name =serializers.SerializerMethodField(read_only=True)
    district_taluka_details = serializers.SerializerMethodField('dist_tlk_details',read_only=True)

    
    class Meta:
        model= User
        fields = "__all__"
    
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["user_role"] = UserRoleSerializer(instance.user_role).data 
        rep["department"] = UserDepartmentSerialzier(instance.department,many=True).data

        return rep

    def get_agency_name(self,obj):
        if obj and obj.agency:
            return obj.agency.agency_name
        return None
    
    def dist_tlk_details(self, obj):
        queryset = DistrictTalukaAdmin.objects.filter(user_id=obj.id)
        if queryset.exists():
            return GetDistrictTalukaAdminSerialzier(queryset.first()).data
        else:
            return None  

class CreateUserSerialzier(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = "__all__"

class LoginUserDetailsSerialzer(serializers.ModelSerializer):
   role_name = serializers.SerializerMethodField(read_only=True)
   
   class Meta:
      model =User
      fields = ['user_role','role_name']

   def get_role_name(self,obj):
      if obj and obj.user_role:
         return obj.user_role.role_name
      else:
         return None
        
       

