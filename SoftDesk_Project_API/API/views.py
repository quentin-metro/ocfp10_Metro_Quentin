from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Project, Contributor
from .models import Issue, Comment
from .permissions import IsContributor, IsAuthorContributor, IsAuthorIssue, IsAssigneeIssue, IsAuthorComment
from .serializers import UserSerializer, ProjectSerializer, ContributorSerializer
from .serializers import IssueSerializer, CommentSerializer


@api_view(['POST'])
def signup_view(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.create(request.data)
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response("Invalid request", status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def project_get_or_create(request):
    # GET list of user-associated projects
    if request.method == 'GET':
        user = request.user
        list_project_ids = Contributor.objects.filter(user_id=user).values('project_id')
        projects_list = Project.objects.filter(id__in=list_project_ids)
        if projects_list:
            serializer = ProjectSerializer(projects_list, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({}, status=status.HTTP_200_OK)

    # POST create a new project
    elif request.method == 'POST':
        data = {
            'title': request.data['title'],
            'description': request.data['description'],
            'type': request.data['type'],
            'author_user_id': request.user.id,
        }
        serializer = ProjectSerializer(data=data)
        if serializer.is_valid():
            project = serializer.create(data)
            augmented_serializer_data = serializer.data
            augmented_serializer_data['id'] = project.id
            return Response(augmented_serializer_data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes((IsAuthenticated, IsContributor))
def project_handler(request, project_id):
    user = request.user
    project = Project.objects.get(id=project_id)
    serializer = ProjectSerializer(project)

    contributor = Contributor.objects.get(user_id=user, project_id=project_id)
    # GET the project information
    if request.method == 'GET':
        return Response(serializer.data, status=status.HTTP_200_OK)

    # PUT Update the project
    elif request.method == 'PUT' and contributor.role == "author":
        new_data = {
            'project_id': project.id,
            'title': request.data['title'],
            'description': request.data['description'],
            'type': request.data['type'],
            'author_user_id': request.data['author_user_id'],
        }
        test_serializer = ProjectSerializer(data=new_data)
        if test_serializer.is_valid():
            serializer.edit(new_data)
            project = Project.objects.get(id=project_id)
            serializer = ProjectSerializer(project)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(test_serializer.errors, status=status.HTTP_406_NOT_ACCEPTABLE)

    # DELETE the project
    elif request.method == 'DELETE' and contributor.role == "author":
        project.delete()
        return Response(status=status.HTTP_200_OK)

    else:
        return Response(status=status.HTTP_403_FORBIDDEN)



@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated, IsContributor))
def user_project_get_or_create(request, project_id):

    # GET  list of project-associated users
    if request.method == 'GET':
        contributors_list = Contributor.objects.filter(project_id=project_id)
        if contributors_list:
            serializer = ContributorSerializer(contributors_list, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({}, status=status.HTTP_200_OK)

    # POST add a user to the project
    elif request.method == 'POST':
        user = request.user
        user_contributor = Contributor.objects.get(user_id=user, project_id=project_id)
        # Check if user is the author project
        if user_contributor.role == "author":
            # check if project, user exists and if new_contributor not already exists
            project = get_object_or_404(Project, id=project_id)
            new_contributor_user = get_object_or_404(User, id=request.data['user_id'])
            try:
                existing_contributor = Contributor.objects.get(user_id=request.data['user_id'], project_id=project_id)
            except ObjectDoesNotExist:
                pass
            else:
                serializer = ContributorSerializer(existing_contributor)
                return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
            data_new_contributor = {
                'user_id': new_contributor_user.id,
                'project_id': project,
                'permission': "",
                'role': "assignee"
            }
            contributor = ContributorSerializer(data=data_new_contributor)
            contributor.create(data_new_contributor)
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


@api_view(['DELETE'])
@permission_classes((IsAuthenticated, IsAuthorContributor))
def user_project_delete(request, project_id, user_id):
    contributor = get_object_or_404(Contributor, user_id=user_id, project_id=project_id)
    if contributor.role == "author":
        # Can't delete the author
        return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
    elif contributor.role == "assignee":
        contributor.delete()
        return Response(status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated, IsContributor))
def issue_get_or_create(request, project_id):
    # GET list of the project issues
    if request.method == 'GET':
        get_object_or_404(Project, id=project_id)
        issue_list = Issue.objects.filter(project_id=project_id)
        if issue_list:
            serializer = IssueSerializer(issue_list, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({}, status=status.HTTP_200_OK)

    # POST create a new issue for the project
    elif request.method == 'POST':
        data = {
            'title': request.data['title'],
            'description': request.data['description'],
            'tag': request.data['tag'],
            'priority': request.data['priority'],
            'status': "À faire",
            'author_user_id': request.user.id,
            'assignee_user_id': [request.user.id],
            'project_id': project_id
        }
        serializer = IssueSerializer(data=data)
        if serializer.is_valid():
            issue = serializer.create(data)
            augmented_serializer_data = serializer.data
            augmented_serializer_data['id'] = issue.id
            augmented_serializer_data['time_created'] = issue.time_created
            return Response(augmented_serializer_data, status=status.HTTP_200_OK)

        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'DELETE'])
@permission_classes((IsAuthenticated, IsAuthorIssue))
def issue_handler(request, project_id, issue_id):
    # check if issue exist for the good project and user is author of the issue
    user = request.user
    issue = Issue.objects.get(author_user_id=user, project_id=project_id, id=issue_id)

    # PUT edit the issue
    if request.method == 'PUT':
        # add old_author in assignee if change author
        assignee_user_id_list = []
        for assignee_user_id in request.data['assignee_user_id'].split(','):
            assignee_user_id_list.append(int(assignee_user_id))
        data = {
            'issue_id': issue_id,
            'title': request.data['title'],
            'description': request.data['description'],
            'tag': request.data['tag'],
            'priority': request.data['priority'],
            'status': "À faire",
            'author_user_id': request.data['author_user_id'],
            'assignee_user_id': assignee_user_id_list,
            'project_id': project_id
        }
        test_serializer = IssueSerializer(data=data)
        if test_serializer.is_valid():
            serializer = IssueSerializer(issue)
            serializer.edit(data)
            issue = Issue.objects.get(id=issue_id)
            serializer = IssueSerializer(issue)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(test_serializer.errors, status=status.HTTP_406_NOT_ACCEPTABLE)

    # DELETE the issue
    elif request.method == 'DELETE':
        issue.delete()
        return Response(status=status.HTTP_200_OK)

    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated, IsAssigneeIssue))
