import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import ensure_csrf_cookie

from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils.timezone import now
from datetime import datetime, date
from food.models import Product, Order
from django.shortcuts import get_object_or_404, get_list_or_404
from my_auth.authentication import CustomTokenAuthentication
from my_auth.permissions import IsLogined
from rest_framework.permissions import AllowAny
from .models import Action, Trigger, Payload, Promos
from .serializers import ActionSerializer, TriggerSerializer, PayloadSerializer, PromosSerializer
from my_auth.models import CustomUserAction
from my_auth.serializers import CustomUserActionSerializer
from django.views import View
from django.core.serializers import serialize
from django.http import JsonResponse
from django.http import Http404
from dataclasses import dataclass
import json
import pytest
from datetime import datetime, timedelta
from django.utils.timezone import now
from typing import List, Callable, Any
from food.models import Product
import copy
from django.forms.models import model_to_dict


@dataclass
class InnerData:
    required_amount: int
    current_amount: int
    amount: List[int]
    addition_price: int
    used_ids: List[int]
    used_amounts: List[int]


def ensure_list(item: Any) -> List[Any]:
    """
    Проверяет, является ли элемент списком, и оборачивает его в список, если это не так.

    Parameters:
    item (Any): Элемент для проверки.

    Returns:
    List[Any]: Элемент, обернутый в список.
    """
    if isinstance(item, list):
        return item
    else:
        return [item]


def generate_combinations(lists: List[List[Any]], prefix: List[Any] = []) -> List[List[Any]]:
    """
    Генерирует все возможные комбинации из списка списков чисел рекурсивно.

    Parameters:
    lists (List[List[Any]]): Список списков чисел для генерации комбинаций.
    prefix (List[Any]): Текущий префикс комбинации (используется для рекурсии).

    Yields:
    List[Any]: Следующая возможная комбинация.
    """
    if not lists:
        yield prefix
    else:
        first_list = ensure_list(lists[0])
        for value in first_list:
            yield from generate_combinations(lists[1:], prefix + [value])


def find(lst: List[Any], function: Callable[[Any], bool]) -> int:
    """
    Find the index of the first element in the list that matches the condition specified by the function.

    Parameters:
    lst (List[Any]): The list to search through.
    function (Callable[[Any], bool]): A function that takes an element as input and returns True if the element matches the condition.

    Returns:
    int: The index of the first matching element, or -1 if no element matches the condition.
    """
    for index, value in enumerate(lst):
        if function(value):
            return index
    return -1


def check_order_cost(trigger, order, can_be_repeated):
    total_sum = 0
    for product in order['products']:
        total_sum += product['price']

    order_cost_max = trigger.get('order_cost_max')
    order_cost_min = trigger.get('order_cost_min')
    if not order_cost_max and not order_cost_min:
        raise ValueError("Error in cost")
    print(total_sum, order_cost_max)
    try:
        if order_cost_min:
            if total_sum < order_cost_min:
                return False, None
        if order_cost_max:
            if total_sum > order_cost_max:
                return False, None
        return True, None
    except Exception as e:
        print(e)
        return False, None


# Функции проверки триггеров
def product_checker(trigger, order, can_be_repeated):
    print("-----------------PRODUCT ID CHECK ----------------------------")
    product_id = trigger.get('product_id')
    if not product_id:
        raise ValueError("Missing product_id in trigger")
    try:
        for product in order['products']:
            print(product['product_id'], product_id)
            data = {
                "product_ids": [product_id],
                "amount": [1 if not can_be_repeated else product.get('amount', 1)]
            }
            if product['product_id'] == product_id:
                return True, data
        return False, None
    except Exception as e:
        print(e)
        return False, None


