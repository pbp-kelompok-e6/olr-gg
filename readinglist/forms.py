# readinglist/forms.py
from django import forms
from .models import ReadingList

class ReadingListForm(forms.ModelForm):
    class Meta:
        model = ReadingList
        fields = ['name']
        labels = {
            'name': 'Nama List Baru',
        }