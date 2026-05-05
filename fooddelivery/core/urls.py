from django.urls import path
from . import views

urlpatterns = [

    path('',views.landing_page, name='landing'),

    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),

    #restaurant
    path('restaurant-profile/', views.create_restaurant_profile, name='create_restaurant_profile'),

    # Admin
    path('approve-restaurants/', views.admin_approve_restaurants, name='admin_approve_restaurants'),
    path('approve/<int:rid>/', views.approve_restaurant, name='approve_restaurant'),


    # Food (Restaurant)
    path('add-food/', views.add_food_item, name='add_food_item'),
    path('my-foods/', views.my_food_items, name='my_food_items'),

    path('restaurants/', views.customer_restaurants, name='customer_restaurants'),

    #customer
    path('add-to-cart/<int:food_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),

    path('place-order/', views.place_order, name='place_order'),

    path('menu/<int:rid>/', views.restaurant_menu, name='restaurant_menu'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),

    path('increase/<int:item_id>/', views.increase_qty, name='increase_qty'),
    path('decrease/<int:item_id>/', views.decrease_qty, name='decrease_qty'),


    path('restaurant-orders/', views.restaurant_orders, name='restaurant_orders'),
    path('update-order/<int:order_id>/<str:status>/', views.update_order_status, name='update_order_status'),   

    path('my-orders/', views.customer_orders, name='customer_orders'),

    path('checkout/', views.checkout, name='checkout'),
    path('order-success/', views.order_success, name='order_success'),

    path('orders/',views.order_history, name='order_history'),

    path('edit-food/<int:food_id>/', views.edit_food_item, name='edit_food_item'),
    path('delete-food/<int:food_id>/', views.delete_food_item, name='delete_food_item'),
]
