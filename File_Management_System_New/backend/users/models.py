from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

from core.models import BaseModelMixin,Department,PaginationMaster
from rest_framework.authtoken.models import Token
from django.db.models.signals import post_save
from django.dispatch import receiver

ACTIVE_CHOICES = (
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    )

class Role(BaseModelMixin):
    role_name=models.CharField(max_length=20,blank=True,null=True)

    class Meta:
        verbose_name = _("Role")
        verbose_name_plural = _("Role")
    
    def __str__(self):
        return f"{self.pk},{self.role_name}"

class TeamMaster(BaseModelMixin):
    team_name = models.CharField(max_length=20,blank=True,null=True)

    class Meta:
        verbose_name = _("Team Master")
        verbose_name_plural = _("Team Master")
    
    def __str__(self):
        return f"{self.pk},{self.team_name}"

class Agency(BaseModelMixin):
    team= models.ForeignKey(TeamMaster,on_delete=models.CASCADE,blank=True,null=True,related_name='team_id')
    agency_name=models.CharField(max_length=100,blank=True,null=True)
    address= models.CharField(max_length=150,blank=True,null=True)
    mobile_number= models.CharField(max_length=15,blank=True,null=True)
    aadhar_no = models.CharField(max_length=15,blank=True,null=True)
    active_status = models.CharField(blank=True, default='Active',max_length=8, choices=ACTIVE_CHOICES)


    class Meta:
        verbose_name = _("Agency")
        verbose_name_plural = _("Agency")
    
    def __str__(self):
        return f"{self.pk},{self.agency_name}"

class User(AbstractUser, BaseModelMixin):

    address= models.CharField(max_length=150,blank=True,null=True)
    mobile_number= models.CharField(max_length=15,blank=True,null=True)
    aadhar_no = models.CharField(max_length=15,blank=True,null=True)
    active_status = models.CharField(blank=True, default='Active',max_length=8, choices=ACTIVE_CHOICES)
    user_role = models.ForeignKey(Role,on_delete=models.CASCADE,blank=True,null=True,related_name='user_roles')
    agency= models.ForeignKey(Agency,on_delete=models.CASCADE,blank=True,null=True,related_name='agency_id')
    department = models.ManyToManyField(Department,blank=True,related_name='user_department')
    session_key = models.CharField(max_length=40, blank=True, null=True)

    USERNAME_FIELD = "username"

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
    
    def __str__(self):
        return f"{self.pk},{self.username}"


@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


@receiver(post_save, sender=User)
def create_pagination_user(sender, instance=None, created=False, **kwargs):
    if created:
        PaginationMaster.objects.create(pagination_user=instance)