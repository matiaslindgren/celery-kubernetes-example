from django.urls import path
from myproject import api_views

urlpatterns = [
    path('', api_views.TaskList.as_view(), name='index'),
    path('<int:task_key>/', api_views.GetTask.as_view(), name='get-task'),
    path('pending/', api_views.PendingTaskList.as_view(), name='pending-tasks'),
    path('completed/', api_views.CompletedTaskList.as_view(), name='completed-tasks'),
]
