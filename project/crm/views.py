from django.contrib.auth import logout, login
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail, BadHeaderError
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import *
from .utils1 import *


class MainPage(LoginRequiredMixin, ListView):
    """The class displays the main page when the user is logged in. The main page displays cards with
    information about each unique product from the model. The card also displays information about
    the quantity of goods, the total weight and the number of packs that do not correspond to the field ref_weight of
    the Product model. """

    paginate_by = 10
    model = Product
    template_name = 'crm/cards.html'
    context_object_name = 'products'
    login_url = reverse_lazy('login')

    def get_context_data(self, *, object_list=None, **kwargs):
        """A function to load data(context) to display the page. """

        context = super().get_context_data(**kwargs)
        # query_context is a function to load data for cards from Product model and ProdInfo
        context = query_context(self.request.user, context)  # getting username to filter products by user
        return context

    def get_queryset(self):
        return Product.objects.all().select_related('company')


class Search(ListView):
    """Implements site search based on Product model."""

    model = Product
    context_object_name = 'products'
    template_name = "crm/search_result.html"

    def get_queryset(self):
        """
        The function receives the input data in the search field and, based on it,
        filters the data for display.
        """
        get_request = self.request.GET.get('q')
        user = self.request.user
        context = query_context(user, get_request=get_request)  # getting username to filter products by user
        return context


# ADD PRODUCT PART
class AddCompany(CreateView):
    """Implements the creation of a new object of the 'Company' model"""

    form_class = CompanyForm
    template_name = 'crm/add/add_company.html'
    success_url = reverse_lazy('home')


class AddShop(CreateView):
    """Implements the creation of a new object of the 'Shop' model"""

    form_class = ShopForm
    template_name = 'crm/add/add_shop.html'
    success_url = reverse_lazy('home')


class AddNewProduct(CreateView):
    """Implements the creation of a new object of the 'Company' model"""

    form_class = ProductForm
    template_name = 'crm/add/add_newproduct.html'
    success_url = reverse_lazy('home')


class AddProduct(CreateView):
    """Implements the creation of a new object of the 'ProdInfo' model"""

    model = ProdInfo
    form_class = ProductInfoForm
    template_name = 'crm/add/add_product.html'
    success_url = reverse_lazy('home')

    def get_form_kwargs(self):
        """Selects the user from the request for further binding of the object to the user"""
        
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'user_info': self.request.user if self.request.user.is_authenticated else None,
        })
        return kwargs


def load_titles(request):
    """
    Loads data from the 'product' model if the query contains 'company' data,
    otherwise a dictionary with a message for the user.

    Parameters
    ----------
    request: str
        Request containing GET data
    """
    if request.GET.get('company'):
        company_id = request.GET.get('company')
        titles = Product.objects.filter(company_id=company_id).order_by('title')
    else:
        titles = ({'pk': '', 'title': 'Выберите сначала производителя'},)
    return render(request, 'crm/product_dropdown_list_options.html', {'titles': titles})


class Detail(LoginRequiredMixin, DetailView):
    """
    Loads data to display information about the "Product" model object, and based on
    this object and user information, all related objects from the "ProdInfo" model are loaded
    """

    model = Product
    template_name = 'crm/detail_page/product_detail.html'
    slug_url_kwarg = 'product_slug'
    login_url = reverse_lazy('home')
    raise_exception = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product_set = self.object
        context['product_set'] = (ProdInfo.objects.filter(account=self.request.user, title=product_set)
                                  .values('pk', 'shop__shop', 'cost', 'weight'))
        return context

    def get_queryset(self):
        return Product.objects.all().select_related('company')


class DetailProdInfoEdit(LoginRequiredMixin, UpdateView):
    """Implements editing of "ProdInfo" model objects"""

    model = ProdInfo
    form_class = DetailProdInfo
    template_name = 'crm/detail_page/detail_prodinfo_edit.html'
    pk_url_kwarg = 'prodinfo_id'
    slug_url_kwarg = 'product_slug'
    login_url = reverse_lazy('home')
    success_url = reverse_lazy('home')
    raise_exception = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pk'] = self.object.pk
        context['slug'] = self.request.path.split('/')[-3]
        return context


class DetailProdInfoDelete(LoginRequiredMixin, DeleteView):
    """Implements the ability to delete objects from the ProdInfo model"""

    model = ProdInfo
    template_name = 'crm/detail_page/detail_prodinfo_delete.html'
    pk_url_kwarg = 'prodinfo_id'
    slug_url_kwarg = 'product_slug'
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super(DetailProdInfoDelete, self).get_context_data(**kwargs)
        context['pk'] = self.object.pk
        context['slug'] = self.request.path.split('/')[-3]
        # print(context['pk'], context['slug'])
        return context


class DetailProductEdit(LoginRequiredMixin, UpdateView):
    """Implements editing of "Product" model objects"""

    model = Product
    form_class = DetailProduct
    template_name = 'crm/detail_page/detail_product_edit.html'
    slug_field = 'slug'
    slug_url_kwarg = 'product_slug'
    login_url = reverse_lazy('home')
    success_url = reverse_lazy('home')
    raise_exception = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['photo'] = self.object.photo
        context['slug'] = self.object.slug
        return context


class DetailProdInfoAdd(LoginRequiredMixin, CreateView):
    """
    Implements the ability to add objects to the "ProdInfo" model
    with filtering by the object from the "Product" model
    """

    model = ProdInfo
    form_class = AddProdInfoForm
    template_name = 'crm/detail_page/detail_prodinfo_add.html'
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product_path = self.request.path
        context['slug'] = product_path.split('/')[-3]
        return context

    def get_form_kwargs(self):
        """Passes the username and slug the url of the object to be processed by the form class"""

        kwargs = super(DetailProdInfoAdd, self).get_form_kwargs()
        kwargs.update({
            'user_info': self.request.user if self.request.user.is_authenticated else None,
        })
        query_request_slug = self.request.path.split('/')[-3]
        kwargs['q_request_s'] = query_request_slug
        return kwargs


class RegUser(CreateView):
    """Implements registration on the site. Based on Django standard registration form"""

    form_class = RegisterUserForm
    template_name = 'crm/registration.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        """Saves the form in the user model and the user login to the system"""

        user = form.save()
        login(self.request, user)
        return redirect('home')


class LoginUser(LoginView):
    """Implements a login and redirects to the main page if successful."""

    form_class = LoginUserForm
    template_name = 'crm/login.html'

    def get_success_url(self):
        return reverse_lazy('home')


def logout_user(request):
    """Implements a logout"""

    logout(request)

    return redirect('login')


def password_reset_request(request):
    """Implements password recovery with confirmation sent to the user's email"""

    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = User.objects.filter(Q(email=data))
            if associated_users.exists():
                for user in associated_users:
                    subject = "Password Reset Requested"
                    email_template_name = "crm/password/password_reset_email.txt"
                    c = {
                        'email': user.email,
                        'domain': '127.0.0.1:8000',
                        'site_name': 'DREADSTORAGE',
                        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                        'user': user,
                        'token': default_token_generator.make_token(user),
                        'protocol': 'http',
                    }
                    email = render_to_string(email_template_name, c)
                    try:
                        send_mail(subject, email, 'admin@example.com', [user.email], fail_silently=False)
                    except BadHeaderError:
                        return HttpResponse('Invalid header found.')
                    return redirect('/password_reset/done/')
    password_reset_form = PasswordResetForm()
    return render(request=request, template_name='crm/password/password_reset.html',
                  context={'password_reset_form': password_reset_form})


def pageNotFound(request, exception):
    return HttpResponseNotFound('<h1>Страница не найдена</h1>')