def products_checker(trigger, order, can_be_repeated):
    print('--- products_checker [started] ---')
    product_ids = trigger.get('product_ids', None)
    if not product_ids:
        print('ValueError("Missing product_ids in trigger")')
        raise ValueError("Missing product_ids in trigger")
    try:
        data = {
            "product_ids": [],
            "amount": []
        }
        print(f"order['products']: {order['products']}")
        for product in order['products']:
            print(f"Product -> {product}")
            product_id_index = find(product_ids, lambda product_id: product_id == product['product_id'])
            print(f"Product ID Index: {product_id_index}")
            if product_id_index != -1:
                data["product_ids"].append(product_ids[product_id_index])
                data["amount"].append(1 if not can_be_repeated else product['amount'])
                print(data)

                if not can_be_repeated:
                    # Если нельзя повторять, выходим из цикла после добавления одного продукта
                    break
                else:
                    # Если повторять можно, продолжаем поиск
                    continue

        print(data)
        return (True, data) if len(data.get("product_ids")) != 0 else (False, None)
    except Exception as e:
        print(e)
        return False, None


def category_checker(trigger, order, can_be_repeated):
    category_id = trigger.get('category_id')
    if not category_id:
        raise ValueError("Missing category_id in trigger")
    try:
        data = {
            "product_ids": [],
            "amount": []
        }
        for product in order['products']:
            order_product = Product.objects.get(id=product['product_id'])
            print(category_id, order_product.category.id)
            if category_id == order_product.category.id:
                data["product_ids"].append(order_product.id)
                data["amount"].append(1 if not can_be_repeated else product['amount'])

        return (True, data) if len(data.get("product_ids")) != 0 else (False, None)
    except Exception as e:
        print(e)
        return False, None


def categories_checker(trigger, order, can_be_repeated):
    category_ids = trigger.get('category_ids', None)
    if not category_ids:
        raise ValueError("Missing category_ids in trigger")
    try:
        data = {
            "product_ids": [],
            "amount": []
        }
        for product in order['products']:
            for category_id in category_ids:
                order_product = Product.objects.get(id=product['product_id'])
                print(category_id, order_product.category.id)
                if category_id == order_product.category.id:
                    data["product_ids"].append(order_product.id)
                    data["amount"].append(1 if not can_be_repeated else product['amount'])

        return (True, data) if len(data.get("product_ids")) != 0 else (False, None)
    except Exception as e:
        print(e)
        return False, None


def combo_checker(trigger, order, can_be_repeated):
    trigger_product_lists = trigger.get('product_lists', None)
    if not trigger_product_lists:
        raise ValueError("Missing product_lists in trigger")

    order_product_ids = []
    print(f"Order Product IDs: {order_product_ids}")
    print(f"Product Lists in Trigger: {trigger_product_lists}")
    for product in order['products']:
        for i in range(product['amount']):
            order_product_ids.append(product['product_id'])
    try:
        data_list = []
        prod_list = order_product_ids.copy()
        while True:
            o = False  # Сбрасываем флаг в начале каждой итерации цикла while
            combinations = generate_combinations(trigger_product_lists)  # Пересчитываем комбинации каждый раз
            combinations = list(combinations)
            if len(prod_list) <= 1:
                break
            for ind, lst in enumerate(combinations):
                used_prod = []
                prod_list_copy = prod_list.copy()
                print(lst)
                is_products_in_combination = True

                # Проверяем, есть ли все продукты комбинации в списке продуктов заказа
                for product in lst:
                    if product in prod_list_copy:
                        prod_list_copy.remove(product)
                        used_prod.append(product)
                    else:
                        is_products_in_combination = False
                        break

                if not is_products_in_combination:
                    if ind != len(combinations) - 1:
                        continue
                    else:
                        o = True

                        # Если длина used_prod не совпадает с длиной комбинации, пропускаем
                if len(used_prod) != len(lst):
                    continue

                cnt_data = {}
                prod_list = prod_list_copy

                # Подсчитываем количество использованных продуктов
                for product in used_prod:
                    cnt_data[product] = cnt_data.get(product, 0) + 1

                data = {
                    "product_ids": [],
                    "amount": []
                }
                for key, value in cnt_data.items():
                    data["product_ids"].append(key)
                    data["amount"].append(value)

                # Устанавливаем в True, если хотя бы одна комбинация сработала
                data_list.append(data)
                if not can_be_repeated:
                    data['combo_lists'] = lst
                    return True, data
            # Выход из цикла, если больше нет продуктов, подходящих для выполнения комбинации
            if not o or not any(product in prod_list for combination in combinations for product in combination):
                break

        if len(data_list) == 0:
            return False, None
        else:
            combo_lists = []
            action_data = {}
            for data in data_list:
                prod_ids = data.get('product_ids', [])
                amount = data.get('amount', [])
                combo_list = []
                for i in range(len(prod_ids)):
                    print(prod_ids[i], amount[i])
                    combo_list.extend([prod_ids[i]] * amount[i])
                    if prod_ids[i] in action_data:
                        action_data[prod_ids[i]] += amount[i]
                    else:
                        action_data[prod_ids[i]] = amount[i]
                combo_lists.append(combo_list)
            result = {
                'product_ids': list(action_data.keys()),
                'amount': list(action_data.values()),
                'combo_lists': combo_lists
            }
            return True, result
    except Exception as e:
        print(e)
        return False, None


