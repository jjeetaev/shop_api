from django.urls import path
from .views import (
    CategoryListCreateView, CategoryDetailView,
    ProductListCreateView, ProductDetailView,
    ReviewListCreateView, ReviewDetailView,
    ProductsWithReviewsListView,
)

urlpatterns = [
    path("categories/", CategoryListCreateView.as_view(), name="category-list"),
    path("categories/<int:id>/", CategoryDetailView.as_view(), name="category-detail"),

    path("products/", ProductListCreateView.as_view(), name="product-list"),
    path("products/<int:id>/", ProductDetailView.as_view(), name="product-detail"),

    path("reviews/", ReviewListCreateView.as_view(), name="review-list"),
    path("reviews/<int:id>/", ReviewDetailView.as_view(), name="review-detail"),

    path("products-reviews/", ProductsWithReviewsListView.as_view(), name="products-reviews"),
]
