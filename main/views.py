# main/views.py
from django.shortcuts import render


def index(request):
    return render(request, 'main/index.html')


def courses(request):
    return render(request, 'main/courses.html')


def mission(request):
    return render(request, 'main/mission.html')


def team(request):
    return render(request, 'main/team.html')
