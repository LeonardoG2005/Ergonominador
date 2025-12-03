"""
URL configuration for ErgoProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views
from pages import views as pages_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', views.dashboard_view, name='dashboard'),  # Vista principal del usuario
    path('get-alerts/', views.get_alerts, name='get_alerts'),
    path("get-sensor-data/", views.get_sensor_data, name="get_sensor_data"),
    path("sensors_view/", views.sensors_view, name="sensors_view"),
    path('', views.index, name='index'),  # Ruta principal para index.html
    path('pages/documentation/', pages_views.documentation, name='documentation'),  # Página de documentación
    path('ui-features/buttons/', views.buttons, name='buttons'),
    path('ui-features/dropdowns/', views.dropdowns, name='dropdowns'),
    path('ui-features/typography/', views.typography, name='typography'),
    path('forms/basic_elements/', views.basic_elements, name='basic_elements'),
    path('charts/chartjs/', views.chart, name='chart'),  # Nueva ruta para chartjs.html
    path('tables/basic_table/', views.basic_tables, name='basic_table'),  # Nueva ruta para chartjs.html
    path('icons/mdi/', views.mdi_view, name='mdi'),  # Nueva ruta para mdi.html
    path('samples/login/', views.login_view, name='login'),  # Nueva ruta para login.html
    path('samples/register/', views.register_view, name='register'),  # Nueva ruta para register.html
]
