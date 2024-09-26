from django.urls import path
from . import views

urlpatterns = [
    path('menu-items', views.menu_items_view),
    path('menu-items/<int:id>', views.single_menu_item),
    path('groups/<str:group>/users', views.groups_view),
    path('groups/<str:group>/users/<int:id>', views.groups_singleuser_view),
    path('cart/menu-items', views.cart_view),
    path('orders', views.order_view),
    path('orders/<int:id>', views.single_order_view),
    path('categories', views.CategoryView.as_view()),
    path('form', views.form_view)

]