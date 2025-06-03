from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework import generics, viewsets
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden
from .models import Menu, Booking
from .forms import BookingForm
from .serializers import MenuSerializer, BookingSerializer, UserSerializer
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .permissions import IsManager, IsCustomer, IsDeliveryCrew, IsAdminOrManager
from django.core.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from django.core import serializers
from datetime import datetime
import json

def index(request):
    return render(request, 'index.html', {})

def about(request):
    return render(request, 'about.html')

def menu(request):
    # menu_data = Menu.objects.all()
    # main_data = {"menu": menu_data}
    return render(request, 'menu.html')

def book(request):
    form = BookingForm()
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            form.save()
    context = {'form':form}
    return render(request, 'book.html', context)

@login_required
def reservations(request):
    permission_checker = IsAdminOrManager()
    if not permission_checker.has_permission(request, None):
        raise PermissionDenied("You do not have permission to access this page.")

    date = request.GET.get('date',datetime.today().date())
    bookings = Booking.objects.all()
    booking_json = serializers.serialize('json', bookings)
    return render(request, 'bookings.html',{"bookings":booking_json})

class MenuItemView(generics.ListCreateAPIView):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['Price', 'Title', 'Inventory']
    filterset_fields = ['Price', 'Title', 'Inventory']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsAdminOrManager()]
        return [IsAuthenticated()]

class SingleMenuItemView(generics.RetrieveUpdateAPIView, generics.DestroyAPIView):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsAdminOrManager()]
        return [IsAuthenticated()]

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated, IsAdminOrManager]

class UserViewSet(viewsets.ModelViewSet):
   queryset = User.objects.all()
   serializer_class = UserSerializer
   permission_classes = [IsAuthenticated]

@csrf_exempt
def bookings(request):
    if request.method == 'POST':
        data = json.load(request)
        exist = Booking.objects.filter(reservation_date=data['reservation_date']).filter(reservation_slot=data['reservation_slot']).exists()
        if exist == False:
            booking = Booking (
                Name=data['Name'],
                No_of_guests=data['No_of_guests'],
                reservation_date=data['reservation_date'],
                reservation_slot=data['reservation_slot'],
            )        
            booking.save()
        else:
            return HttpResponse("'error': 1", content_type='application/json')
        
    date = request.GET.get('date',datetime.today().date())
    bookings = Booking.objects.all().filter(reservation_date=date)
    booking_json = serializers.serialize('json', bookings)
    return HttpResponse(booking_json, content_type='application/json')