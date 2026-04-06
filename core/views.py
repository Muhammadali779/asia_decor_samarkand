import json
import requests
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import AgencySettings, ServiceItem, Order


def get_agency():
    agency = AgencySettings.objects.first()
    if not agency:
        agency = AgencySettings.objects.create()
    return agency


def home(request):
    agency = get_agency()
    tabriklar = ServiceItem.objects.filter(service_type='tabrik', is_active=True)
    bezaklar = ServiceItem.objects.filter(service_type='bezak', is_active=True)
    sarpo = ServiceItem.objects.filter(service_type='sarpo', is_active=True)
    context = {
        'agency': agency,
        'tabriklar': tabriklar,
        'bezaklar': bezaklar,
        'sarpo': sarpo,
    }
    return render(request, 'home.html', context)


def tabriklar_view(request):
    agency = get_agency()
    items = ServiceItem.objects.filter(service_type='tabrik', is_active=True)
    return render(request, 'tabriklar.html', {'agency': agency, 'items': items})


def bezaklar_view(request):
    agency = get_agency()
    items = ServiceItem.objects.filter(service_type='bezak', is_active=True)
    sarpo = ServiceItem.objects.filter(service_type='sarpo', is_active=True)
    return render(request, 'bezaklar.html', {'agency': agency, 'items': items, 'sarpo': sarpo})


def service_detail(request, pk):
    agency = get_agency()
    item = get_object_or_404(ServiceItem, pk=pk, is_active=True)
    images = item.images.all()
    return render(request, 'service_detail.html', {'agency': agency, 'item': item, 'images': images})


def contacts(request):
    agency = get_agency()
    return render(request, 'contacts.html', {'agency': agency})


@csrf_exempt
def create_order(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            service_id = data.get('service_id')
            service = get_object_or_404(ServiceItem, pk=service_id)
            agency = get_agency()

            payment_type = data.get('payment_type', 'full')

            order = Order.objects.create(
                service=service,
                service_title=service.title,
                service_price=service.price,
                customer_name=data.get('customer_name', ''),
                customer_phone=data.get('customer_phone', ''),
                delivery_address=data.get('delivery_address', ''),
                birthday_person_name=data.get('birthday_person_name', ''),
                birthday_person_age=data.get('birthday_person_age', 0),
                event_date=data.get('event_date') or None,
                event_time=data.get('event_time') or None,
                payment_type=payment_type,
                amount_paid=data.get('amount_paid', 0),
                notes=data.get('notes', ''),
            )

            send_order_to_telegram(order, agency)

            return JsonResponse({
                'success': True,
                'order_id': order.id,
                'card_number': agency.payment_card,
                'card_owner': agency.payment_card_owner,
                'amount': int(order.amount_paid),
                'payment_type': payment_type,
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'error': 'Method not allowed'}, status=405)


def send_order_to_telegram(order, agency):
    """Send order notification to admin via Telegram bot"""
    try:
        payment_emoji = "💳" if order.payment_type == 'full' else "💰"
        payment_label = "To'liq to'lov" if order.payment_type == 'full' else "Oldindan to'lov (zaklad)"

        message = f"""
🔔 <b>YANGI BUYURTMA #{order.id}</b> (Sayt orqali)

📦 <b>Xizmat:</b> {order.service_title}
💵 <b>Narxi:</b> {int(order.service_price):,} so'm

👤 <b>Buyurtmachi:</b>
• Ism: <b>{order.customer_name}</b>
• 📱 Telefon: <code>{order.customer_phone}</code>
• 📍 Manzil: {order.delivery_address}

🎂 <b>Tabriklanuvchi:</b>
• Ismi: {order.birthday_person_name}
• Yoshi: {order.birthday_person_age}
{f"• Sana: {order.event_date}" if order.event_date else ""}
{f"• Vaqt: {order.event_time}" if order.event_time else ""}

{payment_emoji} <b>To'lov:</b> {payment_label}
💰 <b>To'langan summa:</b> {int(order.amount_paid):,} so'm

{f"📝 Izoh: {order.notes}" if order.notes else ""}

⏰ <b>Vaqt:</b> {order.created_at.strftime("%d.%m.%Y %H:%M")}
        """.strip()

        bot_token = settings.ADMIN_BOT_TOKEN
        admin_chat_id = settings.ADMIN_CHAT_ID

        if bot_token and bot_token != 'YOUR_ADMIN_BOT_TOKEN_HERE':
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            requests.post(url, json={
                'chat_id': admin_chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }, timeout=10)
            order.telegram_notified = True
            order.save(update_fields=['telegram_notified'])
    except Exception as e:
        print(f"Telegram error: {e}")


def get_service_api(request, pk):
    """API endpoint for service details (used by bots)"""
    item = get_object_or_404(ServiceItem, pk=pk, is_active=True)
    agency = get_agency()
    images = [request.build_absolute_uri(img.image.url) for img in item.images.all()]
    return JsonResponse({
        'id': item.id,
        'title': item.title,
        'description': item.description,
        'price': int(item.price),
        'price_label': item.price_label,
        'cover_image': request.build_absolute_uri(item.cover_image.url) if item.cover_image else '',
        'images': images,
        'advance_percent': agency.advance_percent,
        'advance_amount': int(item.price * agency.advance_percent // 100),
        'payment_card': agency.payment_card,
        'payment_card_owner': agency.payment_card_owner,
    })


def get_services_api(request):
    """API for all active services grouped by type"""
    agency = get_agency()
    result = {}
    for stype in ['tabrik', 'bezak', 'sarpo']:
        items = ServiceItem.objects.filter(service_type=stype, is_active=True)
        result[stype] = [
            {
                'id': item.id,
                'title': item.title,
                'price': int(item.price),
                'price_label': item.price_label,
                'cover': request.build_absolute_uri(item.cover_image.url) if item.cover_image else '',
            }
            for item in items
        ]
    return JsonResponse({
        'services': result,
        'agency': {
            'name': agency.name,
            'phone1': agency.phone1,
            'phone2': agency.phone2,
            'advance_percent': agency.advance_percent,
            'payment_card': agency.payment_card,
        }
    })


def admin_orders_api(request):
    """Admin: get orders list"""
    status_filter = request.GET.get('status', 'new')
    limit = int(request.GET.get('limit', 20))
    
    qs = Order.objects.all()
    if status_filter != 'all':
        qs = qs.filter(status=status_filter)
    
    orders = []
    for o in qs[:limit]:
        orders.append({
            'id': o.id,
            'service_title': o.service_title,
            'service_price': int(o.service_price),
            'customer_name': o.customer_name,
            'customer_phone': o.customer_phone,
            'delivery_address': o.delivery_address,
            'birthday_person_name': o.birthday_person_name,
            'birthday_person_age': o.birthday_person_age,
            'event_date': str(o.event_date) if o.event_date else '',
            'payment_type': o.payment_type,
            'amount_paid': int(o.amount_paid),
            'status': o.status,
            'telegram_notified': o.telegram_notified,
            'created_at': o.created_at.strftime('%d.%m.%Y %H:%M'),
        })
    return JsonResponse({'orders': orders, 'total': qs.count()})
