from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status

import myproject.tasks as tasks
from myproject.models import Task, TaskSerializer

class TaskList(APIView):
    def get(self, request):
        serializer = TaskSerializer(Task.objects.all(), many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            # Save input and put on queue
            task = serializer.save()
            tasks.queue_lcs.delay(task.id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetTask(APIView):
    def get(self, request, task_key):
        try:
            result = Task.objects.get(pk=task_key)
            serializer = TaskSerializer(result)
            return Response(serializer.data)
        except Task.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class PendingTaskList(ListAPIView):
    queryset = Task.objects.filter(lcs__isnull=True)
    serializer_class = TaskSerializer


class CompletedTaskList(ListAPIView):
    queryset = Task.objects.filter(lcs__isnull=False)
    serializer_class = TaskSerializer
