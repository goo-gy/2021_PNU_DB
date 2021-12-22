from django.shortcuts import render, resolve_url
from django.db import connection

# sqlQuery = "SELECT studentID, name, score, county FROM Students;"

dict_header = {
    "query1": ["County", "AVG(Score)"],
    "query2": ["City", "AVG(Score)"],
    "query3": ["Professor", "Student"],
    "query4": ["Professor", "Student"],
    "query5": ["Student", "City"], 
}

dict_query = {
    "query1":"SELECT county, AVG(score) FROM students GROUP BY county ORDER BY county;",
    "query2":"SELECT city, AVG(score) FROM (SELECT studentID, score, city FROM students JOIN counties ON students.county = counties.countyName ) AS studentCounty GROUP BY city ORDER BY city;",
    "query3":"""SELECT topP.name, topS.name FROM 
( SELECT name, county FROM professors p1 WHERE NOT EXISTS (SELECT * FROM professors WHERE county=p1.county AND age > p1.age AND facultyID<>p1.facultyID) ) AS topP
JOIN
( SELECT name, county FROM students s1 WHERE NOT EXISTS (SELECT * FROM students WHERE county=s1.county AND score > s1.score AND studentID<>s1.studentID) ) AS topS
ON topS.county=topP.county ORDER BY topS.county;""",
    "query4": """SELECT topP.name, topS.name FROM
( SELECT name, city FROM students s1, counties c1 WHERE s1.county=c1.countyName AND NOT EXISTS (SELECT * FROM students, counties WHERE county=countyName AND city=c1.city AND studentID<>s1.studentID AND score > s1.score) ) AS topS,
( SELECT name, city FROM professors s1, counties c1 WHERE s1.county=c1.countyName AND NOT EXISTS (SELECT * FROM professors, counties WHERE county=countyName AND city=c1.city AND facultyID<>s1.facultyID AND age > s1.age) ) AS topP
WHERE topS.city=topP.city ORDER BY topS.city;""",
    "query5":"""SELECT name, city FROM students JOIN
(SELECT countyName, Counties.city FROM Counties JOIN
(SELECT popCOVID.city, popCOVID.num/popCity.num as RATIO FROM 
(SELECT city, SUM(population) as num FROM Counties group by city) AS popCity,
(SELECT city, COUNT(*) as num FROM COVID GROUP BY city) AS popCOVID
WHERE popCity.city=popCOVID.city order by RATIO DESC LIMIT 3) AS topCity
ON Counties.city=topCity.city) as topCounty
ON county=countyName;
""",
}

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

def getData(queryNum):
    with connection.cursor() as cursor:
        cursor.execute(dict_query[queryNum])
        result = cursor.fetchall()
        # print(result)
    return result

def home(request):
    if(request.method == 'GET'):
        try:
            queryNum = request.GET['queryNum']
            if(queryNum in dict_query.keys()):
                result = getData(queryNum)
                return render(request, 'myApp/home.html', {"data": result, "header": dict_header[queryNum]},)
        except:
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
                    return render(request, 'myApp/home.html', {"msg" : "%s가 등록되었습니다." %name})
                except:
                    return render(request, 'myApp/home.html', {"error": {"msg" : "등록에 실패하였습니다.(중복/형식)"}})
        return render(request, 'myApp/home.html', {"error" : {"msg":"파일을 업로드하여 주십시오."}})
