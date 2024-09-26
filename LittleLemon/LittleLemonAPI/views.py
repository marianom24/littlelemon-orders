from django.shortcuts import render, get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, throttle_classes, permission_classes
from .models import Category, MenuItem, Cart, OrderItem, Order
from .serializers import CategorySerializer, MenuItemSerializer, CartSerializer, OrderItemSerializer, OrderSerializer, UserSerializer, OrderDeliveryUpdateSerializer, OrderManagerUpdateSerializer
from django.contrib.auth.models import User, Group
from rest_framework.permissions import  IsAuthenticated, IsAdminUser
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from django.core.paginator import Paginator
from datetime import datetime
from .filters import MenuItemFilter
from .models import UserComments
from django.http import JsonResponse
from .forms import CommentForm

# Create your views here.
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([AnonRateThrottle, UserRateThrottle])
def menu_items_view(request):
    manager_check = request.user.groups.filter(name='manager').exists()
    admin_check = request.user.is_superuser

    if request.method == 'GET':
        items = MenuItem.objects.all()

        #Filtering, ordering, searching #
        to_price = request.query_params.get('to_price')
        search = request.query_params.get('search')
        category_name = request.query_params.get('category')
        ordering = request.query_params.get('ordering')
        if category_name:
            items = items.filter(category__slug = category_name)
        if search:
            items = items.filter(title__istartswith=search) 
        if to_price:
            items = items.filter(price__lte = to_price)
        if ordering:
            ordering_fields = ordering.split(",")
            items = items.order_by(*ordering_fields)
        #Pagination#
        perpage = request.query_params.get('perpage', 4)
        page = request.query_params.get('page', 1)
        paginator = Paginator(items, per_page=perpage)
        try:
            items = paginator.page(number=page)
        except:
            return Response({"message": "Invalid page."}, status=status.HTTP_400_BAD_REQUEST)
        
        serialized_items = MenuItemSerializer(items, many=True)
        return Response(serialized_items.data, status=status.HTTP_200_OK)
    
    if request.method == 'POST':
        if manager_check or admin_check: 
            serialized_item = MenuItemSerializer(data = request.data)
            serialized_item.is_valid(raise_exception=True)
            serialized_item.save()
            return Response(serialized_item.data, status=status.HTTP_201_CREATED)
        else:
            return Response({'message':'You are not allowed'},status=status.HTTP_403_FORBIDDEN)

