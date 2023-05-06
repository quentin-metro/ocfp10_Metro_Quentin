from rest_framework.serializers import ModelSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404

from .models import Project, Contributor, Issue, Comment


class UserSerializer(ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ["username", 'first_name', 'last_name', 'email', 'password']

    def create(self, data):
        user = User.objects.create(
            username=data['username'],
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name']
        )
        user.set_password(data['password'])
        user.save()
        return user


class ContributorSerializer(ModelSerializer):
    class Meta:
        model = Contributor
        fields = ['id', 'user_id', 'project_id', 'permission', 'role']

    def create(self, data):
        # Create the Contributor
        user = User.objects.get(id=data['user_id'])
        contributor = Contributor.objects.create(
            user_id=user,
            project_id=data['project_id'],
            permission=data['permission'],
            role=data['role'],
        )
        contributor.save()
        return contributor


    def edit(self, data):
        # if exist edit else call create
        try:
            contributor = Contributor.objects.get(user_id=data['user_id'], project_id=data['project_id'])
            contributor.id = contributor.id
            contributor.role = data['role']
            contributor.permission = data['permission']
            contributor.save()
        except ObjectDoesNotExist:
            contributor = self.create(data)

        return contributor




class ProjectSerializer(ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'title', 'description', 'type', 'author_user_id']


    def create(self, data):
        # create Project
        user = User.objects.get(id=data['author_user_id'])
        project = Project.objects.create(
            title=data['title'],
            description=data['description'],
            type=data['type'],
            author_user_id=user
        )
        project.save()

        # create Contributor for the author
        data_contributor = {
            'user_id': data['author_user_id'],
            'project_id': project,
            'permission': "",
            'role': "author"
        }

        contributor = ContributorSerializer(data=data_contributor)
        contributor.create(data_contributor)
        return project

    @staticmethod
    def edit(data):
        # edit Project
        user = User.objects.get(id=data['author_user_id'])
        project = Project.objects.get(id=data['project_id'])
        old_contributor = project.author_user_id
        project.id = project.id
        project.title = data['title']
        project.description = data['description']
        project.type = data['type']
        project.author_user_id = user
        project.save()

        # edit Contributor for the author if change
        if not user == old_contributor:
            # edit old author
            data_old_contributor = {
                'user_id': old_contributor.id,
                'project_id': project,
                'permission': "",
                'role': "assignee"
            }
            contributor = ContributorSerializer(data=data_old_contributor)
            contributor.edit(data_old_contributor)
            # edit new author
            data_new_contributor = {
                'user_id': data['author_user_id'],
                'project_id': project,
                'permission': "",
                'role': "author"
            }
            contributor = ContributorSerializer(data=data_new_contributor)
            contributor.edit(data_new_contributor)

        return project


class IssueSerializer(ModelSerializer):
    class Meta:
        model = Issue
        read_only_fields = ['time_created']
        fields = ['id',
                  'title',
                  'description',
                  'tag',
                  'priority',
                  "project_id",
                  'status',
                  'author_user_id',
                  'assignee_user_id',
                  'time_created'
                  ]

    def create(self, data):
        # Create the issue
        user = User.objects.get(id=data['author_user_id'])
        project = Project.objects.get(id=data['project_id'])
        issue = Issue.objects.create(
            project_id=project,
            author_user_id=user,
            title=data['title'],
            description=data['description'],
            tag=data['tag'],
            priority=data['priority'],
            status=data['status'],
        )

        issue.save()
        issue.assignee_user_id.add(user)
        return issue


    @staticmethod
    def edit(data):
        new_author = User.objects.get(id=data['author_user_id'])
        issue = Issue.objects.get(id=data['issue_id'])

        # Edit the issue
        issue.id = issue.id
        issue.title = data['title']
        issue.description = data['description']
        issue.priority = data['priority']
        issue.tag = data['tag']
        issue.status = data['status']
        # issue.author change
        old_author = issue.author_user_id
        if not new_author == old_author:
            issue.author_user_id = new_author


        issue.save()

        # edit the issue.assignee
        new_assignee_list = data['assignee_user_id']
        if new_author.id not in new_assignee_list:
            new_assignee_list.append(new_author.id)
        project = Project.objects.get(id=data['project_id'])

        # edit the contributor
        for user_id in new_assignee_list:
            try:
                contributor = Contributor.objects.get(project_id=data['project_id'], user_id=user_id)
            except ObjectDoesNotExist:
                pass
            else:
                user = User.objects.get(id=user_id)
                issue.assignee_user_id.add(user)

        return issue


class CommentSerializer(ModelSerializer):
    class Meta:
        model = Comment
        read_only_fields = ['time_created']
        fields = ['id', 'description', 'author_user_id', 'issue_id', 'time_created']

    def create(self, data):
        # Create the comment
        user = User.objects.get(id=data['author_user_id'])
        issue = Issue.objects.get(id=data['issue_id'])
        comment = Comment.objects.create(
            description=data['description'],
            author_user_id=user,
            issue_id=issue,
        )

        comment.save()
        return comment

    @staticmethod
    def edit(data):
        # edit Project
        user = User.objects.get(id=data['author_user_id'])
        comment = Comment.objects.get(id=data['comment_id'])
        comment.id = comment.id
        comment.description = data['description']
        comment.author_user_id = user

        comment.save()
        return comment
