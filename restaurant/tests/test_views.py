from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from restaurant.models import Menu
from restaurant.serializers import MenuSerializer

class MenuViewTest(TestCase):
    def setUp(self):
        """
        setting up the test client.
        """
        # create a test user:
        # since the MenuItemView uses IsAuthenticated permission,
        # need an authenticated user to make successful requests.
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        # create test instances of the Menu model in a temporary database
        self.menu_item1 = Menu.objects.create(Title="Burger", Price=12.50, Inventory=50)
        self.menu_item2 = Menu.objects.create(Title="Pizza", Price=15.00, Inventory=30)
        self.menu_item3 = Menu.objects.create(Title="Salad", Price=8.75, Inventory=70)

    def test_getall(self):
        """
        This test method retrieves all Menu objects via the API view
        and verifies if the returned serialized data matches the expected data.
        """
        response = self.client.get(reverse('menu-list'))
        menu_items_from_db = Menu.objects.all().order_by('pk')
        expected_serialized_data = MenuSerializer(menu_items_from_db, many=True).data
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, expected_serialized_data)
