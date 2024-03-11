from django.urls import path
from .views import CompanySpotsAPIView, DeliveryLayersAPIView, DeliveryLayersDetailAPIView, CompanySpotsDetailAPIView

urlpatterns = [
    path('company_spots/', CompanySpotsAPIView.as_view(), name='company-spot-list'),
    path('delivery_layers/', DeliveryLayersAPIView.as_view(), name='delivery-layers-list'),
    path('delivery_layers/<int:pk>/', DeliveryLayersDetailAPIView.as_view(), name='delivery-layer-detail'),
    path('company_spots/<int:pk>/', CompanySpotsDetailAPIView.as_view(), name='company-spot-detail'),

]
