from django.core.exceptions import ValidationError
from django.core.validators import validate_ipv46_address

def get_client_ip(request):
    """Получение и проверка валидности IP-адреса клиента."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')

    # Проверяем валидность IP
    try:
        validate_ipv46_address(ip)
    except ValidationError:
        return "Некорректный IP"

    return ip
