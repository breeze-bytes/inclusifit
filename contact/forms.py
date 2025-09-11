from django import forms
from .models import ContactMessage   # using your model

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']

        # Add Bootstrap styling to all fields
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Full Name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Email Address'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Subject'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Write your message here...',
                'rows': 4
            }),
        }

        labels = {
            'name': 'Full Name',
            'email': 'Email Address',
            'subject': 'Subject',
            'message': 'Message',
        }
