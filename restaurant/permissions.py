from rest_framework import permissions

class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.groups.filter(name='Manager').exists()

class IsCustomer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and not request.user.groups.filter(name__in=['Manager', 'Delivery crew']).exists()

class IsDeliveryCrew(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.groups.filter(name='Delivery crew').exists()

class IsAdminOrManager(permissions.BasePermission):
    # custom permission
    message = 'You do not have administrative privileges.'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        return request.user.is_superuser or request.user.groups.filter(name='Manager').exists()