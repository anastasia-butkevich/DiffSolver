from rest_framework import viewsets
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import AllowAny

from app.models import DifferentialEq
from app.api.serializers import DifferentialEqSerializer


class DifferentialEqViewSet(viewsets.ModelViewSet):
    queryset = DifferentialEq.objects.all()
    serializer_class = DifferentialEqSerializer

    filter_backends = (filters.OrderingFilter, DjangoFilterBackend)
    filterset_fields = ('id',)
    permission_classes = (AllowAny,)

    ordering_filter = ('id',)
    ordering = ('-id',)

