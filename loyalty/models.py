from django.db import models



class Action(models.Model):
    id = models.AutoField(primary_key=True)
    company = models.ForeignKey('food.Company', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255,blank=True)
    can_be_triggered = models.BooleanField(default=False)
    date_start = models.DateField()
    date_end = models.DateField()
    triggers = models.ManyToManyField('Trigger')
    payloads = models.ManyToManyField('Payload')



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
