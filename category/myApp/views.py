from django.shortcuts import render, redirect
from .models import Students

def home(request):
    if(request.method == 'GET'):
        students = Students.objects.all()
        return render(request, 'myApp/index.html',{"students": students})

def create(request):
    if(request.method == 'POST'):
        try:
            student = Students()
            student.firstname = request.POST['firstname']
            student.secondname = request.POST['secondname']
            student.age = request.POST['age']
            student.major = request.POST['major']
            student.address = request.POST['address']
            student.save()
            return redirect('home')
        except:
            return redirect('home')

    if(request.method == 'GET'):
        return render(request, 'myApp/create.html',{})

def edit(request):
    if(request.method == 'POST'):
        try:
            studentId = request.POST['id']
            student = Students.objects.get(id=studentId)
            student.firstname = request.POST['firstname']
            student.secondname = request.POST['secondname']
            student.age = request.POST['age']
            student.major = request.POST['major']
            student.address = request.POST['address']
            student.save()
            return redirect('home')
        except:
            return redirect('home')
    if(request.method == 'GET'):
        try:
            studentId = request.GET['id']
            student = Students.objects.get(id=studentId)
            return render(request, 'myApp/edit.html', {"student":student})
        except:
            return redirect('home')

def delete(request):
    if(request.method == 'POST'):
        try:
            studentId = request.POST['id']
            student = Students.objects.get(id=studentId)
            student.delete()
            return redirect('home')
        except:
            return redirect('home')

    if(request.method == 'GET'):
        return redirect('home')