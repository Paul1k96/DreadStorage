from django.db.models import Sum, Count, Q

from .models import *

"List containing information for loading buttons to create new model units"
add_dict = [
    {'title': 'Новый производитель', 'address': 'add_company'},
    {'title': 'Новый магазин', 'address': 'add_shop'},
    {'title': 'Добавить новый товар', 'address': 'add_newproduct'},
    {'title': 'Добавить единицу товара', 'address': 'add_product'},
]


def query_context(user, context=None, get_request=None):
    """
    Function to load data for each product from ProdInfo and Product models.
    This data includes the name, company, total quantity of this product, total weight,
    quantity of the product that does not match the ref_weight field from the Product model, as well as a photo.

    Parameters
    ----------
    user: str
        Username to filter data from ProdInfo model
    context: dict, optional
        Passing a context, otherwise creating an empty context
    get_request: str, optional
        If there is a get request then filter the model Product by request. Built for Search class

    Returns
    ----------
    context: dict
        The context contains a list of objects in the Product model and, for each object,
        the count of the total quantity, the total weight and the number of units, quantity of the product that
        does not match the ref_weight field from the Product model.
    """

    if not type(context) == dict:
        context = dict()

    if get_request:
        context['products'] = Product.objects.filter(
            Q(title__icontains=get_request) | Q(company__company__icontains=get_request)
        )

    counting = list(ProdInfo.objects.filter(account=user).values('title', 'weight'))
    if len(counting) == 0:
        # If the product model list is empty for the current user, then return an empty dict with loading buttons
        # to create new model units

        context = dict()
        context['add_dict'] = add_dict
        return context

    context['add_dict'] = add_dict

    # ------------------------------------------------------------------------
    # QuerySet-list for the template with filtering by product name and company.
    # The list also contains a unique item count and a total weight count.

    count_sum = list(ProdInfo.objects.filter(account=user).values('title', 'company')
                     .annotate(count=Count('title'),
                               weight=Sum('weight'))
                     .order_by('title')
                     )

    # print('counting =', counting, len(counting))
    # print('count_sum =', count_sum, len(count_sum))

    # products list for selecting the value of ref_weight for each object from counting
    products = list(Product.objects.values('id', 'ref_weight'))
    for p in counting:
        ref = [obj['ref_weight'] for obj in products if p['title'] == obj['id']][0]

        # assigning to the 'not_full' variable an item of the 'count_sum' list that matches the id of
        # the 'counting' list
        for c_s in count_sum:
            if p['title'] == c_s['title']:
                not_full = c_s

        # counting elements of the 'counting' list that do not match 'ref_weight'
        cnt = 0
        for c in counting:
            if c['title'] == p['title'] and c['weight'] != ref:
                cnt += 1

        # assigning a new key-value to the selected element count_sum
        not_full['not_full'] = cnt

    # assigning the dictionary "context" the list "count_sum" together with the keys "not_full"
    context['count_sum'] = count_sum
    return context

