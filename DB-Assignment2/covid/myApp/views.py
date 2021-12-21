from django.shortcuts import render
from django.db import connection

# sqlQuery = "SELECT studentID, name, score, county FROM Students;"

def saveWithCSV(table, file):
    content = file.read().decode('utf8')
    csvData = content.split('\n')
    with connection.cursor() as cursor:
        insertSQL = "INSERT INTO %s VALUES" %(table)
        li_strTuple = []
        for row in csvData:
            # TODO: Error Handling (get table info & compare with data)
            tuple = row.strip().split(',')
            strTuple = " ('" + "','".join(tuple) + "')"
            li_strTuple.append(strTuple)
        insertSQL += ",".join(li_strTuple) + ';'
        cursor.execute(insertSQL)

def home(request):
    if(request.method == 'GET'):
        return render(request, 'myApp/home.html')
    elif(request.method == 'POST'):
        if(len(request.FILES)):
            li_name = ['Students', 'Professors', 'Counties', 'COVID']
            for name in li_name:
                try:
                    file = request.FILES[name]
                except:
                    print("pass", name)
                    continue
                try:
                    saveWithCSV(name, file)
                    return render(request, 'myApp/home.html', {"msg": "%s가 등록되었습니다." %name})
                except:
                    return render(request, 'myApp/home.html', {"error": {"msg":"등록에 실패하였습니다.(중복/형식)"}})
        return render(request, 'myApp/home.html', {"error": {"msg":"파일을 업로드하여 주십시오."}})
