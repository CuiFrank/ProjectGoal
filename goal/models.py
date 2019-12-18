from django.db import models

# Create your models here.

class Goal(models.Model):
    name = models.CharField(max_length=50)
    score = models.IntegerField()



