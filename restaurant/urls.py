from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='home'),
    path('about/', views.about, name="about"),
    path('book/', views.book, name="book"),
    path('menu/', views.menu, name="menu"),
    path('bookings/', views.bookings, name='bookings'),
    path('reservations/', views.reservations, name='reservations'),
    path('api/menu/', views.MenuItemView.as_view(), name='menu-list'),
    path('api/menu/<int:pk>', views.SingleMenuItemView.as_view()),
]