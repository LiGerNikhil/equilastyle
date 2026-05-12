from django import forms
from .models import Post, Category


class PostCreateForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'category', 'excerpt', 'content']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your post title...'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'excerpt': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Brief description of your post...'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Write your full post content here...',
                'rows': 10
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.all()
        self.fields['category'].empty_label = "Select a category"
        
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': field.widget.attrs.get('class', '') + ' form-control'
            })
