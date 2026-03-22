from fastapi import FastAPI, Query, Response, status
from pydantic import BaseModel, Field

app = FastAPI()

class OrderRequest(BaseModel):
    customer_name:    str = Field(..., min_length=2)
    item_id:          int = Field(..., gt=0)
    quantity:         int = Field(..., gt=0, le=20)
    delivery_address: str = Field(..., min_length=10)
    order_type:       str = Field('delivery')

class NewMenuItem(BaseModel):
    name:         str  = Field(..., min_length=2, max_length=100)
    price:        int  = Field(..., gt=0)
    category:     str  = Field(..., min_length=2)
    is_available: bool = True

class CheckoutRequest(BaseModel):
    customer_name:    str = Field(..., min_length=2)
    delivery_address: str = Field(..., min_length=10)

menu = [
    {'id': 1, 'name': 'Farmhouse Pizza', 'price': 450, 'category': 'Pizza', 'is_available': True},
    {'id': 2, 'name': 'Paneer Pizza', 'price': 350, 'category': 'Pizza', 'is_available': True},
    {'id': 3, 'name': 'Veg Burger', 'price': 100, 'category': 'Burger', 'is_available': False},
    {'id': 4, 'name': 'Chicken Burger', 'price':  80, 'category': 'Burger', 'is_available': True},
    {'id': 5, 'name': 'Lemon Soda', 'price':  90, 'category': 'Drink', 'is_available': False},
    {'id': 6, 'name': 'Banana Milkshake', 'price': 120, 'category': 'Drink', 'is_available': True},
    {'id': 7, 'name': 'Choco Lava Cake', 'price':  75, 'category': 'Dessert', 'is_available': True},
    {'id': 8, 'name': 'Black Forest Cake', 'price':  90, 'category': 'Dessert', 'is_available': True},
    ]

orders        = []
order_counter = 1
cart          = []

def find_menu_item(item_id: int):
    for item in menu:
        if item['id'] == item_id:
            return item
    return None

def calculate_bill(price: int, quantity: int, order_type: str = 'delivery') -> int:
    total = price * quantity
    if order_type == 'delivery':
        total += 30
    return total

def filter_menu_logic(category=None, max_price=None, is_available=None):
    result = menu
    if category     is not None:
        result = [i for i in result if i['category'].lower() == category.lower()]
    if max_price    is not None:
        result = [i for i in result if i['price'] <= max_price]
    if is_available is not None:
        result = [i for i in result if i['is_available'] == is_available]
    return result

@app.get('/')
def home():
    return {'message': 'Welcome to QuickBite Food Delivery'}

@app.get('/menu')
def get_menu():
    return {'items': menu, 'total': len(menu)}

@app.get('/orders')
def get_orders():
    return {'orders': orders, 'total_orders': len(orders)}

@app.get('/menu/summary')
def summary():
    available   = [i for i in menu if     i['is_available']]
    unavailable = [i for i in menu if not i['is_available']]
    categories  = list({i['category'] for i in menu})
    return {
        'total_menu_items':      len(menu),
        'number_of_available':   len(available),
        'number_of_unavailable': len(unavailable),
        'categories':            categories,
    }

@app.get('/menu/filter')
def filter_menu(
    category:     str  = Query(None),
    max_price:    int  = Query(None),
    is_available: bool = Query(None),
):
    result = filter_menu_logic(category, max_price, is_available)
    return {'filtered_items': result, 'count': len(result)}

@app.get('/menu/search')
def search_menu(keyword: str = Query(...)):
    results = [
        i for i in menu
        if keyword.lower() in i['name'].lower()
        or keyword.lower() in i['category'].lower()
    ]
    if not results:
        return {'message': f'No items found for: {keyword}', 'results': []}
    return {'keyword': keyword, 'total_found': len(results), 'results': results}

@app.get('/menu/sort')
def sort_menu(
    sort_by: str = Query('price'),
    order:   str = Query('asc'),
):
    if sort_by not in ['price', 'name', 'category']:
        return {'error': "sort_by must be 'price', 'name', or 'category'"}
    if order not in ['asc', 'desc']:
        return {'error': "order must be 'asc' or 'desc'"}
    reverse      = (order == 'desc')
    sorted_items = sorted(menu, key=lambda i: i[sort_by], reverse=reverse)
    return {'sort_by': sort_by, 'order': order, 'menu': sorted_items}

