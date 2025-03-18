from django.urls import path

from recipes.views import short_link


app_name = 'recipes'

urlpatterns = [
    path('s/<int:id>/', short_link, name='short_link')
]
