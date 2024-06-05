from django import forms
from django.forms import ModelForm
from django.core.exceptions import ValidationError
from .models import BookInstance, CustomUser
from django.utils.translation import gettext_lazy as _
import datetime

class RenewBookModelForm(ModelForm):
    def clean_due_back(self):
        data = self.cleaned_data['due_back']
        
        if data is None:
            raise ValidationError(_('Invalid date - renewal data is required'))
        
        # Check date is not in past.
        if data < datetime.date.today():
            raise ValidationError(_('Invalid date - renewal in past'))

        # Check date is in range librarian allowed to change (+4 weeks)
        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError(_('Invalid date - renewal more than 4 weeks ahead'))

        # Remember to always return the cleaned data.
        return data

