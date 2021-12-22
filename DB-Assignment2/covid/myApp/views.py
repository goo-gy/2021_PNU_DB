from django.shortcuts import render
from django.db import connection
import django
import time

DB_DUP = 1062

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

updateViewSQL = """
DROP TABLE IF EXISTS QUERY5;
CREATE TABLE QUERY5(
	studentName VARCHAR(30),
	city VARCHAR(30),
	PRIMARY KEY(studentName, City)
);
INSERT INTO QUERY5 (studentName, city) %s;
""" %(dict_query["query5"])

def saveWithCSV(table, file):
    content = file.read().decode('utf8')
    csvData = content.split('\n')
    with connection.cursor() as cursor:
        insertSQL = "INSERT INTO %s VALUES" %(table)
        li_strTuple = []
        for row in csvData:
            tuple = row.strip().split(',')
            strTuple = " ('" + "','".join(tuple) + "')"
            li_strTuple.append(strTuple)
        insertSQL += ",".join(li_strTuple) + ';'
        cursor.execute(insertSQL)
    updateView()

def updateView():
    print(updateViewSQL)
    with connection.cursor() as cursor:
        cursor.execute(updateViewSQL)

def getData(queryNum):
    with connection.cursor() as cursor:
        if(queryNum == "query5"):
            query5SQL = "SELECT * FROM QUERY5"
            # TODO : CHECK TIME START
            cursor.execute(query5SQL)
            result = cursor.fetchall()
            # TODO : CHECK TIME END
        else:
            cursor.execute(dict_query[queryNum])
            result = cursor.fetchall()
    return result

def getErrorNum(err):
    errNumStr = str(err).split(',')[0].split('(')[1]
    return int(errNumStr)

def home(request):
    if(request.method == 'GET'):
        try:
            queryNum = request.GET['queryNum']
            if(queryNum in dict_query.keys()):
                result = getData(queryNum)
                objError = {}
                if(len(result) == 0 ):
                    objError["msg"] = "적절한 데이터가 없습니다."
                return render(request, 'myApp/home.html', {"data": result, "header": dict_header[queryNum], "error": objError},)
        except django.utils.datastructures.MultiValueDictKeyError as paramError:
            return render(request, 'myApp/home.html')
        except:
            return render(request, 'myApp/home.html', {"error": {"msg": "적절한 데이터가 없습니다."}})
    elif(request.method == 'POST'):
        if(len(request.FILES)):
            li_name = ['Students', 'Professors', 'Counties', 'COVID']
            for name in li_name:
                try:
                    file = request.FILES[name]
                except:
                    continue
                #-----------------------------
                try:
                    saveWithCSV(name, file)
                    return render(request, 'myApp/home.html', {"msg" : "%s가 등록되었습니다." %name})
                except django.db.utils.IntegrityError as err:
                    errorNum = getErrorNum(err)
                    if(errorNum == DB_DUP):
                        return render(request, 'myApp/home.html', {"error": {"msg" : "중복된 데이터가 있습니다."}})
                    return render(request, 'myApp/home.html', {"error": {"msg" : "잘못된 형식입니다!"}})
                except django.db.utils.OperationalError as err:
                    return render(request, 'myApp/home.html', {"error": {"msg" : "잘못된 형식입니다."}})
                except:
                    return render(request, 'myApp/home.html', {"error": {"msg" : "잘못된 형식입니다!"}})
        return render(request, 'myApp/home.html', {"error" : {"msg":"파일을 업로드하여 주십시오."}})