def time_checker(trigger, order, can_be_repeated):
    date_start_str = trigger.get('date_start')
    date_end_str = trigger.get('date_end')
    days = trigger.get('days', None)
    time_start_str = trigger.get('time_start')
    time_end_str = trigger.get('time_end')

    if not date_start_str and not date_end_str and not days and not time_end_str and not time_start_str:
        raise ValueError("ERROR EPTA")
    try:
        today = now().date()
        if date_start_str:
            date_start = datetime.strptime(date_start_str, '%d.%m.%Y').date()
            if date_start > today:
                return False, None
        if date_end_str:
            date_end = datetime.strptime(date_end_str, '%d.%m.%Y').date()

            if date_end <= today:
                print(date_end <= today)
                return False, None
        if days and now().weekday() not in days:
            return False, None

        if time_start_str and time_end_str:
            time_start = datetime.strptime(time_start_str, '%H:%M').time()
            time_end = datetime.strptime(time_end_str, '%H:%M').time()
            current_time = now().time()
            current_datetime = datetime.combine(datetime.today(), current_time)
            new_datetime = current_datetime + timedelta(hours=6)
            new_time = new_datetime.time()
            print(time_start, new_time, time_end)
            if time_start >= new_time or new_time >= time_end:
                return False, None

        return True, None
    except Exception as e:
        print(e)
        return False, None


# Лист с функциями проверки триггеров
trigger_checkers = [
    combo_checker,
    product_checker,
    products_checker,
    category_checker,
    categories_checker,
    check_order_cost,
    time_checker,
]

action_types = [
    'combo',
    'product',
    'products',
    'category',
    'categories',
    None,
    None
]


def apply_basic_change(product, inner_data: InnerData, get_full_price, get_partial_price):
    """
        get_full_price - lambda функция, которая из количества продуктов дает цену для 1 случая if
        get_partial_price - lambda функция, которая из количества продуктов дает цену для 2 случая
    """
    if inner_data.current_amount >= product['amount']:
        product['price'] = get_full_price(product['amount'])
        print(f"get_full_price [{product['product_id']}] {get_full_price(product['amount'])}")
        inner_data.used_amounts.append(product["amount"])
        inner_data.used_ids.append(product["product_id"])
        inner_data.current_amount -= product["amount"]
    else:
        old_price = int(product['price'] / product["amount"])
        product['amount'] -= inner_data.current_amount
        product['price'] -= old_price * inner_data.current_amount
        print(old_price, inner_data.current_amount)

        product_copy = copy.deepcopy(product)
        product_copy['amount'] = inner_data.current_amount
        product_copy['price'] = get_partial_price(inner_data.current_amount)
        print(f"get_partial_price [{product['product_id']}] {get_partial_price(inner_data.current_amount)}")
        inner_data.used_amounts.append(inner_data.current_amount)
        inner_data.used_ids.append(product["product_id"])
        inner_data.current_amount -= inner_data.current_amount
        return product_copy


