"""Formulaires pour l'application chat."""
from django import forms
from .models import FAQ


class FAQForm(forms.ModelForm):
    """Formulaire pour créer/modifier une FAQ (réservé aux admins)."""
    class Meta:
        model = FAQ
        fields = ['question', 'response', 'keywords', 'category', 'is_active']
        widgets = {
            'question': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Quelle est la question ?'
            }),
            'response': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'La réponse détaillée...'
            }),
            'keywords': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'mot-clé1, mot-clé2, mot-clé3'
            }),
            'category': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Réseau, Sécurité...'
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ChatMessageForm(forms.Form):
    """Formulaire pour envoyer une question au chatbot."""
    question = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': "Posez votre question sur l'IT... (ex: Qu'est-ce qu'une adresse IP ?)",
            'id': 'chat-input',
        }),
        max_length=2000,
        label=""
    )
