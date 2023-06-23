import json
import re
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import uuid
from decouple import config
from api.models import Plan,Feature,Category,video,Thread,ChatMessage,EditEmail
from .serializers import CategorySerializer, ChatSerializer, FeatureSerializer, PlanSerializer, ThreadSerializer, TrainerSerializer, UserSerializer, VideoSerializer,UserEditSerializer
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
from django.db.models import Q
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail


User = get_user_model()

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['is_superuser'] = user.is_superuser
        token['role']= user.role
        token['own_plan'] = user.own_plan
        token['assigned_trainer'] = user.assigned_trainer
        token['date_joined'] = user.date_joined.isoformat() 
        token['height'] = user.height
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
            users = User.objects.filter(role=User.CUSTOMER).exclude(Q(own_plan=True) & Q(assigned_trainer=False))
            print(users)
        elif user.role == User.TRAINER:
            # Trainer view logic
            trainer_id = user.id
            users = User.objects.filter(role=User.CUSTOMER, trainer_id=trainer_id)
            print(users)
        
        elif user.role == User.CUSTOMER:
            user_id=user.id
            users=User.objects.filter(id=user_id)
            print("test",user)

        else:
            return Response({"message": "Unauthorized"}, status=403)
        
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=200)

class GetMembers(APIView):
    def get(self, request):
        users=User.objects.filter(role=User.CUSTOMER,own_plan=True,assigned_trainer=False)  
        print("membes",users)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status = status.HTTP_200_OK)
        

    
class UserView(APIView):
    def get(self,request,user_id):
        try:
            user = User.objects.get(id=user_id)
        except user.DoesNotExist:
            return Response(status=404)

        serializer = UserSerializer(user)
        return Response(serializer.data, status = status.HTTP_200_OK)
class UserEntry(APIView):
     def post(self,request,user_id):
        user=User.objects.get(id=user_id)
        serializer=UserSerializer(instance=user,data=request.data,partial=True)
    
        if serializer.is_valid():
            serializer.save()
            print(serializer.data)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

class UserEdit(APIView):
    def post(self,request,user_id):
        user=User.objects.get(id=user_id)
        verification_id=str(uuid.uuid1())
        if request.data['email']!= user.email:
            print("email",request.data['email'])
            print(user.email)
            new_email=user.email
            EditEmail.objects.create(new_email=request.data['email'],user_id=request.user.id,uuid=verification_id)
            verification_url=config('FRONTEND_DOMAIN')+'/verify-email/'+verification_id
            subject = 'Email verification process'
            message = ' You are receiving this email because you requested to change your email in fithub profile. Please Click below link to edit email. Thanks for using our site! '+verification_url
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [new_email]
            send_mail( subject, message, email_from, recipient_list )
       

        serializer=UserEditSerializer(instance=user,data=request.data,partial=True)
    
        if serializer.is_valid():
            serializer.save()
            print("data",serializer.data)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

class VerifyEmail(APIView):
    def post(self,request,verification_id):
        if not EditEmail.objects.filter(uuid=verification_id).exists():
            return Response({"message": "Sorry, this link is no more available"}, status=401)
        else:
            print(verification_id)
            verify=EditEmail.objects.get( uuid=verification_id)
            print(verify)
            edit=EditEmail.objects.get(user_id=verify.user_id)

            user=User.objects.get(id=verify.user_id)
            user.email=edit.new_email
            user.save()
            edit.delete()
            return Response(status='200')


class UserBlock(APIView):
    def post(self,request,user_id):
        user=User.objects.get(id=user_id)
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
            
            return Response(status = status.HTTP_200_OK)

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
            return Response(serializer.data,status='200')
    
class GetCurrentPlan(APIView):
    def get(self,request,user_id):
        user = User.objects.get(id=user_id)
        current_plan = Plan.objects.get(id=user.plan_id)
        serializer = PlanSerializer(current_plan)  # Assuming you have a serializer for the Plan model
        return Response(serializer.data, status=status.HTTP_200_OK)

            
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
            plan_type=request.data["plan_type"]
            user.plan_id=plan_id
            user.own_plan=True
            user.plan_type=plan_type
            user.save()
            return Response(status=status.HTTP_200_OK)
            
class GetSinglePlan(APIView):
    def get(self, request, plan_id):  # Use patch method instead of post
        plan = Plan.objects.get(id=plan_id)
        serializer = PlanSerializer(plan)
        print("data",serializer.data)
        return Response(serializer.data,status=status.HTTP_200_OK)