@pytest.mark.django_db
def apply_product_price(product, new_price, inner_data: InnerData):
    print("apply_product_price", inner_data.addition_price)
    return apply_basic_change(
        product,
        inner_data,
        lambda count: (new_price + inner_data.addition_price) * count,
        lambda count: (new_price + inner_data.addition_price) * count,
    )


def apply_discount_percent(product, discount_percent, inner_data: InnerData):
    product_price = sum_one_order_product(product, False)
    amount = product['amount']
    price = product['price']
    old_price = int(price / amount)
    print("apply_discount_percent ", old_price, product_price / amount, discount_percent)

    return apply_basic_change(
        product,
        inner_data,
        lambda count: price - product_price * (discount_percent / 100),
        lambda count: (old_price - product_price / amount * (discount_percent / 100)) * count
    )


def apply_discount_amount(product, discount_amount, inner_data: InnerData):
    print("apply_discount_amount")
    old_price = int(product['price'] / product['amount'])
    price = product['price']
    return apply_basic_change(
        product,
        inner_data,
        lambda count: price - discount_amount * count,
        lambda count: (old_price - discount_amount) * inner_data.required_amount
    )


def sum_one_order_product(order_product, sum_additions=True):
    active_mod = order_product.get("active_modifier")
    additions = order_product.get("additions")
    product_id = order_product.get("product_id")
    product = Product.objects.get(id=product_id)
    if active_mod is not None:
        modifier = next((m for m in product.modifiers if m.id == active_mod), None)
        price = modifier.price if modifier else 0
    else:
        price = product.price

    return order_product['amount'] * (
            price +
            (sum(addition.price for addition in product.additions.all() if
                 addition.id in additions) if sum_additions else 0)
    )


def apply_combo(order, action_data, payload):
    max_combo_amount: int = payload.get("amount", 999999999)
    # combo_ids: List[List[int] | int] = action_data.get('combo_ids', None)
    combo_lists: List[List[int]] = action_data.get('combo_lists', None)
    product_ids: List[int] = action_data.get('product_ids', None)
    amount: List[int] = action_data.get('amount', None)
    print(combo_lists, product_ids, amount, len(product_ids), len(amount))

    used_products = {}
    for i in range(min(max_combo_amount, len(combo_lists))):
        for prod_id in ensure_list(combo_lists[i]):
            if prod_id in used_products:
                used_products[prod_id] += 1
            else:
                used_products[prod_id] = 1
    product_ids = list(used_products.keys())
    amount = list(used_products.values())
    prod_list_copy = []
    for product in order.get("products", None):
        product_price = sum_one_order_product(product)
        addition_price = (product_price - sum_one_order_product(product, False)) / product['amount']
        # print(f"product_price{product_price},Price {product['price']}")
        if product['price'] != product_price:
            continue
        ind = find(product_ids, lambda product_id: product.get('product_id', None) == product_id)
        if ind == -1:
            continue
        product_amount: int = amount[ind]
        if product_amount > product['amount']:
            raise Exception('Че за ошибка баля. Вая код исправь')
        elif product_amount == product['amount']:
            product['price'] = addition_price * product['amount']
        else:
            product['price'] -= product_price * product_amount / product['amount']
            product['amount'] -= product_amount
            print(product['price'], product["amount"])

            product_copy = copy.deepcopy(product)
            product_copy['amount'] = product_amount
            product_copy['price'] = addition_price * product_amount
            prod_list_copy.append(product_copy)
    return prod_list_copy, product_ids, amount


