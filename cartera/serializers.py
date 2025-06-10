from rest_framework import serializers  
from .models import Cartera  

class CarteraSerializer(serializers.ModelSerializer):  
    class Meta:  
        model = Cartera  
        fields = '__all__'

