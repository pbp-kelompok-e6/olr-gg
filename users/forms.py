from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Report, WriterRequest

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('first_name', 'last_name', 'username',)

class CustomUserChangeForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'bio', 'profile_picture']  
    
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
                

class WriterRequestForm(forms.ModelForm):
    reason = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 5, 
            'placeholder': 'Explain why you want to be a writer...',
            'class': 'p-2 border-2 shadow-sm block w-full focus:ring-black-500 focus:border-black-500 sm:text-sm border-black-700 rounded-md'
        }),
        label="Reason for Request"
    )

    class Meta:
        model = WriterRequest
        fields = ['reason']