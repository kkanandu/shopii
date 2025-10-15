# forms.py
from django import forms
from .models import *
from django.forms.widgets import ClearableFileInput
from accounts.models import *
from django.contrib.auth import get_user_model

User = get_user_model()


class MultiFileInput(ClearableFileInput):
    allow_multiple_selected = True

    def __init__(self, attrs=None):
        super().__init__(attrs)
        if attrs is None:
            attrs = {}
        attrs.update({'multiple': True})
        self.attrs = attrs

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        exclude = ['user', 'rating', 'date']  
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            # 'rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 5, 'step': 0.5}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'house_type': forms.Select(attrs={'class': 'form-control', 'id': 'house-type-select'}),
            'booking_limit': forms.NumberInput(attrs={'class': 'form-control','min': 1,'placeholder': 'Max users allowed to book'}),
            'transaction_type' : forms.Select(attrs={'class': 'form-control'})
        }
    def __init__(self, *args, **kwargs):
            super(ProductForm, self).__init__(*args, **kwargs)

            category = None
            if 'category' in self.data:
                category = self.data.get('category')
            elif 'instance' in kwargs and kwargs['instance']:
                category = kwargs['instance'].category

            if category == 'bike':
                self.fields.pop('house_type', None)
            else:
                self.fields['house_type'].required = False
    def clean(self):
            cleaned_data = super().clean()
            category = cleaned_data.get('category')
            house_type = cleaned_data.get('house_type')

            if category == 'house' and not house_type:
                self.add_error('house_type', "House type is required for house listings.")

    def available_slots(self):
        from .models import Booking  # Import here to avoid circular import

        # Clean expired bookings
        Booking.objects.filter(
            product=self,
            is_active=True,
            is_confirmed=False,
            date_booked__lt=timezone.now() - timedelta(minutes=15)
        ).update(is_active=False)

        active = Booking.objects.filter(product=self, is_active=True).count()
        return self.booking_limit - active
    

class MultipleImageForm(forms.Form):
    images = forms.FileField(
        widget=MultiFileInput(),
        required=False
    )

    def __init__(self, *args, **kwargs):
        self._files = kwargs.pop('files', None)
        super().__init__(*args, **kwargs)

    def clean_images(self):
        images = []
        if self._files:
            images = self._files.getlist('images')

        if len(images) > 5:
            raise forms.ValidationError("You can upload a maximum of 5 images.")
        for image in images:
            if not image.content_type.startswith('image/'):
                raise forms.ValidationError("Only image files are allowed.")
        return images






class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image',]

        
class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'name', 'phone','email', 'address', 'bio', 'profile_pic',]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['profile_pic'].widget.attrs.update({'accept': 'image/*'})
        self.fields['username'].disabled = True


# class RatingForm(forms.ModelForm):
#     class Meta:
#         model = Rating
#         fields = ['value']
#         widgets = {
#             'value': forms.RadioSelect(choices=[(i, f"{i} Star{'s' if i > 1 else ''}") for i in range(1, 6)])
#         }
#         labels = {
#             'value': 'Your Rating'
#         }
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'text']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5, 'class': 'form-control'}),
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }



class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Write your complaint here...'}),
        }

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['subject', 'message']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Describe your issue'}),
            
        }



class NotificationForm(forms.Form):
    recipients = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=True
    )
    send_to_all = forms.BooleanField(
        required=False,
        label="Send to all users"
    )


