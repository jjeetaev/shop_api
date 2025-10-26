from django.urls import path
from . import views

urlpatterns = [
    path("categories/", views.CategoryListCreateView.as_view(), name="category-list"),
    path("categories/<int:id>/", views.CategoryDetailView.as_view(), name="category-detail"),

    path("products/", views.ProductListCreateView.as_view(), name="product-list"),
    path("products/<int:id>/", views.ProductDetailView.as_view(), name="product-detail"),

    path("reviews/", views.ReviewListCreateView.as_view(), name="review-list"),
    path("reviews/<int:id>/", views.ReviewDetailView.as_view(), name="review-detail"),

    path("products-reviews/", views.ProductsWithReviewsListView.as_view(), name="products-reviews"),

    path('tasks/generate-report/', views.trigger_products_report, name='generate-products-report'),
    path('tasks/cleanup/', views.manual_cleanup, name='manual-cleanup'),
    path('tasks/categories-stats/', views.send_categories_stats_manual, name='categories-stats'),
]