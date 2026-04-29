from rest_framework import viewsets, filters, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from .models import Lead
from .serializers import LeadSerializer
from .permissions import IsAIBotOrAdmin
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class LeadPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class LeadViewSet(viewsets.ModelViewSet):
    queryset = Lead.objects.all().order_by('-date')
    serializer_class = LeadSerializer
    pagination_class = LeadPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["platform"]
    search_fields = ["name", "interested_product"]
    
    def get_permissions(self):
        """
        AI Bot can POST leads using X-Api-Key.
        Admin can do everything.
        """
        if self.action == 'create':
            return [permissions.AllowAny()] # Handled in dispatch or specifically
        return [permissions.IsAdminUser()]

    # Overriding permission check for 'create' to support API Key
    def check_permissions(self, request):
        if self.action == 'create':
            perm = IsAIBotOrAdmin()
            if not perm.has_permission(request, self):
                self.permission_denied(request, message="Invalid API Key or Unauthorized")
        else:
            super().check_permissions(request)

    @swagger_auto_schema(
        operation_description="Create a new lead from the AI Bot. Requires 'X-Api-Key' in headers.",
        manual_parameters=[
            openapi.Parameter(
                'X-Api-Key', 
                openapi.IN_HEADER, 
                description="Secret key for AI bot authentication", 
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        request_body=LeadSerializer,
        responses={201: LeadSerializer()}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="List all leads. Admin only.",
        responses={200: LeadSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
