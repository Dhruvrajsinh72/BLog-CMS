from django import forms
from .models import Post
from tinymce.widgets import TinyMCE
from .models import Comment
from .models import Report


class PostForm(forms.ModelForm):
    content = forms.CharField(widget=TinyMCE(attrs={'cols': 500, 'rows': 80}))
    
    class Meta:
        model = Post
        fields = ['title', 'content', 'status', 'thumbnail']  

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].widget.attrs.update({'class': 'form-select'}) 


class CommentForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Write your comment here..."}),
        label="",
    )

    class Meta:
        model = Comment
        fields = ["content"]


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['reason']