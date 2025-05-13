from django import template

register = template.Library()

@register.filter
def class_name(obj):
    """Retourne le nom de la classe d'un objet"""
    return obj.__class__.__name__
