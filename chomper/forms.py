from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from chomper.models import UserProfile

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    address = forms.CharField()

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'address')
