from os import name
from django.contrib import admin
from django.urls import path
from . import views
from django.conf import settings
from django.contrib.staticfiles.urls import static
from django.conf.urls import handler404, handler500

app_name = "Labels_Nudges"

urlpatterns = [
    path('', views.home, name='home'),
    path('personal_info', views.personal_info, name='personal_info'),
    path('topic_preference', views.topic_preference, name='topic_preference'),
    path('ghs_fk', views.ghs_fk, name='ghs_fk'),
    path('ghs_fk2', views.ghs_fk2, name='ghs_fk2'),
    path('redemption/<int:phase>/', views.redemption, name='redemption'),
    # path('submit-saved-articles/', views.submit_saved_articles, name='submit_saved_articles'),
    path('list_news', views.list_news, name='list_news'),
    path('list_img', views.list_img, name='list_img'),
    path('choice_evaluation', views.choice_evaluation, name='choice_evaluation'),
    path('choice_evaluation2', views.choice_evaluation2, name='choice_evaluation2'),
    path('choice_evaluation4', views.choice_evaluation4, name='choice_evaluation4'),
    path('choice_evaluation5', views.choice_evaluation5, name='choice_evaluation5'),
    path('choice_evaluation6', views.choice_evaluation6, name='choice_evaluation6'),
    path('choice_evaluation7', views.choice_evaluation7, name='choice_evaluation7'),
    path('choice_evaluation8', views.choice_evaluation8, name='choice_evaluation8'),
    path('choice_evaluation9', views.choice_evaluation9, name='choice_evaluation9'),
    path('choice_evaluation10', views.choice_evaluation10, name='choice_evaluation10'),
    path('thanks', views.thank_u, name='thank_u')
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = views.error_404
handler500 = views.error_500
