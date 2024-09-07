from django.urls import path
from .views import ActionListView, ActionDetailView, TriggerListView, PayloadListView, PromosAPIView, \
    CustomUserActionView,OrderAnalysisView,ActionListViewCompany

urlpatterns = [
    path('actions/', ActionListView.as_view(), name='action-list'),
    path('actions/<int:pk>/', ActionDetailView.as_view(), name='action-detail'),
    path('triggers/', TriggerListView.as_view(), name='trigger-list'),
    path('payloads/', PayloadListView.as_view(), name='payload-list'),
    path('promos/', PromosAPIView.as_view(), name='promos-list'),
    path('analyze-order/', OrderAnalysisView.as_view(), name='analyze_order'),
    path('actions_company/<int:company_id>/', ActionListViewCompany.as_view(), name='action-list-by-company'),
    path('actions_user/', CustomUserActionView.as_view(), name='customuseraction-list'),  # Для получения всех и создания новой записи
    path('actions_user/<int:pk>/', CustomUserActionView.as_view(), name='customuseraction-detail'),  # Для работы с конкретной записью
]
