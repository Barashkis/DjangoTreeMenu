from django.db import models
from django.core.exceptions import ValidationError
from django.utils.text import slugify


class Menu(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Url(models.Model):
    uri = models.CharField(max_length=255, unique=True)
    name = models.BooleanField()

    def __str__(self):
        return f'/{self.uri}'

    def save(self, *args, **kwargs):
        self.uri = slugify(self.uri.strip('/'))

        super().save()


def get_item_descendants(item: 'Item'):
    children = item.children.all()
    if not children:
        return []
    elif item.parent is None:
        return list(Item.objects.filter(menu=item.menu).exclude(pk=item.pk))

    descendants = []
    for child in children:
        descendants += [child] + get_item_descendants(child)

    return descendants


class Item(models.Model):
    title = models.CharField(max_length=255)
    url = models.OneToOneField(Url, on_delete=models.CASCADE)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name='items')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    def __str__(self):
        return f"{self.title}, menu '{self.menu}'"

    def clean(self):
        if self.parent:
            if self.menu != self.parent.menu:
                raise ValidationError('The parent must have the same menu as item instance itself.')
        else:
            if Item.objects.filter(menu=self.menu, parent=None).exclude(pk=self.pk).exists():
                raise ValidationError('Selected menu already has root item.')

        item_qs = Item.objects.filter(pk=self.pk)
        if item_qs.exists():
            if not item_qs.first().parent and self.parent:
                raise ValidationError('Selected menu can\'t have no root item.')
            elif self.parent in self.children.all():
                raise ValidationError('There can\'t be circular menu. Specify a valid parent object.')

        if self.parent == self:
            raise ValidationError('The parent can\'t be the same as item instance itself.')

        super().clean()

    def save(self, *args, **kwargs):
        old_qs = Item.objects.filter(pk=self.pk)
        if old_qs.exists():
            old_instance = old_qs.first()
            original_menu, new_menu = old_instance.menu, self.menu
            if new_menu != original_menu:
                descendants = get_item_descendants(old_instance)
                for descendant in descendants:
                    descendant.menu = new_menu
                    descendant.save()

        super().save()


class ItemProxy(Item):
    class Meta:
        proxy = True
        verbose_name = 'Root Item'
        verbose_name_plural = 'Root Items'
