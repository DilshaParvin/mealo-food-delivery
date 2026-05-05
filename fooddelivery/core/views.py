from django.shortcuts import render

# Create your views here.
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import UserRegisterForm
from .models import User



def landing_page(request):
    return render(request, 'landing.html')


from django.contrib.auth import get_user_model
from django.contrib import messages
from django.shortcuts import render, redirect

User = get_user_model()

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        role = request.POST['role']

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('register')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        user.role = role
        user.save()

        return redirect('login')

    return render(request, 'register.html')


from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        print("USER:", user)  # debug

        if user is not None:
            login(request, user)   # ✅ THIS SAVES SESSION
            return redirect('dashboard')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})

    return render(request, 'login.html')

def user_logout(request):
    logout(request)
    return redirect('login')


from django.db.models import Q
from .models import FoodItem, Restaurant

def dashboard(request):

    if request.user.role == 'customer':

        foods = FoodItem.objects.all()
        restaurants = Restaurant.objects.all()

        # 🔍 Search
        query = request.GET.get('q')

        if query:
            foods = foods.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query)
            )

        # 🏷 Category Filter
        category = request.GET.get('category')

        if category:
            foods = foods.filter(category=category)

        # 💰 Price Filter
        max_price = request.GET.get('max_price')

        if max_price:
            foods = foods.filter(price__lte=max_price)

        # unique categories
        categories = FoodItem.objects.values_list(
            'category',
            flat=True
        ).distinct()

        return render(request, 'customer_dashboard.html', {
            'foods': foods,
            'restaurants': restaurants,
            'categories': categories
        })

    elif request.user.role == 'restaurant':

        restaurant = Restaurant.objects.filter(
            user=request.user
        ).first()

        total_foods = FoodItem.objects.filter(
            restaurant=restaurant
        ).count()

        orders = Order.objects.filter(
            restaurant=restaurant
        )

        total_orders = orders.count()

        total_revenue = sum(
            order.total_price for order in orders
        )

        recent_orders = orders.order_by('-created_at')[:5]

        return render(request, 'restaurant_dashboard.html', {

            'restaurant': restaurant,
            'total_foods': total_foods,
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'recent_orders': recent_orders

        })
    else:
        return render(request, 'admin_dashboard.html')
    

# ################################################################################################


from .models import Restaurant
from .forms import RestaurantProfileForm
from django.contrib.auth.decorators import login_required

@login_required
def create_restaurant_profile(request):
    if request.method == 'POST':
        form = RestaurantProfileForm(request.POST)
        if form.is_valid():
            restaurant = form.save(commit=False)
            restaurant.user = request.user
            restaurant.save()
            return redirect('dashboard')
    else:
        form = RestaurantProfileForm()
    return render(request, 'restaurant_profile_form.html', {'form': form})


@login_required
def admin_approve_restaurants(request):
    restaurants = Restaurant.objects.filter(is_approved=False)
    return render(request, 'admin_approve_restaurants.html', {'restaurants': restaurants})


@login_required
def approve_restaurant(request, rid):
    restaurant = Restaurant.objects.get(id=rid)
    restaurant.is_approved = True
    restaurant.save()
    return redirect('admin_approve_restaurants')




# #################################################################################################
from .forms import FoodItemForm

@login_required
def add_food_item(request):
    if request.user.role != 'restaurant':
        return redirect('dashboard')

    restaurant = Restaurant.objects.filter(
        user=request.user,
        is_approved=True
    ).first()

    if not restaurant:
        return render(
            request,
            'restaurant_dashboard.html',
            {'error': 'Create restaurant profile or wait for admin approval.'}
        )

    # ✅ ADD THIS LINE HERE
    form = FoodItemForm()

    if request.method == 'POST':
        form = FoodItemForm(request.POST, request.FILES)

        if form.is_valid():
            print("FORM VALID ✅")
            food = form.save(commit=False)
            food.restaurant = restaurant
            food.save()
            return redirect('my_food_items')
        else:
            print("FORM ERRORS ❌", form.errors)

    return render(request, 'add_food_item.html', {'form': form})

@login_required
def my_food_items(request):
    if request.user.role != 'restaurant':
        return redirect('dashboard')

    restaurant = Restaurant.objects.filter(user=request.user).first()

    if not restaurant:
        return redirect('create_restaurant_profile')

    foods = FoodItem.objects.filter(restaurant=restaurant)

    return render(request, 'my_food_items.html', {'foods': foods})



from .models import Restaurant

def customer_restaurants(request):
    restaurants = Restaurant.objects.filter(is_approved=True)
    return render(request, 'customer_restaurants.html', {
        'restaurants': restaurants
    })

###########################################################################################################


from .models import Cart, CartItem, FoodItem
from django.contrib.auth.decorators import login_required

