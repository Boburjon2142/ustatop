from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class StyledFormMixin:
    def add_styling(self):
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs.setdefault('class', 'form-select')
            else:
                field.widget.attrs.setdefault('class', 'form-control')
            field.widget.attrs.setdefault('placeholder', field.label)
            field.help_text = ''


class RegistrationStartForm(StyledFormMixin, forms.Form):
    username = forms.CharField(max_length=150)
    phone_number = forms.CharField(max_length=20, required=False)
    role = forms.ChoiceField(choices=[(User.Roles.CLIENT, 'Mijoz'), (User.Roles.PROVIDER, 'Usta')])
    full_name = forms.CharField(max_length=255)
    city = forms.CharField(max_length=120)
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Foydalanuvchi nomi'
        self.fields['phone_number'].label = 'Telefon'
        self.fields['full_name'].label = 'Ism familiya'
        self.fields['city'].label = 'Shahar'
        self.fields['password1'].label = 'Parol'
        self.fields['password2'].label = 'Parolni tasdiqlash'
        StyledFormMixin.add_styling(self)

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Bu foydalanuvchi nomi allaqachon ro‘yxatdan o‘tgan.')
        return username

    def clean(self):
        cleaned = super().clean()
        password1 = cleaned.get('password1')
        password2 = cleaned.get('password2')
        if password1 and password2 and password1 != password2:
            self.add_error('password2', 'Parollar mos emas.')
        if password1:
            validate_password(password1)
        return cleaned


class VerificationCodeForm(StyledFormMixin, forms.Form):
    code = forms.CharField(max_length=6)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['code'].label = 'Tasdiqlash kodi'
        StyledFormMixin.add_styling(self)


class PasswordResetRequestForm(StyledFormMixin, forms.Form):
    username = forms.CharField(max_length=150)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Foydalanuvchi nomi'
        StyledFormMixin.add_styling(self)

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        if not User.objects.filter(username=username).exists():
            raise forms.ValidationError('Bunday foydalanuvchi nomi topilmadi.')
        return username


class PasswordResetConfirmForm(StyledFormMixin, forms.Form):
    code = forms.CharField(max_length=6)
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['code'].label = 'Tasdiqlash kodi'
        self.fields['password1'].label = 'Yangi parol'
        self.fields['password2'].label = 'Parolni tasdiqlash'
        StyledFormMixin.add_styling(self)

    def clean(self):
        cleaned = super().clean()
        password1 = cleaned.get('password1')
        password2 = cleaned.get('password2')
        if password1 and password2 and password1 != password2:
            self.add_error('password2', 'Parollar mos emas.')
        if password1:
            validate_password(password1)
        return cleaned


class LoginForm(StyledFormMixin, AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Foydalanuvchi nomi'
        self.fields['password'].label = 'Parol'
        StyledFormMixin.add_styling(self)
