from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import BasePermission

from .models import Contributor, Issue, Comment


class IsContributor(BasePermission):
    message = "This user is not a contributor of the project."  # custom error message

    def has_permission(self, request, view):
        project_id = view.kwargs['project_id']
        user = request.user
        try:
            Contributor.objects.get(user_id=user, project_id=project_id)
        except ObjectDoesNotExist:
            return False
        else:
            return True


class IsAuthorContributor(BasePermission):
    message = "This user is not the author of the project."  # custom error message

    def has_permission(self, request, view):
        project_id = view.kwargs['project_id']
        user = request.user
        try:
            Contributor.objects.get(user_id=user, project_id=project_id, role='author')
        except ObjectDoesNotExist:
            return False
        else:
            return True


class IsAuthorIssue(BasePermission):
    message = "This user is not the author of the issue."  # custom error message

    def has_permission(self, request, view):
        project_id = view.kwargs['project_id']
        issue_id = view.kwargs['issue_id']
        user = request.user
        try:
            Issue.objects.get(author_user_id=user, project_id=project_id, id=issue_id)
        except ObjectDoesNotExist:
            return False
        else:
            return True



class IsAssigneeIssue(BasePermission):
    message = "This user is not the author of the issue."  # custom error message

    def has_permission(self, request, view):
        project_id = view.kwargs['project_id']
        issue_id = view.kwargs['issue_id']
        user = request.user
        try:
            issue = Issue.objects.get(project_id=project_id, id=issue_id)

        except ObjectDoesNotExist:
            return False
        else:
            for assignee in issue.assignee_user_id.all():
                if assignee == user:
                    return True
            return False


class IsAuthorComment(BasePermission):
    message = "This user is not the author of the comment."  # custom error message

    def has_permission(self, request, view):
        project_id = view.kwargs['project_id']
        issue_id = view.kwargs['issue_id']
        comment_id = view.kwargs['comment_id']
        user = request.user
        try:
            Issue.objects.get(project_id=project_id, id=issue_id)
            Comment.objects.get(issue_id=issue_id, id=comment_id, author_user_id=user)
        except ObjectDoesNotExist:
            return False
        else:
            return True
