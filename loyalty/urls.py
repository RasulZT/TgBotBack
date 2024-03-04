from django.urls import path
from .views import ActionListView, ActionDetailView, TriggerListView, PayloadListView, PromosAPIView

urlpatterns = [
    path('actions/', ActionListView.as_view(), name='action-list'),
    path('actions/<int:pk>/', ActionDetailView.as_view(), name='action-detail'),
    path('triggers/', TriggerListView.as_view(), name='trigger-list'),
    path('payloads/', PayloadListView.as_view(), name='payload-list'),
    path('promos/', PromosAPIView.as_view(), name='promos-list'),
]
