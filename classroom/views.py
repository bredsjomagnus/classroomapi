from django.shortcuts import render
from httplib2 import Http
from oauth2client.client import OAuth2WebServerFlow
from django.http import HttpResponseRedirect
from oauth2client import file, client, tools
from googleapiclient.discovery import build
from django.urls import reverse_lazy
from oauth2client.file import Storage
from googleapiclient.errors import HttpError
from django.conf import settings

FLOWCOURSES = OAuth2WebServerFlow(client_id=settings.GOOGLE_OAUTH_CLIENTID,
                            client_secret=settings.GOOGLE_OAUTH_SECRET,
                            scope='https://www.googleapis.com/auth/classroom.courses',
                            redirect_uri='http://localhost:8001/classroom/classroomlist')

FLOWROSTERS = OAuth2WebServerFlow(client_id=settings.GOOGLE_OAUTH_CLIENTID,
                            client_secret=settings.GOOGLE_OAUTH_SECRET,
                            scope='https://www.googleapis.com/auth/classroom.rosters',
                            redirect_uri='http://localhost:8001/classroom/editteachers')


def index(request):
    """
    Route hem eller indexsida.
    """
    return render(request, 'classroom/index.html')

def classroomlist(request):
    """
    Route lista ens klassrum
    """
    if 'code' in request.GET:
            credentials = FLOWCOURSES.step2_exchange(request.GET['code'])
            storage = Storage('courses')
            storage.put(credentials)

    storage = Storage('courses')
    creds = storage.get()
    if creds is None or creds.invalid == True:
        auth_uri = FLOWCOURSES.step1_get_authorize_url()
        return HttpResponseRedirect(auth_uri)
    else:
        service = build('classroom', 'v1', http=creds.authorize(Http()))
        
        results = service.courses().list().execute()
        courses = results.get('courses', [])

    data = {
        "courses": courses
    }

    return render(request, 'classroom/classroomlist.html', data)

def editteachers(request):
    """
    Route fylla i information till att antingen bjuda in eller lägga till lärare till kurs.
    Lite beroende på behörighet.
    """
    courseid = ''
    email = ''
    msg = ''

    if 'code' in request.GET:
        creds = FLOWROSTERS.step2_exchange(request.GET['code'])
        storage = Storage('rosters')
        storage.put(creds)

    storage = Storage('rosters')
    creds = storage.get()
    if creds is None or creds.invalid == True:
        auth_uri = FLOWROSTERS.step1_get_authorize_url()
        return HttpResponseRedirect(auth_uri)
    
    if 'courseid' in request.POST:
        request.session['courseid'] = request.POST['courseid']
        

    if 'email' in request.POST:
        request.session['email'] = request.POST['email']

    data = {
        "msg": msg
    }

    return render(request, 'classroom/editteachers.html', data)

def inviteteacherprocess(request):
    """
    Process för att bjuda in lärare till klassrum via email och kursid.
    """
    storage = Storage('rosters')
    creds = storage.get()
    courseid = request.POST['courseid']
    email = request.POST['email']

    service = build('classroom', 'v1', http=creds.authorize(Http()))

    invitation = {
        "courseId": courseid,
        "userId": email,
        "role": "TEACHER"
    }

    try:
        invit = service.invitations().create(body=invitation).execute()
        msg = 'Användare {0} bjöds in som lärare till kurs med ID "{1}"'.format(email,courseid)
    except HttpError as err:
        msg = err
    except AttributeError as err:
        msg = err
    
    data = {
        "msg": msg
    }

    return render(request, 'classroom/result.html', data)

def createteacherprocess(request):
    """
    Process för att lägga till lärare till klassrum via email och kursid.
    """
    storage = Storage('rosters')
    creds = storage.get()

    courseid = request.POST['courseid']
    email = request.POST['email']
    
    service = build('classroom', 'v1', http=creds.authorize(Http()))
    teacher = {
        'userId': email
    }

    try:
        teacher = service.courses().teachers().create(courseId=courseid,body=teacher).execute()
        msg = 'Användare {0} lades till som lärarare till kurs med ID "{1}"'.format(teacher.get('profile').get('name').get('fullName'),courseid)
    except HttpError as err:
        msg = err
    except AttributeError as err:
        msg = err
    data = {
        "msg": msg
    }

    return render(request, 'classroom/result.html', data)

def deletecred(request):
    """
    Process för att logga ut. Tar bort sparade credentials.
    """
    try:
        storage = Storage('courses')
        storage.delete()
    except FileNotFoundError:
        print("Saknar Storage('courses')")

    try:
        storage = Storage('rosters')
        storage.delete()
    except FileNotFoundError:
        print("Saknar Storage('rosters')")

    return HttpResponseRedirect('/classroom')

