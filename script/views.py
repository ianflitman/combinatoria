from django.shortcuts import render
from django.http import HttpResponse
from generator import writer
# Create your views here.

def index(request):
    return HttpResponse("Hello, Jane")

def scene(request):
    script_writer = writer.Writer('jane', scene='marriedtoolong')
    return HttpResponse(script_writer.write_scenario())
