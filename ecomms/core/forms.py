from django import forms
from core.models import *
from core.models import Product
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category':forms.Select(attrs={'class':'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'product_available_count':forms.NumberInput(attrs={'class':'form-control'}),
            'img': forms.FileInput(attrs={'class': 'form-control'}),
            'desc':forms.Textarea(attrs={'class':'form-control'}),
            
        }
        
class Checkout(forms.Form):
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    address = forms.CharField(max_length=255, required=True, widget=forms.Textarea(attrs={'class': 'form-control'}))
    country = CountryField(blank_label='(select country)').formfield(
    widget=CountrySelectWidget(attrs={'class': 'custom-select d-block w-100'}))
    zip = forms.CharField(max_length=10, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(max_length=15, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    