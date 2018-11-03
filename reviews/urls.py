from django.urls import path

from . import views

urlpatterns = [
    path('', views.scraper, name='scraper'),
    path('reviews', views.review_results, name='review_results'),
    path('description', views.review_description, name='review_description'),
]