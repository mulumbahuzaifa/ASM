from django.db import models

# Create your models here.
class Setting(models.Model):
    afparam = models.CharField("Parameter",max_length = 100, primary_key = True)
    afvalue = models.CharField("Value",max_length = 200)
    aftimestamp = models.DateTimeField("Time  stamp",auto_now_add=True, blank=True)
