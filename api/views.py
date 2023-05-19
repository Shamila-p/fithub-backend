import json
import re
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from api.models import Plan,Feature,Category,video
from .serializers import CategorySerializer, FeatureSerializer, PlanSerializer, TrainerSerializer, UserSerializer, VideoSerializer
from .serializers import UserSerializerWithToken
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status
from django.db import IntegrityError
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication



User = get_user_model()

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['is_superuser'] = user.is_superuser
        token['role'] = user.role
        return token


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class Signup(CreateAPIView):
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        try:
            user = User.objects.create_user(
                first_name=data['name'],
                email=data['email'],
                username=data['username'],
                phone=data['phone'],
                password=data['password'],
                role=User.CUSTOMER
            )
            serializer = UserSerializer(user, many=False)
            print(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except KeyError as e:
            message = {'detail': f'Missing required field: {e.args[0]}'}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            print("error =", error)
            message = {'detail': 'An unexpected error occurred'}
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class GetUser(APIView):
#     def get(self,request):
#         print("yes")
#         user=User.objects.filter(role=User.CUSTOMER)
#         serializer=UserSerializer(user,many=True)
#         return Response(serializer.data,status='200')
class GetUser(APIView):
    def get(self, request):
        user = request.user
        print(request.user)
        if user.role == User.ADMIN:
            # Admin view logic
            users = User.objects.filter(role=User.CUSTOMER)
            print(users)
        elif user.role == User.TRAINER:
            # Trainer view logic
            trainer_id = user.id
            users = User.objects.filter(role=User.CUSTOMER, trainer_id=trainer_id)
            print(users)

        else:
            return Response({"message": "Unauthorized"}, status=403)
        
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=200)
    
class UserView(APIView):
    def get(self,request,user_id):
        try:
            user = User.objects.get(id=user_id)
        except user.DoesNotExist:
            return Response(status=404)

        serializer = UserSerializer(user)
        return Response(serializer.data, status = status.HTTP_200_OK)

class UserEdit(APIView):
    def post(self,request,user_id):
        user=User.objects.get(id=user_id)
        
        serializer=UserSerializer(instance=user,data=request.data,partial=True)
       
        if serializer.is_valid():
            serializer.save()
            print(serializer.data)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

class UserBlock(APIView):
    def post(self,request,user_id):
        print("enter")
        user=User.objects.get(id=user_id)
        print(user)
        print('this',user.is_active)
        user.is_active= not user.is_active
        user.save()
        return Response({"message": "success"}, status = status.HTTP_200_OK)

class UserDelete(APIView):
    def post(self,request,user_id):
        user=User.objects.get(id=user_id)
        user.delete()
        return Response({"message": "successfully deleted"}, status = status.HTTP_200_OK)
    
class GetTrainers(APIView):
    def get(self,request):
        trainers=User.objects.filter(role=User.TRAINER)
        serializer=TrainerSerializer(trainers,many=True)
        return Response(serializer.data,status='200')

class GetTrainer(APIView):
     def get(self,request,trainer_id):
        print('enter')
        trainers=User.objects.filter(role=User.TRAINER,id=trainer_id)
        serializer=TrainerSerializer(trainers,many=True)
        return Response(serializer.data,status='200')
        

