from django.shortcuts import render
import requests
from django import http

import socket

def home(request):
	return render(request, 'pages/home.html')

def handler404(request, exception):
	return render(request,'errors/404.html', {'error': exception},status=404)

def handler500(request, exception=None):
	return render(request,'errors/500.html', {'error': exception},status=500)

def open_ppt(request):
    url = 'http://192.168.225.106/openppt'  # replace with other python app url or ip
    request_data = {'key': 'value'}  # replace with data to be sent to other app
    response = requests.post(url, json=request_data)
    #response_data = response.json()  # data returned by other app
    return render(request, 'pages/home.html') #http.JsonResponse(response_data)

def open_ppt1(request):
    host = '127.0.0.1'
    port = 5000  # initiate port no above 1024
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    print ("Connection on {}".format(port) )
    msg = "open_ppt@"+"C:\\wamp64\\www\\test.pptx"
    sock.send(bytes(msg,"utf-8"))
    msg = sock.recv(1024)
    print(msg.decode("utf-8"))
    print ("Close" )
    sock.close()
    return render(request, 'pages/home.html')