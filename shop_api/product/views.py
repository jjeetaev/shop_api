from rest_framework import generics
from django.db.models import Count
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import api_view
from django.http import JsonResponse
from .models import Category, Product, Review, Order
from .serializers import (
    CategorySerializer,
    ProductReviewSerializer,
    ReviewSerializer,
    ProductSerializer,
)
from users.permissions import IsModerator
from common.validators import validate_user_age  
from .tasks import (
    generate_products_report,
    send_low_stock_alert, 
    send_new_order_notification,
    send_daily_sales_report,
    check_low_stock_and_cleanup
)


class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.annotate(products_count=Count("products"))
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.annotate(products_count=Count("products"))
    serializer_class = CategorySerializer
    lookup_field = "id"
    permission_classes = [IsAuthenticated]


class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.select_related("category").all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            if self.request.user.is_staff:
                return [IsModerator()]  
            return [IsAuthenticated()]  
        return [IsAuthenticated() | IsModerator()]

    def perform_create(self, serializer):
        validate_user_age(self.request.user)
        product = serializer.save()
        check_low_stock_and_cleanup.delay()
        
        return product


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.prefetch_related("reviews").all()
    serializer_class = ProductSerializer
    lookup_field = "id"
    permission_classes = [IsModerator]


class ReviewListCreateView(generics.ListCreateAPIView):
    queryset = Review.objects.select_related("product").all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]


class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    lookup_field = "id"
    permission_classes = [IsAuthenticated]


class ProductsWithReviewsListView(generics.ListAPIView):
    queryset = Product.objects.prefetch_related("reviews").all()
    serializer_class = ProductReviewSerializer
    permission_classes = [IsAuthenticated]


@api_view(['GET'])
def trigger_products_report(request):
    if not request.user.has_perm('products.can_generate_reports'):
        return JsonResponse({'error': 'Нет прав'}, status=403)
    
    task = generate_products_report.delay()
    return JsonResponse({
        'task_id': str(task.id),
        'message': 'Запущена генерация отчета по товарам'
    })


@api_view(['POST'])
def create_order_with_notification(request):
    order_data = request.data
    task = send_new_order_notification.delay(order.id)
    
    return JsonResponse({
        'order_id': order.id,
        'task_id': str(task.id),
        'message': 'Заказ создан, уведомление отправляется'
    })


@api_view(['GET'])
def manual_stock_check(request):
    if not request.user.is_staff:
        return JsonResponse({'error': 'Только для персонала'}, status=403)
    
    email = request.GET.get('email', 'manager@example.com')
    task = send_low_stock_alert.delay(email)
    
    return JsonResponse({
        'task_id': str(task.id),
        'message': f'Проверка остатков запущена, уведомление будет на {email}'
    })


@api_view(['GET'])
def manual_cleanup(request):
    if not request.user.is_staff:
        return JsonResponse({'error': 'Только для администраторов'}, status=403)
    
    task = check_low_stock_and_cleanup.delay()
    return JsonResponse({
        'task_id': str(task.id),
        'message': 'Запущена очистка старых данных и проверка остатков'
    })


@api_view(['GET'])
def send_daily_stats_manual(request):
    if not request.user.is_staff:
        return JsonResponse({'error': 'Только для администраторов'}, status=403)
    
    task = send_daily_sales_report.delay()
    return JsonResponse({
        'task_id': str(task.id),
        'message': 'Запущена отправка ежедневной статистики'
    })