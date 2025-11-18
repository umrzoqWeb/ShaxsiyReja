from django import forms

from .models import StudentActivity

class StudentActivityForm(forms.ModelForm):
    class Meta:
        model = StudentActivity
        fields = ['title', 'description', 'evidence_file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'evidence_file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }