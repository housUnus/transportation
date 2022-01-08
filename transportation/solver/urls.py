from django.contrib.auth.decorators import login_required
from django.urls import path

from .views import MainIndexView, solve, renderpdf
app_name = 'solver'


urlpatterns = [
    path('', MainIndexView.as_view(), name='list'),
    path('solve', solve.as_view(), name='solve'),
    path('render', renderpdf, name='render'),

]
