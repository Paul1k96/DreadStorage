from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from captcha.fields import CaptchaField

from .models import *


class CompanyForm(forms.ModelForm):
    """Class for adding a new object to the Company model"""

    class Meta:
        model = Company
        fields = ('company',)
        widgets = {
            'company': forms.TextInput(attrs={'placeholder': 'Название производителя',
                                              'class': 'form_input'}),
        }


class ShopForm(forms.ModelForm):
    """Class for adding a new object to the Shop model"""

    class Meta:
        model = Shop
        fields = ('shop',)
        widgets = {
            'shop': forms.TextInput(attrs={'placeholder': 'Название магазина',
                                           'class': 'form_input'}),
        }


class ProductForm(forms.ModelForm):
    """Class for adding a new object to the Product model"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['company'].empty_label = "Выберите производителя"
        self.fields['company'].help_text = '*Обязательное поле.'
        self.fields['title'].help_text = '*Обязательное поле.'
        self.fields['ref_weight'].help_text = '*Обязательное поле.'

    class Meta:
        model = Product
        fields = ['title', 'company', 'ref_weight', 'photo']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Название товара',
                                            'class': 'form_input'}),
            'ref_weight': forms.TextInput(attrs={'placeholder': 'Базовый вес',
                                                 'class': 'form_input'}),
            'company': forms.Select(attrs={'class': 'choice_field'}),
        }


class ProductInfoForm(forms.ModelForm):
    """Class for adding a new object to the ProdInfo model"""

    def __init__(self, user_info, *args, **kwargs):
        """
        Initialization function. The 'title' field loads data depending on data passed from
        the template.

        Parameters
        ----------
        user_info: str
            To assign a created object to a user
        """
        self.user_info = user_info
        super().__init__(*args, **kwargs)
        self.fields['title'].empty_label = "Выберите сначала производителя"
        self.fields['title'].queryset = Product.objects.none()
        self.fields['company'].empty_label = "Выберите производителя"
        self.fields['shop'].empty_label = 'Выберите магазин'

        if 'company' in self.data:
            # If ajax passes data from the 'company' field, then load
            # the filtered data by 'company' from the Product model.
            try:
                company_id = int(self.data.get('company'))
                self.fields['title'].queryset = Product.objects.filter(company_id=company_id).order_by('title')
            except(ValueError, TypeError):
                pass
        elif self.instance.pk:
            # Else, load the data according to the selected data in the "company" field
            self.fields['title'].queryset = self.instance.company.title_set.order_by('title')

    def save(self, *args, **kwargs):
        """Saves a new object for the current user"""

        self.instance.account = self.user_info
        return super().save(*args, **kwargs)

    class Meta:
        model = ProdInfo
        fields = ['company', 'title', 'shop', 'cost', 'weight']
        widgets = {
            'cost': forms.TextInput(attrs={'placeholder': 'Стоимость',
                                           'class': 'form_input'}),
            'weight': forms.TextInput(attrs={'placeholder': 'Вес',
                                             'class': 'form_input'}),
            'title': forms.Select(attrs={'class': 'choice_field'}),
            'company': forms.Select(attrs={'class': 'choice_field'}),
            'shop': forms.Select(attrs={'class': 'choice_field'}),
        }


class DetailProduct(forms.ModelForm):
    """Class for editing the object from the Product model"""

    def __init__(self, *args, **kwargs):
        super(DetailProduct, self).__init__(*args, **kwargs)
        self.fields['title'].empty_label = "Выберите товар"
        self.fields['company'].empty_label = "Выберите производителя"

    photo = forms.ImageField(label=('photo',), required=False, widget=forms
                             .FileInput(attrs={'onchange': 'readURL(this);'}))

    class Meta:
        model = Product
        fields = ['title', 'company', 'ref_weight', 'photo']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Название товара',
                                            'class': 'form_input'}),
            'ref_weight': forms.TextInput(attrs={'placeholder': 'Базовый вес',
                                                 'class': 'form_input'}),
            'company': forms.Select(attrs={'class': 'choice_field'}),
        }


class DetailProdInfo(forms.ModelForm):
    """Class for editing the object from ProdInfo model."""

    def __init__(self, **kwargs):
        super(DetailProdInfo, self).__init__(**kwargs)
        self.fields['shop'].empty_label = "Выберите магазин"

    class Meta:
        model = ProdInfo
        fields = ['shop', 'cost', 'weight']
        widgets = {
            'cost': forms.TextInput(attrs={'placeholder': 'Стоимость',
                                           'class': 'form_input'}),
            'weight': forms.TextInput(attrs={'placeholder': 'Вес',
                                             'class': 'form_input'}),
            'shop': forms.Select(attrs={'class': 'choice_field'}),
        }


class AddProdInfoForm(forms.ModelForm):
    """
    Class for adding a new object to the ProdInfo model based on data from the title
    field and companies from the selected model Product
    """

    def __init__(self, user_info, **kwargs):
        """
        Function for initialization. The function loads the slug from the view's get_form_kwargs function.
        Data from the model is filtered by slug and substituted into the title and company fields

        Parameters
        ----------
        user_info: str
            To assign a created object to a user
        """

        self.user_info = user_info
        q_request_s = kwargs.pop('q_request_s', None)
        super(AddProdInfoForm, self).__init__(**kwargs)
        q_set = tuple(Product.objects.filter(slug=q_request_s).values('pk', 'company'))
        self.fields['title'].initial = q_set[0]['pk']
        self.fields['company'].initial = q_set[0]['company']
        self.fields['shop'].empty_label = "Выберите магазин"

    def save(self, *args, **kwargs):
        """Saves a new object for the current user"""

        self.instance.account = self.user_info
        return super().save(*args, **kwargs)

    class Meta:
        model = ProdInfo
        fields = ['title', 'company', 'shop', 'cost', 'weight']
        widgets = {
            'title': forms.Select(attrs={'class': 'for_hide'}),
            'company': forms.Select(attrs={'class': 'for_hide'}),
            'cost': forms.TextInput(attrs={'placeholder': 'Стоимость',
                                           'class': 'form_input'}),
            'weight': forms.TextInput(attrs={'placeholder': 'Вес',
                                             'class': 'form_input'}),
            'shop': forms.Select(attrs={'class': 'choice_field'}),
        }


class RegisterUserForm(UserCreationForm):
    """Implements registration on the site, based on the standard Django registration form"""

    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form_input',
                                                                            'placeholder': 'Логин'}),
                               help_text='*Обязательное поле.')
    email = forms.EmailField(label='Электронная почта', required=True,
                             widget=forms.TextInput(attrs={'class': 'form_input',
                                                           'placeholder': 'Электронная почта'}),
                             help_text='*Обязательное поле.')
    first_name = forms.CharField(label='Имя', required=False, widget=forms.TextInput(attrs={'class': 'form_input',
                                                                                            'placeholder': 'Имя'}))
    last_name = forms.CharField(label='Фамилия', required=False,
                                widget=forms.TextInput(attrs={'class': 'form_input',
                                                              'placeholder': 'Фамилия'}))
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form_input',
                                                                                  'placeholder': 'Пароль'}),
                                help_text='*Обязательное поле.')
    password2 = forms.CharField(label='Повтор пароля',
                                widget=forms.PasswordInput(attrs={'class': 'form_input',
                                                                  'placeholder': 'Повтор пароля'}),
                                help_text='*Обязательное поле.')
    captcha = CaptchaField()

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form_input', 'placeholder': 'Логин'}),
            'first_name': forms.TextInput(attrs={'class': 'form_input', 'placeholder': 'Имя'}),
            'last_name': forms.TextInput(attrs={'class': 'form_input', 'placeholder': 'Фамилия'}),
            'email': forms.TextInput(attrs={'class': 'form_input', 'placeholder': 'Электронная почта'}),
            'password1': forms.PasswordInput(attrs={'class': 'form_input', 'placeholder': 'Пароль'}),
            'password2': forms.PasswordInput(attrs={'class': 'form_input', 'placeholder': 'Повтор пароля'}),
        }


class LoginUserForm(AuthenticationForm):
    """Implements login on the site"""

    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form_input',
                                                                            'placeholder': 'Логин'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form_input',
                                                                                 'placeholder': 'Пароль'}))
    captcha = CaptchaField()