@app.get('/menu/page')
def get_menu_paged(
    page:  int = Query(1, ge=1),
    limit: int = Query(3, ge=1, le=10),
    ):
    start = (page - 1) * limit
    paged = menu[start: start + limit]
    return {
        'page':        page,
        'limit':       limit,
        'total':       len(menu),
        'total_pages': -(-len(menu) // limit),
        'items':       paged,
    }

@app.get('/menu/browse')
def browse_menu(
    keyword: str = Query(None),
    sort_by: str = Query('price'),
    order:   str = Query('asc'),
    page:    int = Query(1, ge=1),
    limit:   int = Query(4, ge=1, le=10),
):
    result = menu
    if keyword:
        result = [
            i for i in result
            if keyword.lower() in i['name'].lower()
            or keyword.lower() in i['category'].lower()
        ]
    if sort_by in ['price', 'name', 'category']:
        reverse = (order == 'desc')
        result  = sorted(result, key=lambda i: i[sort_by], reverse=reverse)
    total = len(result)
    start = (page - 1) * limit
    paged = result[start: start + limit]
    return {
        'keyword':     keyword,
        'sort_by':     sort_by,
        'order':       order,
        'page':        page,
        'limit':       limit,
        'total_found': total,
        'total_pages': -(-total // limit),
        'items':       paged,
    }

@app.get('/orders/search')
def search_orders(customer_name: str = Query(...)):
    result = [o for o in orders if customer_name.lower() in o['customer_name'].lower()]
    if not result:
        return {'message': 'No orders found'}
    return {'customer_name': customer_name, 'total_found': len(result), 'orders': result}

@app.get('/orders/sort')
def sort_orders(order: str = Query('asc')):
    if order not in ['asc', 'desc']:
        return {'error': "order must be 'asc' or 'desc'"}
    reverse       = (order == 'desc')
    sorted_orders = sorted(orders, key=lambda o: o['total_price'], reverse=reverse)
    return {'order': order, 'orders': sorted_orders}

@app.post('/menu')
def add_menu_item(new_item: NewMenuItem, response: Response):
    existing_names = [i['name'].lower() for i in menu]
    if new_item.name.lower() in existing_names:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'Menu item with this name already exists'}
    next_id = max(i['id'] for i in menu) + 1
    item = {
        'id':           next_id,
        'name':         new_item.name,
        'price':        new_item.price,
        'category':     new_item.category,
        'is_available': new_item.is_available,
    }
    menu.append(item)
    response.status_code = status.HTTP_201_CREATED
    return {'message': 'Menu item added', 'item': item}

@app.post('/orders')
def place_order(order_data: OrderRequest):
    global order_counter
    item = find_menu_item(order_data.item_id)
    if not item:
        return {'error': 'Menu item not found'}
    if not item['is_available']:
        return {'error': f"{item['name']} is currently unavailable"}
    if order_data.order_type not in ['delivery', 'pickup']:
        return {'error': "order_type must be 'delivery' or 'pickup'"}
    total = calculate_bill(item['price'], order_data.quantity, order_data.order_type)
    order = {
        'order_id':         order_counter,
        'customer_name':    order_data.customer_name,
        'item':             item['name'],
        'quantity':         order_data.quantity,
        'delivery_address': order_data.delivery_address,
        'order_type':       order_data.order_type,
        'total_price':      total,
        'status':           'confirmed',
    }
    orders.append(order)
    order_counter += 1
    return {'message': 'Order placed successfully', 'order': order}

@app.put('/menu/{item_id}')
def update_menu_item(
    item_id:      int,
    response:     Response,
    price:        int  = Query(None),
    is_available: bool = Query(None),
):
    item = find_menu_item(item_id)
    if not item:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'error': 'Menu item not found'}
    if price        is not None:
        item['price']        = price
    if is_available is not None:
        item['is_available'] = is_available
    return {'message': 'Menu item updated', 'item': item}

@app.delete('/menu/{item_id}')
def delete_menu_item(item_id: int, response: Response):
    item = find_menu_item(item_id)
    if not item:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'error': 'Menu item not found'}
    menu.remove(item)
    return {'message': f"Menu item '{item['name']}' deleted successfully"}

@app.get('/menu/{id}')
def get_items_by_id(id: int):
    for item in menu:
        if item['id'] == id:
            return item
    return {'error': 'Item not found'}

@app.post('/cart/add')
def add_to_cart(
    item_id:  int = Query(...),
    quantity: int = Query(1),
):
    item = find_menu_item(item_id)
    if not item:
        return {'error': 'Menu item not found'}
    if not item['is_available']:
        return {'error': f"{item['name']} is currently unavailable"}
    for cart_item in cart:
        if cart_item['item_id'] == item_id:
            cart_item['quantity'] += quantity
            cart_item['subtotal']  = item['price'] * cart_item['quantity']
            return {'message': 'Cart updated', 'cart_item': cart_item}
    cart_item = {
        'item_id':    item_id,
        'item_name':  item['name'],
        'quantity':   quantity,
        'unit_price': item['price'],
        'subtotal':   item['price'] * quantity,
    }
    cart.append(cart_item)
    return {'message': 'Added to cart', 'cart_item': cart_item}

@app.get('/cart')
def view_cart():
    if not cart:
        return {'message': 'Cart is empty', 'items': [], 'grand_total': 0}
    return {
        'items':       cart,
        'item_count':  len(cart),
        'grand_total': sum(i['subtotal'] for i in cart),
    }

@app.post('/cart/checkout')
def checkout(checkout_data: CheckoutRequest, response: Response):
    global order_counter
    if not cart:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'Cart is empty'}
    placed_orders = []
    grand_total   = 0
    for cart_item in cart:
        order = {
            'order_id':         order_counter,
            'customer_name':    checkout_data.customer_name,
            'item':             cart_item['item_name'],
            'quantity':         cart_item['quantity'],
            'delivery_address': checkout_data.delivery_address,
            'order_type':       'delivery',
            'total_price':      cart_item['subtotal'],
            'status':           'confirmed',
        }
        orders.append(order)
        placed_orders.append(order)
        grand_total   += cart_item['subtotal']
        order_counter += 1
    cart.clear()
    response.status_code = status.HTTP_201_CREATED
    return {
        'message':       'Checkout successful',
        'orders_placed': placed_orders,
        'grand_total':   grand_total,
    }

@app.delete('/cart/{item_id}')
def remove_from_cart(item_id: int, response: Response):
    for cart_item in cart:
        if cart_item['item_id'] == item_id:
            cart.remove(cart_item)
            return {'message': f"{cart_item['item_name']} removed from cart"}
    response.status_code = status.HTTP_404_NOT_FOUND
    return {'error': 'Item not in cart'}