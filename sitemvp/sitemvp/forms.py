from cProfile import label
from click import help_option
from django import forms

class PinForm(forms.Form):
    pin = forms.CharField(label="Access PIN", max_length=8, min_length=4, widget=forms.PasswordInput()) # forms.PasswordInput()