@login_required
def add_to_cart(request, food_id):
    food = FoodItem.objects.get(id=food_id)

    cart, created = Cart.objects.get_or_create(user=request.user)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        food=food
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('view_cart')


@login_required
def view_cart(request):
    cart = Cart.objects.filter(user=request.user).first()

    if not cart:
        cart_items = []
        total_price = 0
    else:
        cart_items = CartItem.objects.filter(cart=cart)
        total_price = sum(
            item.food.price * item.quantity for item in cart_items
        )

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })

@login_required
def increase_qty(request, item_id):
    item = CartItem.objects.get(id=item_id)
    item.quantity += 1
    item.save()
    return redirect('view_cart')


@login_required
def decrease_qty(request, item_id):
    item = CartItem.objects.get(id=item_id)

    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    else:
        item.delete()

    return redirect('view_cart')



##########################################################################################
from .models import Order, OrderItem

@login_required
def place_order(request):
    cart = Cart.objects.filter(user=request.user).first()
    if not cart:
        return redirect('customer_restaurants')

    items = CartItem.objects.filter(cart=cart)
    if not items:
        return redirect('customer_restaurants')

    restaurant = items.first().food.restaurant
    total = sum(item.food.price * item.quantity for item in items)

    order = Order.objects.create(
        user=request.user,
        restaurant=restaurant,
        total_price=total
    )

    for item in items:
        OrderItem.objects.create(
            order=order,
            food=item.food,
            quantity=item.quantity,
            price=item.food.price
        )

    items.delete()

    return render(request, 'order_success.html', {'order': order})










def restaurant_menu(request, rid):

    restaurant = Restaurant.objects.get(id=rid)

    foods = FoodItem.objects.filter(
        restaurant=restaurant
    )

    return render(request, 'restaurant_menu.html', {

        'restaurant': restaurant,
        'foods': foods

    })
# ##########################################################################################################


def customer_dashboard(request):
    foods = FoodItem.objects.all()
    print("DEBUG FOODS:", foods)
    restaurants = Restaurant.objects.all()
    print("DEBUG RESTAURANTS:", restaurants)

    return render(request, 'customer_dashboard.html', {
        'foods': foods,
        'restaurants': restaurants
    })




from django.shortcuts import redirect, get_object_or_404
from .models import CartItem

def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)

    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    else:
        item.delete()

    return redirect('view_cart')


from .models import CartItem

def increase_quantity(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    item.quantity += 1
    item.save()
    return redirect('view_cart')


def decrease_quantity(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)

    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    else:
        item.delete()

    return redirect('view_cart')







############################################################################################################

from .models import Order, Restaurant

def restaurant_orders(request):
    restaurant = Restaurant.objects.get(user=request.user)
    orders = Order.objects.filter(restaurant=restaurant).order_by('-created_at')

    return render(request, 'restaurant_orders.html', {
        'orders': orders
    })






def update_order_status(request, order_id, status):
    order = Order.objects.get(id=order_id)

    order.status = status
    order.save()

    return redirect('restaurant_orders')










def customer_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'customer_orders.html', {
        'orders': orders
    })    


#===================================================================================================


@login_required
def checkout(request):
    cart = Cart.objects.filter(user=request.user).first()

    if not cart:
        return redirect('view_cart')

    cart_items = CartItem.objects.filter(cart=cart)

    if not cart_items:
        return redirect('view_cart')

    # ⚠️ assuming all items belong to same restaurant
    restaurant = cart_items.first().food.restaurant

    total_price = sum(
        item.food.price * item.quantity for item in cart_items
    )

    # ✅ Create Order
    order = Order.objects.create(
        user=request.user,
        restaurant=restaurant,
        total_price=total_price
    )

    # ✅ Create OrderItems
    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            food=item.food,
            quantity=item.quantity,
            price=item.food.price   # IMPORTANT
        )

    # ✅ Clear cart
    cart_items.delete()

    return redirect('order_success')




@login_required
def order_success(request):
    return render(request, 'order_success.html')




# ===========================================================================

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'order_history.html', {'orders' : orders})





# ===========================================================================


@login_required
def edit_food_item(request, food_id):
    food = FoodItem.objects.get(id=food_id)

    # security check
    if food.restaurant.user != request.user:
        return redirect('dashboard')

    if request.method == 'POST':
        form = FoodItemForm(request.POST, request.FILES, instance=food)
        if form.is_valid():
            form.save()
            return redirect('my_food_items')
    else:
        form = FoodItemForm(instance=food)

    return render(request, 'edit_food_item.html', {'form': form})





@login_required
def delete_food_item(request, food_id):
    food = FoodItem.objects.get(id=food_id)

    # security check
    if food.restaurant.user != request.user:
        return redirect('dashboard')

    food.delete()
    return redirect('my_food_items')