@api_view(['GET','PUT','PATCH','DELETE'])
@permission_classes([IsAuthenticated])
@throttle_classes([AnonRateThrottle, UserRateThrottle])
def single_menu_item(request, id):
    manager_check = request.user.groups.filter(name='manager').exists()
    admin_check = request.user.is_superuser
    item = get_object_or_404(MenuItem, pk=id)
    user = get_object_or_404(User, username= request.user)

    if request.method == 'GET':
        serialized_item = MenuItemSerializer(item)
        return Response(serialized_item.data, status=status.HTTP_200_OK)
            
    if manager_check or admin_check: 
        if request.method == 'PUT':
            serialized_item = MenuItemSerializer(item, data=request.data)
            serialized_item.is_valid()
            serialized_item.save(raise_exception=True)
            return Response(serialized_item.data, status=status.HTTP_201_CREATED)
        if request.method == 'PATCH':
            serialized_item = MenuItemSerializer(item, data=request.data, partial=True)
            serialized_item.is_valid(raise_exception=True)
            serialized_item.save()
            return Response(serialized_item.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            item.delete()
            return Response({'message':'Removed'}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({'message':'You are not allowed'},status=status.HTTP_403_FORBIDDEN)
    
@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([AnonRateThrottle, UserRateThrottle])
def groups_view(request, group):
    manager_check = request.user.groups.filter(name='manager').exists()
    admin_check = request.user.is_superuser

    if group == 'manager':
        if admin_check:
            group = Group.objects.get(name=group)
            if request.method == 'GET':
                users = group.user_set.all()
                users_serialized = UserSerializer(users, many=True)
                return Response(users_serialized.data, status=status.HTTP_200_OK)
            if request.method == 'POST':
                username = request.data.get('username')
                user = get_object_or_404(User, username=username)
                user.groups.add(group)
                return Response(status=status.HTTP_201_CREATED)
            if request.method == 'DELETE':
                username = request.data.get('username')
                user = get_object_or_404(User, username=username)
                user.groups.remove(group)
                return Response({'message':'Removed'}, status=status.HTTP_404_NOT_FOUND)           
        else:
            return Response({'message':'You are not allowed'},status=status.HTTP_403_FORBIDDEN) 
        
    if manager_check or admin_check:
        group = Group.objects.get(name=group)
        if request.method == 'GET':
            users = group.user_set.all()
            users_serialized = UserSerializer(users, many=True)
            return Response(users_serialized.data, status=status.HTTP_200_OK)
        if request.method == 'POST':
            username = request.data.get('username')
            user = get_object_or_404(User, username=username)
            user.groups.add(group)
            return Response(status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            username = request.data.get('username')
            user = get_object_or_404(User, username=username)
            user.groups.remove(group)
            return Response({'message':'Removed'}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({'message':'You are not allowed'},status=status.HTTP_403_FORBIDDEN) 
    
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@throttle_classes([AnonRateThrottle, UserRateThrottle])
def groups_singleuser_view(request, group, id):
    if request.user.groups.filter(name='manager').exists() or request.user.is_staff:
        group = Group.objects.get(name=group)
        if request.method == 'DELETE':
            user = get_object_or_404(User, pk=id)
            user.groups.remove(group)
            return Response({'message':'Removed'}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({'message':'You are not allowed'},status=status.HTTP_403_FORBIDDEN) 

@api_view(['GET','POST','DELETE'])
@permission_classes([IsAuthenticated])
def cart_view(request):
    if request.method == 'GET':
        user = request.user
        items = Cart.objects.filter(user_id = user.id) #tenes configurado para usar el username como user ID#
        serialized_items = CartSerializer(items, many=True)
        return Response(serialized_items.data, status=status.HTTP_200_OK)
    if request.method == 'POST':
        serialized_item = CartSerializer(data = request.data)
        serialized_item.is_valid(raise_exception=True)
        serialized_item.save()
        return Response(serialized_item.data, status=status.HTTP_201_CREATED)
    if request.method == 'DELETE':
        user = request.user
        cart = Cart.objects.filter(user_id = user.id)
        cart.delete()
        return Response({'message':'Removed'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([AnonRateThrottle, UserRateThrottle])
def order_view(request):
    delivery_check = request.user.groups.filter(name='delivery-crew').exists()
    manager_check = request.user.groups.filter(name='manager').exists()
    admin_check = request.user.is_superuser
    user = request.user   

    if request.method == 'GET':
        if manager_check or admin_check:
            items = Order.objects.all()
            serialized_items = OrderSerializer(items, many=True)
            return Response(serialized_items.data, status=status.HTTP_200_OK)
        
        if delivery_check:
            items = Order.objects.filter(delivery_crew_id = user)
            serialized_items = OrderSerializer(items, many=True)
            return Response(serialized_items.data, status=status.HTTP_200_OK)
        
        else:
            try:
                items = Order.objects.filter(user_id=user.id)
                to_price = request.query_params.get('to_price')
                search = request.query_params.get('search')
                ordering = request.query_params.get('ordering')
                perpage = request.query_params.get('perpage', 2)
                page = request.query_params.get('page', 1)
                paginator = Paginator(items, per_page=perpage)

                if ordering:
                    ordering_fields = ordering.split(",")
                    items = items.order_by(*ordering_fields)
                if to_price:
                    items = items.filter(price__lte = to_price)
                if search:
                    items = items.filter(title__startswith = search)
                try:
                    items = paginator.page(number=page)
                except:
                    items=[]   

                serialized_items = OrderSerializer(items, many=True)

                return Response(serialized_items.data, status= status.HTTP_200_OK)
            except:
                return Response(status=status.HTTP_404_BAD_REQUEST)
    if request.method == 'POST':
        cart_items = Cart.objects.filter(user_id=user.id)
        if not cart_items.exists():
            return Response({'message': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)
        
        total_price = sum(item.price for item in cart_items)

        order = Order.objects.create(
            user = user,
            status = False,
            total = total_price,
            date = datetime.today(),
        )
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                menu_item = item.menu_item,
                quantity = item.quantity,
                unit_price = item.unit_price,
                price = item.price,
            )
        cart_items.delete()
        serialized_order = OrderSerializer(order)
        return Response(serialized_order.data, status=status.HTTP_201_CREATED)

@api_view(['GET','PATCH','DELETE'])
@permission_classes([IsAuthenticated])
@throttle_classes([AnonRateThrottle, UserRateThrottle])
def single_order_view(request, id):
    delivery_check = request.user.groups.filter(name='delivery-crew').exists()
    manager_check = request.user.groups.filter(name='manager').exists()
    admin_check = request.user.is_superuser
    user = request.user

    order = get_object_or_404(Order, pk=id)

    if request.method =='GET':
        if manager_check or (delivery_check and order.delivery_crew == user) or (order.user == user) or admin_check:
            serialized_order = OrderSerializer(order)
            return Response(serialized_order.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        
    if request.method == 'PATCH':
        if manager_check or admin_check:
            serialized_order = OrderManagerUpdateSerializer(order, data=request.data, partial=True)
            serialized_order.is_valid(raise_exception=True)
            serialized_order.save()
            return Response(serialized_order.data, status.HTTP_201_CREATED)
        if delivery_check:
            serialized_order = OrderDeliveryUpdateSerializer(order, data=request.data, partial=True)
            serialized_order.is_valid(raise_exception=True)
            serialized_order.save()
            return Response(serialized_order.data, status.HTTP_201_CREATED)            
        else:
            return Response({'message':'You are not allowed'},status=status.HTTP_401_UNAUTHORIZED) 

    if request.method == 'DELETE':
        if manager_check or admin_check:
            order.delete()
        else:
            return Response({'message':'You are not allowed'},status=status.HTTP_401_UNAUTHORIZED) 

class CategoryView(generics.ListCreateAPIView): #deberia hacer un rewrite para permitir ver a todos las categorias pero que solo las pueda cambiar el manager#
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    permission_classes = [IsAdminUser]


def form_view(request):
    form = CommentForm()
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            clean_data = form.cleaned_data
            user_comment  = UserComments(
                menu_item = clean_data['menu_item'],
                first_name = clean_data['first_name'],
                last_name = clean_data['last_name'],
                comment = clean_data['comment'],
            )
            user_comment.save()
            return JsonResponse({'message': 'success'})
    return render(request, 'blog.html', {'form' : form})