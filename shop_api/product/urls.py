from django.urls import path
from . import views

urlpatterns = [
    path('categories/', views.category_list),
    path('categories/<int:id>/', views.category_detail),
    path('products/', views.product_list),
    path('products/<int:id>/', views.product_detail),
    path('reviews/', views.review_list),
    path('reviews/<int:id>/', views.review_detail),
    path('products/reviews/', views.products_reviews_list),  # Все товары с отзывами и рейтингом
]