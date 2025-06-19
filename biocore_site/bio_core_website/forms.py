from django import forms
from .models import UserAnalysis

class AnalysisUploadForm(forms.ModelForm):
    class Meta:
        model = UserAnalysis
        fields = ['analysis_file']