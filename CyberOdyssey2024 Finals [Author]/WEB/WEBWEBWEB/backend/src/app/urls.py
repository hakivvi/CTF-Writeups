from django.urls import path
from .views import LoginView, WebFrameworkExperiencesView, WebFrameworks, SetHotOfExperienceView, AddWebFrameworkView

urlpatterns = [
    path('login', LoginView.as_view(), name='login'),
    path('webframeworks', WebFrameworks.as_view(), name='webframeworks'),
    path('webframeworks/add', AddWebFrameworkView.as_view(), name='add-webframework'),
    path('experiences', WebFrameworkExperiencesView.as_view(), name='experiences'),
    path('experiences/setHot/<int:id>/<str:hot>', SetHotOfExperienceView.as_view(), name='set-hot')
]
