from django import template
from django.utils.html import mark_safe
from django.urls import reverse

from tree_menu.models import Item


register = template.Library()


@register.simple_tag(takes_context=True)
def draw_menu(context: dict, name: str):
    def draw_li(instance: Item, is_active: bool):
        html = '<li{}><a href="{}">{}</a></li>'
        if instance.url.name:
            html = html.format(' class="active"' if is_active else '',
                               f"{reverse('string', kwargs={'string': instance.url.uri})}", instance.title)
        else:
            html = html.format(' class="active"' if is_active else '',
                               f'{context["request"].scheme}://{context["request"].get_host()}/{instance.url.uri}',
                               instance.title)

        return html

    def construct_menu_string(instance: Item):
        is_active = False
        if active_instance == instance:
            is_active = True

        html = draw_li(instance, is_active)

        if active_level is None:
            return html

        children = instance.children.all()
        if instance == active_instance:
            html += '<ul>'
            for i, child in enumerate(children, start=1):
                html += draw_li(child, False)
            html += '</ul>'
        elif instance in active_instance_parents:
            for i, child in enumerate(children, start=1):
                if i == 1:
                    html += '<ul>'
                html += construct_menu_string(child)
                if i == len(children):
                    html += '</ul>'

        return html

    items_qs = Item.objects.prefetch_related('children').select_related('url').filter(menu__name=name)
    if not items_qs:
        return ''

    active_instance = next(filter(lambda x: f'/{x.url.uri}/' == context['request'].path, items_qs), None)
    active_instance_parents = []
    if active_instance:
        parent = active_instance.parent
        active_instance_parents.append(parent)
        active_level = 0
        while parent:
            parent = parent.parent
            active_instance_parents.append(parent)
            active_level += 1
    else:
        active_level = None

    return mark_safe(f'<ul>{construct_menu_string(items_qs.first())}</ul>')