class AddTrainer(APIView):
      # Add TokenAuthentication for authentication
    def post(self,request):
        request_data=request.data
        print(request.data)
        serializer=TrainerSerializer(data=request_data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response( status = status.HTTP_200_OK)

class AssignTrainer(APIView):
    def post(self,request,user_id):
            # user_id = request.data.get('userId')
            trainer_id = request.data.get('trainer_id')
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response({'error': 'User not found'}, status=404)

            try:
                trainer = User.objects.get(id=trainer_id)
            except User.DoesNotExist:
                return Response({'error': 'Trainer not found'}, status=404)

            user.trainer_id = trainer_id
            user.assigned_trainer= True
            trainer.assigned_user=True
            # user.assigned_user=True
            user.save()
            trainer.save()
            return Response( status = status.HTTP_200_OK)

class EditTrainer(APIView):
    def post(self,request,trainer_id):
        print('ok')
        trainer=User.objects.get(id=trainer_id)
        print(trainer)
        serializer=TrainerSerializer(instance=trainer,data=request.data, partial=True)
        print(serializer.is_valid())
        print(serializer.errors)
        if serializer.is_valid():
            serializer.save()
            return Response( serializer.data)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
        

        
class BlockTrainer(APIView):
    def post(self,request,trainer_id):
        print('reached here')
        trainer=User.objects.get(id=trainer_id)
        trainer.is_active=not trainer.is_active
        trainer.save()
        return Response( status = status.HTTP_200_OK)

class DeleteTrainer(APIView):
    def post(self,request,trainer_id):
        trainer=User.objects.get(id=trainer_id)
        trainer.delete()
        return Response({"message": "successfully deleted"}, status = status.HTTP_200_OK)

class GetPlans(APIView):
    def get(self,request):
            queryset = Plan.objects.all()
            serializer= PlanSerializer(queryset,many=True)
            print(serializer.data)
            return Response(serializer.data,status='200')
            
        # plans=Plan.objects.all()
        # features=[]
        # for plan in plans:
        #     features.append(Feature.objects.filter(plan_id=plan.id))
        # serializer=PlanSerializer(data=plans,many=True)
        # fseriaizer=FeatureSerializer(data=features,many=True)




class AddPlan(APIView):
    def post(self, request):
        print(request.data)
        serializer = PlanSerializer(data=request.data)
        if serializer.is_valid():
            features = request.data.get('features', [])  # Get the features from request.data
            serializer.save(features=features)  # Pass features as an argument to serializer.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AssignPlan(APIView):
        def post(self,request):
            user=User.objects.get(id=request.user.id)
            plan_id=request.data["plan_id"]
            user.plan_id=plan_id
            user.own_plan=True
            user.save()
            return Response(status=status.HTTP_200_OK)
            
    

class EditPlan(APIView):
    def put(self, request, plan_id):  # Use patch method instead of post
        plan = Plan.objects.get(id=plan_id)
        serializer = PlanSerializer(instance=plan, data=request.data, partial=True)  # Specify partial=True
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeletePlan(APIView):
    def post(self,request,plan_id):
        print("delete")
        plan=Plan.objects.get(id=plan_id)
        plan.delete()
        return Response({"message": "successfully deleted"}, status=status.HTTP_200_OK)

class Categories(APIView):
    def get(self,request):
        categories=Category.objects.all()
        serializer=CategorySerializer(categories,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)


class AddCategory(APIView):
    def post(self,request):
        serializer=CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "successfully added"}, status=status.HTTP_200_OK)

class GetVideos(APIView):
    def get(self,request,category_id):
        videos=video.objects.filter(category_id=category_id)
        serializer=VideoSerializer(videos,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

class ShowVideos(APIView):
    def get(self,request):
        videos=video.objects.all()
        serializer=VideoSerializer(videos,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

# class AddVideo(APIView):
#     def post(self,request,category_id):
#         category=Category.objects.get(id=category_id)
#         serializer=VideoSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save(category=category)
#             print(serializer.data)
#             return Response({"message": "successfully added"}, status=status.HTTP_200_OK)

class AddVideo(APIView):
    def post(self, request, category_id):
        category=Category.objects.get(id=category_id)
        serializer = VideoSerializer(data=request.data)
        if serializer.is_valid():
            video = serializer.save(category=category)
            response_data = serializer.data
            response_data['thumbnail_url'] = serializer.get_thumbnail_url(video)
            print(response_data)
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UploadImage(APIView):
    def post(self,request,user_id):
            user=User.objects.get(id=user_id)
            data = request.data["image"]
            user.profile_image = data
            user.save()
            serializer = TrainerSerializer(user)
            print(serializer.data)
            return Response(serializer.data,status = status.HTTP_200_OK)

class ChangePassword(APIView):
    def post(self,request):
        user=User.objects.get(id=request.data['id'])
        current_password = request.data['current_password']
        new_password = request.data['new_password']
        confirm_password = request.data['confirm_password']

        # Validate the user's current password
        if not request.user.check_password(current_password):
            return Response({'error': 'Invalid current password.'}, status=400)

        # Verify the new password and confirm password match
        if new_password != confirm_password:
            return Response({'error': 'New password and confirm password do not match.'}, status=400)

        # Update the user's password
        user.set_password(new_password)
        user.save()
        return Response({'message': 'Password changed successfully.'}, status=200)
