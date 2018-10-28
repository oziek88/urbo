from django.db import models

class Reviews(models.Model):
    city = models.CharField(max_length=200, default='Washington DC')
    tour = models.CharField(max_length=200)
    date_of_review = models.IntegerField(default=None)
    source = models.CharField(max_length=200)
    reviewer_name = models.CharField(max_length=200)
    rating = models.IntegerField(default=None)
    description = models.CharField(max_length=2000)
    guide = models.CharField(max_length=200, default=None)
