from django.urls import path, include  
from rest_framework.routers import DefaultRouter  
from .views import TorneoViewSet 

router = DefaultRouter()  
router.register(r'', TorneoViewSet)  

urlpatterns = [  
    path('', include(router.urls)),  
] 