def sort_products(products, action_data, order='asc'):
    return sorted(products, key=lambda x: x['price'] / x['amount'], reverse=(order == "desc"))


def merge_products(products):
    merged_products = {}

    for product in products:
        key = (product['product_id'], product['price'] / product['amount'], tuple(product['additions']),
               product['active_modifier'])
        if key in merged_products:
            merged_products[key]['amount'] += product['amount']
            merged_products[key]['price'] += product['price']
        else:
            merged_products[key] = product.copy()
    return list(merged_products.values())


class OrderAnalysisView(APIView):
    permission_classes = [AllowAny]

    def do_payloads(self, order: dict[str, any], payload, action_data, action):
        """
        action_data = {
            "product_ids": List[int]
            "amount": List[number]
        }
        """
        action_copy = copy.deepcopy(action)
        action_copy = model_to_dict(action_copy)
        for i in range(len(payload)):
            product_ids_tr: List[int] = action_data.get("product_ids", [])
            amount_tr: List[int] = action_data.get("amount", [])
            product_ids = payload[i].get("product_ids", None)
            product_id = payload[i].get("product_id", None)
            filter_by_static: bool = payload[0].get("filter_by_static", None)
            print(product_id, product_ids)
            if (product_id or product_ids) and not filter_by_static:
                # статическая
                raise Exception("КТО ПРОЧЕЛ ТОТ ОСЕЛ")
            elif product_id or product_ids:
                # динамическая, но с фильтром
                payload_prod_ids = {key: 0 for key in product_ids}
                actual_data = dict(zip(product_ids_tr, amount_tr))
                keys = payload_prod_ids.keys() & actual_data.keys()
                all_data = {key: payload_prod_ids[key] + actual_data[key] for key in keys}
                pass
            else:
                # динамическая
                all_data = dict(zip(product_ids_tr, amount_tr))
                pass

            type = action_data.get("type", None)
            new_price = payload[i].get("new_price", None)
            new_prices = payload[i].get("new_prices", None)
            discount_percent = payload[i].get("discount_percent", None)
            discount_amount = payload[i].get("discount_amount", None)
            add_products = payload[i].get("add_products", None)
            payload_amount = payload[i].get("amount", sum(all_data.values()))
            products = order['products']
            sort_by = payload[i].get("sort_by_price", "asc")
            inner_data = InnerData(amount=list(all_data.values()), required_amount=payload_amount,
                                   current_amount=payload_amount, addition_price=0, used_ids=[], used_amounts=[])

            if sort_by == "asc":
                products = sort_products(products, action_data, 'asc')
            else:
                products = sort_products(products, action_data, 'desc')

            print(f"Sorted products: {products}")
            new_products = []

            if type == 'combo':
                prod_list_copy, product_ids, amount = apply_combo(order, action_data, payload[i])
                new_products = []
                for product_copy in prod_list_copy:
                    if product_copy is not None:
                        is_similar = False
                        for prod in order['products']:
                            if prod['price'] / prod['amount'] == product_copy['price'] / product_copy['amount'] \
                                    and prod["product_id"] == product_copy['product_id']:
                                print('is similar', prod['product_id'])
                                is_similar = True
                                prod['amount'] += product_copy['amount']
                                prod['price'] += product_copy['price']
                        if not is_similar:
                            print('is not similar')
                            new_products.append(product_copy)
                order['products'].extend(new_products)
                order['products'] = merge_products(order['products'])
                action_copy['payloads'][i]["used_product_ids"] = product_ids
                action_copy['payloads'][i]["used_amount"] = amount
                action_copy['payloads'][i]["combo_lists"] = action_data.get("combo_lists", [])
                break

            for product in products:
                product_id = product['product_id']
                if product_id in all_data:
                    if product['price'] != sum_one_order_product(product):
                        continue
                    if inner_data.current_amount <= 0:
                        break

                    inner_data.required_amount = all_data[product_id]
                    old_price = sum_one_order_product(product) / product['amount']
                    inner_data.addition_price = old_price - sum_one_order_product(product, False) / product['amount']
                    product_copy = None

                    if new_price:
                        print('new_price: ', new_price)
                        product_copy = apply_product_price(product, new_price, inner_data)
                        print("product_copy:", product_copy)

                    elif discount_percent:
                        product_copy = apply_discount_percent(product, discount_percent, inner_data)
                        print("product_copy:", product_copy)

                    elif discount_amount:
                        product_copy = apply_discount_amount(product, discount_amount, inner_data)
                        print("product_copy:", product_copy)

                    elif new_prices:
                        product_price_dict = dict(zip(new_prices['product_ids'], new_prices['new_price']))
                        price = product_price_dict.get(product_id)
                        print('new_prices: ', new_price)
                        if price is not None:
                            product_copy = apply_product_price(product, price, inner_data)
                            print("product_copy:", product_copy)

                    if add_products:
                        product_copy = add_products

                    if product_copy is None:
                        continue
                    if isinstance(product, list):
                        product_copy = [product_copy]
                    for new_product_to_add in product_copy:
                        is_similar = False
                        for prod in order['products']:
                            if prod['price'] / prod['amount'] == new_product_to_add['price'] / new_product_to_add[
                                'amount'] \
                                    and prod["product_id"] == new_product_to_add['product_id']:
                                print('is similar', prod['product_id'])
                                is_similar = True
                                prod['amount'] += new_product_to_add['amount']
                                prod['price'] += new_product_to_add['price']
                        if not is_similar:
                            print('is not similar')
                            new_products.append(new_product_to_add)

            order['products'].extend(new_products)
            order['products'] = merge_products(order['products'])
            print('---- new_products -----: ', new_products, id(products), id(order["products"]))
            if len(inner_data.used_ids) != 0:
                action_copy['payloads'][i]["used_product_ids"] = inner_data.used_ids
                action_copy['payloads'][i]["used_amount"] = inner_data.used_amounts

        order['actions'].append(action_copy)

    def sort_actions_by_product_lists(self, actions):
        """
        Сортирует список акций так, чтобы элементы с ключом "product_lists" в "triggers" были на первом месте.

        :param actions: список акций для сортировки
        :return: отсортированный список акций
        """
        combo_list = []
        products_list = []
        product_list = []
        category_list = []
        categories_list = []
        other_list = []
        for action in actions:
            triggers = action.triggers
            is_added = False
            for trigger in triggers:
                if "product_lists" in trigger:
                    combo_list.append(action)
                    is_added = True
                    break
                elif 'product_id' in trigger:
                    product_list.append(action)
                    is_added = True
                    break
                elif 'product_ids' in trigger:
                    products_list.append(action)
                    is_added = True
                    break
                elif 'category_id' in trigger:
                    category_list.append(action)
                    is_added = True
                    break
                elif 'category_ids' in trigger:
                    categories_list.append(action)
                    is_added = True
                    break
            if not is_added:
                other_list.append(action)

        return combo_list + product_list + products_list + category_list + categories_list + other_list

    def triggers(self, action_index, action, order_data, order_data_copy, order_company_id):
        action_data = None
        action_type = None
        combo_ids = None
        payload = action.payloads
        company_id = action.company.id
        can_be_repeated = action.can_be_repeated
        pass_checkers = True
        triggers = action.triggers
        data = None
        if len(triggers) == 0 or not action.can_be_triggered or company_id != order_company_id:
            pass_checkers = False
        else:
            for trigger in triggers:
                for ind, checker in enumerate(trigger_checkers):
                    try:

                        result, data = checker(trigger, order_data_copy, can_be_repeated)
                        # print(result, data)
                        if not result:
                            pass_checkers = False
                            break
                        elif data is not None and action_data is None:
                            if action_type is None:
                                action_type = action_types[ind]
                            if action_type == 'combo':
                                combo_ids = trigger.get('product_lists', None)
                            action_data = data
                        else:
                            pass_checkers = False
                    except Exception as e:
                        print(f"ERROR: {e}")
                        continue
                if not pass_checkers:
                    break

        if not pass_checkers:
            raise AttributeError()

        print(f"ACTION DATA \n {action_data} \n-----------------------------------")

        product_ids = data['product_ids']
        amounts = data["amount"]
        for index, product_id in enumerate(product_ids):
            for product in order_data_copy['products']:
                if product["product_id"] == product_id:
                    if (product['amount'] - amounts[index]) == 0:
                        order_data_copy['products'].remove(product)
                    else:
                        product['amount'] -= amounts[index]

        action_data['type'] = action_type
        action_data['combo_ids'] = combo_ids
        print(f"Action_data: {action_data}")
        self.do_payloads(order_data, payload, action_data, action)

    def post(self, request, *args, **kwargs):
        order_data = request.data
        order_data_copy = copy.deepcopy(order_data)
        actions = Action.objects.filter(can_be_triggered=True)
        order_actions = order_data_copy['actions']
        print(f"Order_actions:{order_actions}")
        order_company_id = order_data["company_id"]

        sorted_actions = self.sort_actions_by_product_lists(actions)
        print(f"Sorted actions : {sorted_actions}")

        for action_index, action in enumerate(sorted_actions):
            try:
                self.triggers(action_index, action, order_data, order_data_copy, order_company_id)
            except AttributeError:
                continue

        print(f"Order_data {order_data}")

        return Response(order_data, status=status.HTTP_200_OK)


