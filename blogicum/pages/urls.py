from django.urls import path

from . import views

app_name = 'pages'

urlpatterns = [
    # path('about/', views.about, name="about"),
    # path('rules/', views.rules, name="rules"),
    path('about/', views.AboutView.as_view(), name="about"),
    path('rules/', views.RulesView.as_view(), name="rules"),
]
