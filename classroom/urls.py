from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    # path('authcallback', views.authcallback, name='authcallback'),
    path('classroomlist', views.classroomlist, name='classroomlist'),
    path('editteachers', views.editteachers, name='editteachers'),
    path('inviteteacherprocess', views.inviteteacherprocess, name='inviteteacherprocess'),
    path('createteacherprocess', views.createteacherprocess, name='createteacherprocess'),
    path('deletecred', views.deletecred, name='deletecred')
]