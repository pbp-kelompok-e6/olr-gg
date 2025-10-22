from django.forms import ModelForm
from berita.models import Berita
from django.utils.html import strip_tags

class beritaForm(ModelForm):
    class Meta:
        model = Berita
        fields = ["title", "content", "category", "thumbnail", "is_featured"]

    def clean_title(self):
        title = self.cleaned_data["title"]
        return strip_tags(title)

    def clean_content(self):
        content = self.cleaned_data["content"]
        return strip_tags(content)