import os
from main.models import Profile
from rest_framework.views import APIView
from rest_framework.response import Response
from .tasks import process_file
from celery.result import AsyncResult
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAdminUser
from rest_framework import status
import requests
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView


class MyAPIView(APIView):
    def get(self, request):
        return Response({'title': 'Default route. Method - GET'})

    def post(self, request):
        return Response({'title': 'Default route. Method - POST'})


class UploadView(APIView):
    def post(self, request):
        try:
            if request.user.is_authenticated:
                # Получаем количество МБ свободного пространства на диске
                cmd = "df -m / | awk 'NR==2 {print $4}'"
                output = int(os.popen(cmd).read())

                # Если меньше 10 гигабайт, пишем warning
                if output < 10000:
                    print(f'Free disk space is running out! {output} MB left!')
                # Если меньше гигабайта, прерываем
                elif output < 1000:
                    print(f'Less than {output} MB! Uploading aborted!')
                    return Response({'result': 'fail'})
                else:
                    print(f'Free space {output} MB')

                for name, file in request.FILES.items():
                    if file.size > 1000000:
                        print(f'File is too big: {file.size / 1000} Kb')
                        return Response({'result': 'fail. File is too big. You can upload file < 1Mb'}, status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)

                    is_profile_exists = Profile.objects.filter(user=request.user).exists()
                    profile = None
                    if is_profile_exists:
                        profile = Profile.objects.get(user=request.user)
                        profile.file_name = name
                    else:
                        profile = Profile(user=request.user, file_name=f'media/{name}')

                    with open(f'media/{name}', "wb+") as f:
                        for chunk in file.chunks():
                            f.write(chunk)

                    task = process_file.delay(f'media/{name}')
                    profile.task_id = task.id

                    profile.save()

                    # код добаления имени файла в индекс elasticsearch
                    requests.put(f'http://127.0.0.1:9200/file_index/_doc/{request.user.id}/_create',
                                 json={'title': name},
                                 headers={'content-type': 'application/json'})
                    break

                return Response({'result': 'success'}, status=status.HTTP_201_CREATED)
            return Response({'result': 'Upload failed! Please log-in!'}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            print(e)
            return Response({'result': 'fail'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UploadResultView(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            profile = Profile.objects.get(user=request.user)
            task_result = AsyncResult(profile.task_id)
            if task_result.status == 'SUCCESS' or task_result.status == 'FAILURE':
                return Response({'Download result': task_result.result})
            else:
                return Response({'Download result': task_result.status})

        result = None
        return Response({'result': result})


class OAuthCompleteView(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            user_id = request.user.id
            refresh = RefreshToken.for_user(request.user)

            return Response({'user_id': user_id,
                             'access': str(refresh.access_token),
                             'refresh': str(refresh)
                             })
        else:
            return Response({'error': 'User is not authenticated'}, status=401)


class ElasticSearchView(APIView):
    def get(self, request, q: str):
        result = requests.get(f'http://127.0.0.1:9200/file_index/_search', json={
            "query": {
                "match": {
                    "title": q
                }
            }
        })
        return Response({'result': result.json()})


class SpectacularSwaggerAdminView(SpectacularSwaggerView):
    permission_classes = [IsAdminUser]


class SpectacularRedocAdminView(SpectacularRedocView):
    permission_classes = [IsAdminUser]


class SpectacularAPIAdminView(SpectacularAPIView):
    permission_classes = [IsAdminUser]