class EditPlan(APIView):
    def post(self, request, plan_id):  # Use patch method instead of post
        plan = Plan.objects.get(id=plan_id)
        serializer = PlanSerializer(instance=plan, data=request.data, partial=True)  # Specify partial=True
        if serializer.is_valid():
            serializer.save()
            print(serializer.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class UpgradePlan(APIView):
    def post(self,request):
        user_id=request.data["user_id"]
        plan_id=request.data["plan_id"]
        print("user",user_id)
        print("user",plan_id)
        plan=User.objects.get(id=user_id)
        print("pl",plan.plan_id)
        plan.plan_id=plan_id
        plan.save()
        return Response(status=status.HTTP_200_OK)



class DeletePlan(APIView):
    def post(self,request,plan_id):
        print("delete")
        plan=Plan.objects.get(id=plan_id)
        plan.delete()
        return Response({"message": "successfully deleted"}, status=status.HTTP_200_OK)

# class Categories(APIView):
    
#     def get(self,request):
#         print(request.data)

#         categories=Category.objects.all()
#         serializer=CategorySerializer(categories,many=True)
#         return Response(serializer.data,status=status.HTTP_200_OK)
class Categories(APIView):
    def get(self,request):
        
        if request.user.is_authenticated:
            if request.user.role == User.ADMIN:
                categories = Category.objects.all()
            else:
                categories = Category.objects.filter(is_active=True)
        else:
            categories = Category.objects.filter(is_active=True)


        serializer=CategorySerializer(categories,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)



class AddCategory(APIView):
    def post(self,request):
        print(request.data)
        serializer=CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "successfully added"}, status=status.HTTP_200_OK)
        # def post(self, request):
        # category_id = request.data.get('id')  # Get the 'id' parameter from the request data
        # if category_id:
        #     category = Category.objects.get(id=category_id) # Fetch the existing category
        #     serializer = CategorySerializer(instance=category, data=request.data)  # Pass the existing category instance
        # else:
        #     serializer = CategorySerializer(data=request.data)  # Create a new category instance
        
        # if serializer.is_valid():
        #     serializer.save()
        #     if category_id:
        #         return Response({"message": "successfully updated"}, status=status.HTTP_200_OK)
        #     else:
        #         return Response({"message": "successfully added"}, status=status.HTTP_200_OK)
        # else:
        #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EditCategory(APIView):
    def post(self,request,category_id):
        category=Category.objects.get(id=category_id)
        serializer=CategorySerializer(instance=category,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response( serializer.data)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

class BlockCategory(APIView):
    def post(self,request,category_id):
        category=Category.objects.get(id=category_id)
        category.is_active = not category.is_active
        category.save()
        return Response( status = status.HTTP_200_OK)
        
class DeleteCategory(APIView):
    def post(self,request,category_id):
        category=Category.objects.get(id=category_id)
        category.delete()
        return Response({"message": "successfully deleted"}, status=status.HTTP_200_OK)



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

class EditVideo(APIView):
    def post(self, request, video_id):
        video_single=video.objects.get(id=video_id)
        serializer=VideoSerializer(instance=video_single,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response( serializer.data)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)



class DeleteVideo(APIView):
    def post(self, request, video_id):
        print(video_id)
        video_single=video.objects.get(id=video_id)
        video_single.delete()
        return Response({"message": "successfully deleted"}, status=status.HTTP_200_OK)


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

class GetAssignedUsers(APIView):
    def get(self,request,trainer_id):
        users=User.objects.filter(trainer_id=trainer_id)
        serializer=UserSerializer(users,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

class GetCount(APIView):
    def get(self,request):
        user_count=User.objects.filter(role=User.CUSTOMER).count()
        print("usercount",user_count)
        member_count=User.objects.filter(role=User.CUSTOMER,own_plan=True).count()
        print("membercount",member_count)
        trainer_count=User.objects.filter(role=User.TRAINER).count()
        print("trainercount",trainer_count)
        return Response({'user_count': user_count,'member_count': member_count,'trainer_count': trainer_count})

class Statistics(APIView):
    def get(self, request):
        packages = Plan.objects.all()
        data = {
            'packages': [],
            'userCounts': []
        }

        for plan in packages:
            user_count = User.objects.filter(plan_id=plan.id).count()
            data['packages'].append(plan.type)
            data['userCounts'].append(user_count)

        return Response(data)



class ChatConsumer(APIView):

    def get(self, request):
        print("vaa",request.user)
        # threads = Thread.objects.filter(Q(first_person=user_id) | Q(second_person=user_id)).prefetch_related('chatmessage_thread').order_by('timestamp')
        threads = Thread.objects.by_user(user=request.user).prefetch_related('chatmessage_thread').order_by('timestamp')
        print("this is",threads)
        serializer = ThreadSerializer(threads, many=True)
        return Response(serializer.data)

class GetChat(APIView):
    def get(self,request,user_id,trainer_id,thread_id)  :
        print("user",user_id)  
        print("trainer",trainer_id)
        print("thread",thread_id)
        chats=ChatMessage.objects.filter(thread_id=thread_id)
        serializer = ChatSerializer(chats, many=True)
        return Response(serializer.data)

    
class ThreadView(APIView):
    def post(self, request):
        print("req",request.data)
        user_ids = request.data.get('users', [])
        if len(user_ids) != 2:
            return Response({'error': 'Invalid number of users'}, status=400)
        
        user1_id, user2_id = user_ids
        print("1",user1_id)
        print("2",user2_id)
        thread = Thread.objects.filter(
            Q(first_person_id=user1_id, second_person_id=user2_id) |
            Q(first_person_id=user2_id, second_person_id=user1_id)
        ).first()

        if thread is None:
            # Create new thread
            user1 = User.objects.get(id=user1_id)
            user2 = User.objects.get(id=user2_id)
            thread = Thread.objects.create(
                first_person=user1,
                second_person=user2
            )

        serializer = ThreadSerializer(thread)
        print(serializer.data)
        return Response(serializer.data)
    
