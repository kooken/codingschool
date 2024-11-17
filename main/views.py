# main/views.py
from django.shortcuts import render


def index(request):
    return render(request, 'main/index.html')


def courses(request):
    return render(request, 'main/courses.html')


def mission(request):
    return render(request, 'main/mission.html')


def community(request):
    return render(request, 'main/community.html')


def job_search(request):
    return render(request, 'main/job_search.html')


def team(request):
    return render(request, 'main/team.html')
