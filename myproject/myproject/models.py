"""
Persistent storage for arguments and results from longest common substring calls.
"""
from django.db import models
from rest_framework import serializers


class Task(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    string_a = models.TextField()
    string_b = models.TextField()
    lcs = models.TextField(null=True, default=None)

    class Meta:
        ordering = ('-created', )


# API serializer
class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('id', 'created', 'string_a', 'string_b', 'lcs')
