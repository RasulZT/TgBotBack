from django.db import models




class Action(models.Model):
    id = models.AutoField(primary_key=True)
    company = models.ForeignKey('food.Company', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255,blank=True)
    can_be_triggered = models.BooleanField(default=False)
    can_be_repeated = models.BooleanField(default=False)
    image = models.CharField(max_length=255, null=True, blank=True)
    can_use_bonus = models.BooleanField(default=False)  # Можно ли использовать с бонусом
    can_add_bonus = models.BooleanField(default=False)
    date_start = models.DateField(blank=True,null=True)
    date_end = models.DateField(blank=True,null=True)
    triggers = models.JSONField(null=True,blank=True)
    payloads = models.JSONField(null=True,blank=True)



class Trigger(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=255, unique=True)
    payload = models.JSONField(null=True,blank=True)

    def __str__(self):
        return self.name


class Payload(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=255)
    payload = models.JSONField(null=True,blank=True)

    def __str__(self):
        return self.name

class Promos(models.Model):
    token = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    link_to_source = models.CharField(max_length=255, null=True)
    action = models.ForeignKey(Action, on_delete=models.CASCADE,blank=True,null=True)
    amount = models.IntegerField(null=True, blank=True)
    date_start = models.DateTimeField(null=True, blank=True)
    date_end = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(null=True, blank=True)
    auto_add_on_registration = models.BooleanField(default=False,
                                                   help_text="Добавлять акцию автоматически при регистрации")
    replace_existing_promo = models.BooleanField(default=False,
                                                 help_text="Заменить существующее промо, если оно уже связано с пользователем")

class UsedPromos(models.Model):
    user = models.ForeignKey('my_auth.CustomUser', on_delete=models.CASCADE)
    promo = models.ForeignKey(Promos, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'promo')