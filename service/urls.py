from django.urls import path
from .views import CompanySpotsAPIView, DeliveryLayersAPIView, DeliveryLayersDetailAPIView, CompanySpotsDetailAPIView, \
    get_addresses, get_matching_coordinates, AddressListView, create_reminder, ReminderAPIView, \
    get_users_by_role_or_company, UserCompaniesAPIView, CheckUserIdAPIView, add_user_id_view, UserActionsView, \
    IntegrationCreateView, IntegrationDetailView, PaymentView, PaymentDetailView

urlpatterns = [
    path('company_spots/', CompanySpotsAPIView.as_view(), name='company-spot-list'),
    path('delivery_layers/', DeliveryLayersAPIView.as_view(), name='delivery-layers-list'),
    path('delivery_layers/<int:pk>/', DeliveryLayersDetailAPIView.as_view(), name='delivery-layer-detail'),
    path('company_spots/<int:pk>/', CompanySpotsDetailAPIView.as_view(), name='company-spot-detail'),
    path('get_addresses/', get_addresses, name='get_addresses'),
    path('getby_coordinates/',get_matching_coordinates,name="get addr by coord"),
    path('addresses/<int:user_id>/', AddressListView.as_view(), name='address-list'),
    path('create_reminder/', create_reminder, name='create_reminder'),
    path('users_find/', get_users_by_role_or_company),
    path('reminders/', ReminderAPIView.as_view()),  # для POST и GET всех записей
    path('reminders/<int:pk>/', ReminderAPIView.as_view()),  # для GET, PUT и DELETE конкретной записи
    path('user/<str:user_id>/companies/', UserCompaniesAPIView.as_view(), name='user-companies'),
    path('check-user-id/', CheckUserIdAPIView.as_view(), name='check_user_id'),
    path('add_user_id/', add_user_id_view, name='add_user_id'),
    path('user/<str:user_id>/actions/', UserActionsView.as_view(), name='user-actions'),
    path('integrations/', IntegrationCreateView.as_view(), name='integration-list-create'),
    path('integrations/<int:pk>/', IntegrationDetailView.as_view(), name='integration-detail'),
    path('payments/', PaymentView.as_view(), name='payment-list'),  # Получение всех платежей и создание нового
    path('payments/<str:order_id>/', PaymentDetailView.as_view(), name='payment-detail'),
]
