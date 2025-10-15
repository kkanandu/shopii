from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
import re
from django.core.exceptions import ValidationError
# WORKING SOLUTION - Use ModelForm instead of UserCreationForm
class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Create password'}),
        min_length=8
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password'}),
        min_length=8
    )
    
    class Meta:
        model = CustomUser
        fields = ['name', 'email', 'phone']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
        }
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered. Please use a different email.")
        return email
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone:
            raise ValidationError("Phone number is required.")
        if not re.fullmatch(r'^\d{10}$', phone):
            raise ValidationError("Enter a valid 10-digit phone number.")
        if CustomUser.objects.filter(phone=phone).exists():
            raise ValidationError("This phone number is already registered.")
        return phone
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match.")
        return password2
    def save(self, commit=True):
        user = super().save(commit=False)
        # Use email as username
        user.username = self.cleaned_data['email']
        # Set password properly using Django's method
        user.set_password(self.cleaned_data['password1'])
        
        if commit:
            user.save()
        return user
# Your other forms remain the same
class Socialreg(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'name', 'phone', 'email', 'address', 'bio', 'profile_pic']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['profile_pic'].widget.attrs.update({'accept': 'image/*'})
        self.fields['username'].disabled = True
        self.fields['email'].disabled = True
        
    def save(self, commit=True):
        user = super().save(commit=False)
        if self.instance.pk:
            original = CustomUser.objects.get(pk=self.instance.pk)
            user.email = original.email
        if commit:
            user.save()
        return user
class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
class DeletionReasonForm(forms.Form):
    reason = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), label="Reason for deletion")