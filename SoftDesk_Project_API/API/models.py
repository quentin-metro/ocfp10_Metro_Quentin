from django.db import models
from django.conf import settings


# Create your models here.
class Project(models.Model):
    title = models.fields.CharField(max_length=128)
    TYPE_CHOICES = [
        ("Back-End", "Back-End"),
        ("Front-End", "Front-End"),
        ("iOS", "iOS"),
        ("Android", "Android"),
    ]
    type = models.CharField(max_length=128, choices=TYPE_CHOICES)
    author_user_id = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    objects = models.Manager()


class Contributor(models.Model):
    user_id = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    project_id = models.ForeignKey(to=Project, on_delete=models.CASCADE)
    PERMISSION_CHOICES = [
    ]
    permission = models.CharField(
        max_length=128,
        choices=PERMISSION_CHOICES,
    )
    role = models.fields.CharField(max_length=128)
    objects = models.Manager()


class Issue(models.Model):
    title = models.fields.CharField(max_length=128)
    description = models.fields.CharField(max_length=2048, blank=True)
    TAG_CHOICES = [
        ("BUG", "BUG"),
        ("AMÉLIORATION", "AMÉLIORATION"),
        ("TÂCHE", "TÂCHE"),
    ]
    tag = models.CharField(max_length=128, choices=TAG_CHOICES)
    PRIORITY_CHOICES = [
        ("FAIBLE", "FAIBLE"),
        ("MOYENNE", "MOYENNE"),
        ("ÉLEVÉE", "ÉLEVÉE")
    ]
    priority = models.CharField(max_length=128, choices=PRIORITY_CHOICES)
    STATUS_CHOICES = [
        ("À faire", "À faire"),
        ("En cours", "En cours"),
        ("Terminé", "Terminé")
    ]
    project_id = models.ForeignKey(to=Project, on_delete=models.CASCADE)
    status = models.CharField(max_length=128, choices=STATUS_CHOICES)
    author_user_id = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="author")
    assignee_user_id = models.ManyToManyField(to=settings.AUTH_USER_MODEL, related_name="assignee")
    time_created = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()


class Comment(models.Model):
    description = models.fields.CharField(max_length=2048, blank=True)
    author_user_id = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    issue_id = models.ForeignKey(to=Issue, on_delete=models.CASCADE)
    time_created = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()
