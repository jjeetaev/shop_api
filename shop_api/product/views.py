from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Avg
from .models import Category, Product, Review
from .serializers import CategorySerializer, ProductReviewSerializer, ReviewSerializer, ProductSerializer

@api_view(['GET'])
def products_reviews_list(request):
    products = Product.objects.prefetch_related('reviews').all()
    serializer = ProductReviewSerializer(products, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def category_list(request):
    categories = Category.objects.annotate(products_count=Count('products'))
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def category_detail(request, id):
    try:
        category = Category.objects.annotate(products_count=Count('products')).get(id=id)
    except Category.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    serializer = CategorySerializer(category)
    return Response(serializer.data)

@api_view(['GET'])
def product_list(request):
    products = Product.objects.select_related('category').all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def product_detail(request, id):
    try:
        product = Product.objects.prefetch_related('reviews').get(id=id)
    except Product.DoesNotExist:
        return Response(
            data={'error': 'Product not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    serializer = ProductSerializer(product)
    return Response(serializer.data)

@api_view(['GET'])
def review_list(request):
    reviews = Review.objects.select_related('product').all()
    serializer = ReviewSerializer(reviews, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def review_detail(request, id):
    try:
        review = Review.objects.get(id=id)
    except Review.DoesNotExist:
        return Response(
            data={'error': 'Review not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    serializer = ReviewSerializer(review)
    return Response(serializer.data)