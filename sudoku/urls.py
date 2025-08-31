from django.urls import path
from . import views

urlpatterns = [
    path('', views.sudoku_home, name='sudoku_home'),
    path('generate/', views.generate_sudoku_pdf, name='generate_sudoku_pdf'),
]