class ActionListView(APIView):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [AllowAny]

    def get(self, request, format=None):
        actions = Action.objects.all()
        serializer = ActionSerializer(actions, many=True)
        return Response(serializer.data)

    @csrf_exempt
    def post(self, request, format=None):
        serializer = ActionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TriggerListView(APIView):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [IsLogined]

    def get(self, request, format=None):
        triggers = Trigger.objects.all()
        serializer = TriggerSerializer(triggers, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = TriggerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PayloadListView(APIView):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [IsLogined]

    def get(self, request, format=None):
        payloads = Payload.objects.all()
        serializer = PayloadSerializer(payloads, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = PayloadSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ActionDetailView(APIView):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return Action.objects.get(pk=pk)
        except Action.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        action = self.get_object(pk)
        serializer = ActionSerializer(action)
        return Response(serializer.data)

    def put(self, request, pk):
        action = self.get_object(pk)
        serializer = ActionSerializer(action, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        action = self.get_object(pk)
        action.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PromosAPIView(APIView):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [IsLogined]

    def get(self, request, format=None):
        promos = Promos.objects.all()
        serializer = PromosSerializer(promos, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = PromosSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomUserActionView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk=None):
        if pk:
            # Получение одного объекта по его pk
            action = get_object_or_404(CustomUserAction, pk=pk)
            serializer = CustomUserActionSerializer(action)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # Получение всех объектов
            actions = CustomUserAction.objects.all()
            serializer = CustomUserActionSerializer(actions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CustomUserActionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        action = get_object_or_404(CustomUserAction, pk=pk)
        serializer = CustomUserActionSerializer(action, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        action = get_object_or_404(CustomUserAction, pk=pk)
        action.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ActionListViewCompany(View):
    def get(self, request, company_id):
        actions = Action.objects.filter(company_id=company_id)
        data = list(actions.values())  # Преобразуйте QuerySet в список словарей
        for item in data:
            if isinstance(item['date_start'], date):
                item['date_start'] = item['date_start'].isoformat()
            if isinstance(item['date_end'], date):
                item['date_end'] = item['date_end'].isoformat()
        return JsonResponse(data, safe=False, json_dumps_params={'indent': 4})
