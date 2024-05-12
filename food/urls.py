from django.urls import path
from .views import *

urlpatterns = [
    path('categories/', GetAllCategoriesView.as_view(), name='all-categories'),
    path('categories/<int:category_id>/', CategoryDetailView.as_view(), name='category-detail'),
    path('categories/<int:category_id>/products/', GetProductsByCategoryView.as_view(), name='products-by-category'),
    path('products/<int:product_id>/', ProductDetailView.as_view(), name='product-detail'),
    path('orders/', OrderListAPIView.as_view(), name='order-list'),
    path('orders/<int:pk>/', OrderDetailAPIView.as_view(), name='order-detail'),
    path('order-products/', OrderProductListAPIView.as_view(), name='order-product-list'),
    path('order-products/<int:pk>/', OrderProductDetailAPIView.as_view(), name='order-product-detail'),
    path('order/<int:order_id>/', OrderWithActionsAPIView.as_view(), name='order-with-actions'),
    path('modifiers/', ModifierListCreateAPIView.as_view(), name='modifier-list'),
    path('modifiers/<int:pk>/', ModifierRetrieveUpdateDestroyAPIView.as_view(), name='modifier-detail'),
    path('additions/', AdditionListAPIView.as_view(), name='addition-list'),
    path('additions/<int:pk>/', AdditionDetailAPIView.as_view(), name='addition-detail'),
    path('tags/', TagListAPIView.as_view(), name='tag-list'),
    path('tags/<int:pk>/', TagDetailAPIView.as_view(), name='tag-detail'),
    path('filter_orders/', OrderFilterListAPIView.as_view(), name='order-list'),
    path('order_count/<int:pk>/', OrderCountBonus.as_view(), name='order-bonus-count')
]
