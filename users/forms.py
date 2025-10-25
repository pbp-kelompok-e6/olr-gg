from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Report

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('first_name', 'last_name', 'username',)

class CustomUserChangeForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'bio',]  
    
class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['profile_picture',]

class ReportUserForm(forms.ModelForm):
    reason = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'Jelaskan alasan Anda...'}),
        label="Alasan Laporan"
    )
    
    class Meta:
        model = Report
        fields = ['reason']

class AdminUserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'username', 
            'first_name', 
            'last_name', 
            'email', 
            'bio',
            'profile_picture',
            'role',
            'strikes',
        ]
        
    def __init__(self, *args, **kwargs):
        super(AdminUserUpdateForm, self).__init__(*args, **kwargs)
        
        for field_name, field in self.fields.items():
            if isinstance(field, forms.BooleanField):
                 field.widget.attrs.update({'class': 'form-check-input'})
            else:
                field.widget.attrs.update({'class': 'form-control'})
                
