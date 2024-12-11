from django.urls import path
from .views import ucinewgame, isready, position, go, stop, quit, chat

urlpatterns = [
    path('ucinewgame/', ucinewgame, name='ucinewgame'),
    path('isready/', isready, name='isready'),
    path('position/', position, name='position'),
    path('go/', go, name='go'),
    path('stop/', stop, name='stop'),
    path('quit/', quit, name='quit'),
    path('chat/', chat, name='chat'),
]
