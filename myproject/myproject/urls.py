from django.urls import path
from myproject import views
from myproject import api_views

urlpatterns = [
    path('', views.index, name='index'),
    path('tasks/', api_views.TaskList.as_view(), name='tasks'),
    path('tasks/<int:task_key>/', api_views.GetTask.as_view(), name='get-task'),
    path('tasks/pending/', api_views.PendingTaskList.as_view(), name='pending-tasks'),
    path('tasks/completed/', api_views.CompletedTaskList.as_view(), name='completed-tasks'),
]
