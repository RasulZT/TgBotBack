from django.urls import path
from .views import CompanySpotsAPIView, DeliveryLayersAPIView, DeliveryLayersDetailAPIView, CompanySpotsDetailAPIView,get_addresses,get_matching_coordinates,AddressListView

urlpatterns = [
    path('company_spots/', CompanySpotsAPIView.as_view(), name='company-spot-list'),
    path('delivery_layers/', DeliveryLayersAPIView.as_view(), name='delivery-layers-list'),
    path('delivery_layers/<int:pk>/', DeliveryLayersDetailAPIView.as_view(), name='delivery-layer-detail'),
    path('company_spots/<int:pk>/', CompanySpotsDetailAPIView.as_view(), name='company-spot-detail'),
    path('get_addresses/', get_addresses, name='get_addresses'),
    path('getby_coordinates/',get_matching_coordinates,name="get addr by coord"),
    path('addresses/<int:user_id>/', AddressListView.as_view(), name='address-list'),

]
