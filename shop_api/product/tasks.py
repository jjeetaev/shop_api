from celery import shared_task
from django.utils import timezone
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.db.models import Count, Sum, Avg, F
from django.core.files.storage import default_storage
import pandas as pd
import os
from datetime import timedelta
from django.conf import settings
from .models import Product, Category, Review

# 1. ЗАДАЧА ЧЕРЕЗ .delay() - Генерация отчета по товарам
@shared_task
def generate_products_report():
    try:
        products = Product.objects.select_related('category').all()
        
        products_data = []
        for product in products:
            reviews_stats = product.reviews.aggregate(
                total_reviews=Count('id'),
                avg_rating=Avg('stars')
            )
            
            product_data = {
                'Название': product.title,
                'Описание': product.description[:100],
                'Цена': float(product.price),
                'Категория': product.category.name,
                'Количество отзывов': reviews_stats['total_reviews'] or 0,
                'Средний рейтинг': round(reviews_stats['avg_rating'] or 0, 2),
                'Дата создания': product.created.strftime('%Y-%m-%d') if hasattr(product, 'created') else ''
            }
            products_data.append(product_data)
        
        if products_data:
            df = pd.DataFrame(products_data)
            
            report_dir = os.path.join(settings.MEDIA_ROOT, 'reports', 'products')
            os.makedirs(report_dir, exist_ok=True)
            
            filename = f"products_report_{timezone.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            filepath = os.path.join(report_dir, filename)
            
            df.to_excel(filepath, index=False)
            
            return {
                'status': 'success',
                'message': f'Отчет по товарам создан: {filename}',
                'products_count': len(products_data),
                'file_path': filepath
            }
        else:
            return {
                'status': 'info', 
                'message': 'Нет товаров для отчета'
            }
            
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Ошибка при создании отчета по товарам: {str(e)}'
        }

# 2. ЗАДАЧА ПО РАСПИСАНИЮ - Очистка старых данных
@shared_task
def cleanup_old_data():
    try:
        reports_deleted = 0
        report_dir = os.path.join(settings.MEDIA_ROOT, 'reports')
        
        if os.path.exists(report_dir):
            for root, dirs, files in os.walk(report_dir):
                for file in files:
                    if file.endswith('.xlsx'):
                        filepath = os.path.join(root, file)
                        file_time = os.path.getctime(filepath)
                        file_age_days = (timezone.now().timestamp() - file_time) / (24 * 60 * 60)
                        
                        if file_age_days > 7:
                            os.remove(filepath)
                            reports_deleted += 1
        
        return {
            'status': 'success',
            'message': 'Очистка старых отчетов завершена',
            'deleted_reports': reports_deleted
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Ошибка при очистке: {str(e)}'
        }

# 3. ЗАДАЧА С SMTP - Уведомление о новых товарах
@shared_task
def send_new_product_notification(product_id, recipient_emails):
    try:
        product = Product.objects.select_related('category').get(id=product_id)
        
        context = {
            'product': product,
            'notification_date': timezone.now().strftime('%d.%m.%Y'),
        }
        
        html_content = render_to_string('emails/new_product_notification.html', context)
        
        email = EmailMessage(
            subject=f'🆕 Новый товар: {product.title}',
            body=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipient_emails,
        )
        email.content_subtype = "html"
        
        email.send()
        
        return {
            'status': 'success',
            'message': f'Уведомление о товаре "{product.title}" отправлено'
        }
        
    except Product.DoesNotExist:
        return {
            'status': 'error',
            'message': f'Товар с ID {product_id} не найден'
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Ошибка отправки уведомления: {str(e)}'
        }

