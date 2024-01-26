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
    path('order-products/<int:pk>/', OrderProductDetailAPIView.as_view(), name='order-product-detail')
]
