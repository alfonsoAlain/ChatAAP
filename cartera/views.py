from rest_framework import viewsets
from rest_framework.response import Response
from cartera.serializers import CarteraSerializer
from .models import Cartera
from rest_framework.permissions import IsAuthenticated


class CarteraViewSet(viewsets.ModelViewSet):
    queryset = Cartera.objects.all()
    serializer_class = CarteraSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Cartera.objects.filter(usuario=user)


