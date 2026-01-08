"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.views.generic import RedirectView
from uploads.views import upload_csv, rerun_pipeline, get_dbt_status

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/upload/', permanent=False), name='home'),
    path('upload/', upload_csv, name='upload'),
    path('api/rerun-pipeline/', rerun_pipeline, name='rerun_pipeline'),
    path('api/dbt-status/<int:log_id>/', get_dbt_status, name='dbt_status'),
]
