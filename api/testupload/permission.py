from rest_framework.permissions import IsAuthenticated


class NewTestUploadPermission(IsAuthenticated):

    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.role == 'admin'