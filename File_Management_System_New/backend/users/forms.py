from django import forms
from users.models import (User,)



class UserCreationForm(forms.ModelForm):

    class Meta:
        model = User
        fields = "__all__"
    
    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user
