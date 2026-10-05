from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('analyze/', views.analyze, name='analyze'),
    path('report/', views.report, name='report'),
    path('actions/', views.actions, name='actions'),
    path('controls/', views.controls, name='controls'),
    path('inspections/', views.inspections, name='inspections'),
    path('rca/', views.rca, name='rca'),
    path('analytics/export/', views.export_reports, name='export_reports'),
    path('analytics/', views.analytics, name='analytics'),
    path('batch/', views.batch_analyze, name='batch'),
    path('dashboard/', views.dashboard, name='dashboard'),
]
