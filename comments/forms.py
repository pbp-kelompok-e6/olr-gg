from django.forms import ModelForm
from comments.models import Comments
from django.utils.html import strip_tags

class CommentForm(ModelForm):
    class Meta:
        model = Comments
        fields = ["content"]

    def clean_content(self):
        content = self.cleaned_data["content"]
        return strip_tags(content)