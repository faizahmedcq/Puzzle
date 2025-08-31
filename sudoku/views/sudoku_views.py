from django.http import FileResponse
from django.shortcuts import render

def sudoku_home(request):
    print("i am in sudoku home")
    return render(request, 'sudoku/home_sudoku.html')

def generate_pdf(request):
    # PDF generation logic here
    print('its working')
    pass
