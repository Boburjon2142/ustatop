from django import forms
from django.forms import inlineformset_factory
from services.models import ServiceDetail
from .models import Listing, ListingImage


class ListingForm(forms.ModelForm):
    service_details = forms.ModelMultipleChoiceField(
        queryset=ServiceDetail.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Xizmat tafsilotlari',
    )

    class Meta:
        model = Listing
        fields = (
            'category',
            'service',
            'title',
            'description',
            'city',
            'price_from',
            'service_details',
        )
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs.setdefault('class', 'form-select')
            elif isinstance(field.widget, forms.CheckboxSelectMultiple):
                field.widget.attrs.setdefault('class', 'detail-list')
            else:
                field.widget.attrs.setdefault('class', 'form-control')
            field.widget.attrs.setdefault('placeholder', field.label)
        self.fields['category'].label = 'Kategoriya'
        self.fields['service'].label = 'Xizmat'
        self.fields['title'].label = 'Sarlavha'
        self.fields['description'].label = 'Tavsif'
        self.fields['city'].label = 'Shahar'
        self.fields['price_from'].label = 'Narx (boshlanish)'
        self.fields['price_from'].widget.attrs.update(
            {
                'inputmode': 'numeric',
                'data-thousands': 'true',
                'placeholder': '100 000',
            }
        )
        self.fields['price_from'].widget.input_type = 'text'

        category_id = None
        if self.data.get('category'):
            category_id = self.data.get('category')
        elif self.instance.pk and self.instance.category_id:
            category_id = self.instance.category_id
        if category_id:
            self.fields['service'].queryset = self.fields['service'].queryset.filter(
                category_id=category_id
            )

        service_id = None
        if self.data.get('service'):
            service_id = self.data.get('service')
        elif self.instance.pk and self.instance.service_id:
            service_id = self.instance.service_id
        if service_id:
            self.fields['service_details'].queryset = ServiceDetail.objects.filter(
                service_id=service_id
            )
        else:
            self.fields['service_details'].queryset = ServiceDetail.objects.none()

    def clean_price_from(self):
        value = self.cleaned_data.get('price_from')
        if value in (None, ''):
            return None
        if isinstance(value, str):
            value = value.replace(' ', '').replace(',', '.')
        return value


def listing_image_formset(extra):
    return inlineformset_factory(
        Listing,
        ListingImage,
        fields=('image',),
        extra=extra,
        max_num=3,
        validate_max=True,
        can_delete=True,
    )
