from django import template
from ChatApp.models import chatMessages  # eksaktong pangalan ng model

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def unread_count(user_from_id, user_to_id):
    return chatMessages.objects.filter(
        user_from_id=user_from_id,
        user_to_id=user_to_id,
        is_read=False
    ).count()
