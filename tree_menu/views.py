from django.shortcuts import render


# Create your views here.
def draw_menu(request, string):
    return render(request, 'index.html')
