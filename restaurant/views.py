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
from datetime import datetime, date
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
    
    is_admin_or_manager = False
    if request.user.is_authenticated:
        permission_checker = IsAdminOrManager()
        is_admin_or_manager = permission_checker.has_permission(request, None) 

    context = {
        'form': form,
        'is_admin_or_manager': is_admin_or_manager,
    }
    return render(request, 'book.html', context)

@csrf_exempt
def bookings(request):
    if request.method == 'POST':
        data = json.load(request)
        
        # --- back-end validation for Name field ---
        name = data.get('Name', '').strip()
        if not name or len(name) < 3:
            return JsonResponse({'error': 'Name is required and must be at least 3 characters.'}, status=400)

        # --- back-end validation for Guests field ---
        guests_Number = data.get('No_of_guests', '').strip()
        if not guests_Number.isdigit() or not (1 <= int(guests_Number) <= 10):
            return JsonResponse({'error': 'Number of guests must be an integer between 1 and 10.'}, status=400)

        # --- back-end validation for Date field ---
        reservation_date_str = data.get('reservation_date', '').strip()
        if not reservation_date_str:
            return JsonResponse({'error': 'Reservation date is required.'}, status=400)

        # --- back-end validation for Time field ---
        reservation_slot_int = str(data.get('reservation_slot', '')).strip()
        if reservation_slot_int in [None, '', 0, '0']:
            return JsonResponse({'error': 'Reservation time is required.'}, status=400)
        try:
            reservation_slot_int = int(reservation_slot_int)
        except ValueError:
            return JsonResponse({'error': 'Reservation time must be a valid number.'}, status=400)

        # --- back-end validation for past dates ---
        try:
            selected_date_obj = datetime.strptime(reservation_date_str, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({'error': 'Invalid date format provided.'}, status=400) # 400 bad request

        today_date = date.today() # get today's date on the server

        if selected_date_obj < today_date:
            return JsonResponse({'error': 'Cannot book a reservation for a past date.'}, status=400)
        
        field_type = Booking._meta.get_field('reservation_date').get_internal_type()

        save_value_for_reservation_date = selected_date_obj

        if field_type == 'DateTimeField':
            save_value_for_reservation_date = datetime.combine(selected_date_obj, datetime.min.time())
        
        exist = Booking.objects.filter(
            reservation_date__date=selected_date_obj, 
            reservation_slot=reservation_slot_int
        ).exists()

        if exist == False:
            booking = Booking (
                Name=data['Name'],
                No_of_guests=data['No_of_guests'],
                reservation_date=save_value_for_reservation_date,
                reservation_slot=reservation_slot_int,
            )         
            booking.save()
            return JsonResponse({'success': 'Booking created successfully!'})
        else:
            return JsonResponse({'error': 'This slot is already booked for the selected date.'}, status=409) # 409 conflict

        # --- end of validation above ---

    requested_date_str = request.GET.get('date')

    if requested_date_str:
        try:
            date_to_filter = datetime.strptime(requested_date_str, '%Y-%m-%d').date()
        except ValueError:
            date_to_filter = datetime.today().date()
    else:
        date_to_filter = datetime.today().date()
    
    bookings_for_date = Booking.objects.filter(reservation_date__date=date_to_filter)
    
    formatted_bookings = []
    for booking in bookings_for_date:
        formatted_bookings.append({
            'model': 'restaurant.booking', 
            'pk': booking.pk,
            'fields': {
                'Name': booking.Name,
                'No_of_guests': booking.No_of_guests,
                'reservation_date': booking.reservation_date.strftime('%Y-%m-%d'), 
                'reservation_slot': booking.reservation_slot
            }
        })
    booking_json = json.dumps(formatted_bookings) 

    return HttpResponse(booking_json, content_type='application/json')

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

