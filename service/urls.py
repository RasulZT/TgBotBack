from django.urls import path
from .views import CompanySpotsAPIView, DeliveryLayersAPIView

urlpatterns = [
    path('company_spots/', CompanySpotsAPIView.as_view(), name='company-spot-list'),
    path('delivery_layers/', DeliveryLayersAPIView.as_view(), name='delivery-layers-list'),
]
