from django.db import models


class AgencySettings(models.Model):
    """Agency general settings - managed by admin"""
    name = models.CharField(max_length=200, default="Asia Decor Samarkand")
    tagline = models.CharField(max_length=300, default="Yaqinlaringizga quvonch baxsh eting")
    bio = models.TextField(blank=True, default="")
    logo = models.ImageField(upload_to='agency/', blank=True, null=True)
    phone1 = models.CharField(max_length=20, blank=True, default="")
    phone2 = models.CharField(max_length=20, blank=True, default="")
    email = models.EmailField(blank=True, default="")
    address = models.CharField(max_length=300, blank=True, default="")
    payment_card = models.CharField(max_length=30, blank=True, default="8600 0000 0000 0000", help_text="Karta raqami")
    payment_card_owner = models.CharField(max_length=100, blank=True, default="")
    advance_percent = models.IntegerField(default=30, help_text="Oldindan to'lov foizi (%)")

    # Social Media
    telegram_link = models.URLField(blank=True, default="", help_text="https://t.me/channelname")
    instagram_link = models.URLField(blank=True, default="", help_text="https://instagram.com/...")
    youtube_link = models.URLField(blank=True, default="", help_text="https://youtube.com/...")
    tiktok_link = models.URLField(blank=True, default="", help_text="https://tiktok.com/@...")
    facebook_link = models.URLField(blank=True, default="", help_text="https://facebook.com/...")

    class Meta:
        verbose_name = "Agentlik sozlamalari"
        verbose_name_plural = "Agentlik sozlamalari"

    def __str__(self):
        return self.name


class ServiceItem(models.Model):
    """Service item (tabrik, bezak, sarpo)"""
    SERVICE_TYPES = [
        ('tabrik', 'Tabriklar'),
        ('bezak', "To'y bezaklari"),
        ('sarpo', "Sarpo-sandiq bezaklari"),
    ]
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES, default='tabrik')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=0)
    price_label = models.CharField(max_length=50, default="so'm", help_text="Masalan: so'm, $ yoki 'dan boshlab'")
    cover_image = models.ImageField(upload_to='services/covers/')
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)  # 🔥 oldingi order → sort_order
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Xizmat"
        verbose_name_plural = "Xizmatlar"
        ordering = ['service_type', 'sort_order']

    def __str__(self):
        return f"{self.get_service_type_display()} - {self.title}"


class ServiceImage(models.Model):
    """Multiple images for a service"""
    service = models.ForeignKey(ServiceItem, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='services/gallery/')
    sort_order = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Xizmat rasmi"
        verbose_name_plural = "Xizmat rasmlari"
        ordering = ['sort_order']


class Order(models.Model):
    PAYMENT_TYPES = [
        ('full', "To'liq to'lov"),
        ('advance', "Oldindan to'lov (zaklad)"),
    ]
    STATUS_CHOICES = [
        ('new', 'Yangi'),
        ('confirmed', 'Tasdiqlangan'),
        ('in_progress', 'Jarayonda'),
        ('completed', 'Bajarilgan'),
        ('cancelled', 'Bekor qilingan'),
    ]

    service = models.ForeignKey(
        ServiceItem,
        on_delete=models.SET_NULL,
        null=True,
        related_name='orders'  # 🔥 clash-free
    )
    service_title = models.CharField(max_length=200)
    service_price = models.DecimalField(max_digits=12, decimal_places=0)

    # Customer info
    customer_name = models.CharField(max_length=200)
    customer_phone = models.CharField(max_length=20)
    delivery_address = models.TextField()

    # Birthday person info
    birthday_person_name = models.CharField(max_length=200)
    birthday_person_age = models.IntegerField()
    event_date = models.DateField(null=True, blank=True)
    event_time = models.TimeField(null=True, blank=True)

    # Payment
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES, default='full')
    amount_paid = models.DecimalField(max_digits=12, decimal_places=0, default=0)

    # Notes
    notes = models.TextField(blank=True)

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')

    # Telegram notification sent?
    telegram_notified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Buyurtma"
        verbose_name_plural = "Buyurtmalar"
        ordering = ['-created_at']

    def __str__(self):
        return f"#{self.id} - {self.customer_name} - {self.service_title}"

    def get_advance_amount(self):
        """Calculate advance payment based on agency settings"""
        settings_obj = AgencySettings.objects.first()
        pct = settings_obj.advance_percent if settings_obj else 30
        return int(self.service_price * pct / 100)