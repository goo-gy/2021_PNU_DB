from django.shortcuts import render, redirect
from .models import Students
from django.contrib import messages

def home(request):
    if(request.method == 'GET'):
        students = Students.objects.all()
        return render(request, 'myApp/index.html', {"students": students})

def create(request):
    if(request.method == 'POST'):
        duplicate = True
        try:
            studentId = request.POST['id']
            student = Students.objects.get(id=studentId)
        except:
            duplicate = False
        if(duplicate):
            return render(request, 'myApp/create.html', {"error": {"msg":"중복된 id입니다."}})
        try:
            student = Students()
            student.id = request.POST['id']
            student.firstname = request.POST['firstname']
            student.secondname = request.POST['secondname']
            student.age = request.POST['age']
            student.major = request.POST['major']
            student.address = request.POST['address']
            student.save()
            students = Students.objects.all()
            return render(request, 'myApp/index.html', {"students": students, "msg": "User가 등록되었습니다."})
        except:
            return render(request, 'myApp/create.html', {"error": {"msg":"ID와 Age에는 숫자를 입력해주세요."}})

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
            students = Students.objects.all()
            return render(request, 'myApp/index.html', {"students": students, "msg": "정상적으로 수정되었습니다."})
        except:
            student = Students.objects.get(id=studentId)
            return render(request, 'myApp/edit.html', {"student":student, "error": {"msg":"Age에는 숫자를 입력해주세요."}})
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
            students = Students.objects.all()
            return render(request, 'myApp/index.html', {"students": students, "msg": "정상적으로 삭제되었습니다."})
        except:
            return redirect('home')

    if(request.method == 'GET'):
        return redirect('home')