def comment_get_or_create(request, project_id, issue_id):
    # GET list of the project issues
    if request.method == 'GET':
        comments_list = Comment.objects.filter(issue_id=issue_id)
        if comments_list:
            serializer = CommentSerializer(comments_list, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({}, status=status.HTTP_200_OK)

    # POST create a new issue for the project
    elif request.method == 'POST':
        data = {
            'description': request.data['description'],
            'author_user_id': request.user.id,
            'issue_id': issue_id
        }
        serializer = CommentSerializer(data=data)
        if serializer.is_valid():
            comment = serializer.create(data)
            augmented_serializer_data = serializer.data
            augmented_serializer_data['id'] = comment.id
            augmented_serializer_data['time_created'] = comment.time_created
            return Response(augmented_serializer_data, status=status.HTTP_200_OK)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes((IsAuthenticated, IsAuthorComment))
def comment_handler(request, project_id, issue_id, comment_id):
    comment = Comment.objects.get(issue_id=issue_id, id=comment_id)

    # PUT edit the comment
    if request.method == 'GET':
        serializer = CommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # PUT edit the comment
    elif request.method == 'PUT':
        data = {
            'comment_id': comment_id,
            'issue_id': comment_id,
            'description': request.data['description'],
            'author_user_id': request.data['author_user_id'],
        }
        test_serializer = CommentSerializer(data=data)
        if test_serializer.is_valid():
            serializer = CommentSerializer(comment)
            serializer.edit(data)
            comment = Comment.objects.get(id=comment_id)
            serializer = CommentSerializer(comment)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(test_serializer.errors, status=status.HTTP_406_NOT_ACCEPTABLE)

    # DELETE the comment
    elif request.method == 'DELETE':
        comment.delete()
        return Response(status=status.HTTP_200_OK)

    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)
