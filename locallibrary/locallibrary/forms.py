from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

CustomUser = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(label='username', min_length=5, max_length=150)  
    email = forms.EmailField(label='email')  
    password1 = forms.CharField(label='password', widget=forms.PasswordInput)  
    password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput)  

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']

    def username_clean(self):  
        username = self.cleaned_data['username'].lower()  
        new = CustomUser.objects.filter(username=username)  
        if new.exists():  
            raise ValidationError("User Already Exist")  
        return username  

    def email_clean(self):  
        email = self.cleaned_data['email'].lower()  
        new = CustomUser.objects.filter(email=email)  
        if new.exists():  
            raise ValidationError(" Email Already Exist")  
        return email  

    def clean_password2(self):  
        password1 = self.cleaned_data['password1']  
        password2 = self.cleaned_data['password2']  

        if password1 and password2 and password1 != password2:  
            raise ValidationError("Password don't match")  
        return password2  

    def save(self, commit=True):  
        user = CustomUser.objects.create_user(  
            self.cleaned_data['username'],  
            self.cleaned_data['email'],  
            self.cleaned_data['password1']  
        )  
        return user
