from django import template

register = template.Library()

@register.filter(name='get_item')  # Registra o filtro com o nome 'get_item'
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter(name='zip')
def zip_lists(a, b):
   return zip(a, b)

@register.filter(name='range_custom')
def range_custom(value):
    return range(1, int(value) + 1)
