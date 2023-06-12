from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from pytube import YouTube
from api.models import Plan,Feature,Category,video,Thread,ChatMessage

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        print('reached')
        model = User
        fields = ['id','first_name','username','email','phone','age','is_active','height','weight','own_plan','assigned_trainer','trainer_id','gender','plan_type','plan_id']


class UserSerializerWithToken(UserSerializer):
    token = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name','token','role']

    def get_token(self, obj):
        token = RefreshToken.for_user(obj)
        return str(token.access_token)


from django.contrib.auth.hashers import make_password

class TrainerSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'username', 'email', 'phone', 'is_active', 'assigned_user', 'password','role','profile_image']

    
    # def save(self, **kwargs):
    #     print(self.validated_data.get('password'))
    #     # password = make_password(self.validated_data.get('password'))
    #     password=make_password(self.validated_data['password']),
    #     print("new",password)

    #     role = self.validated_data.get('role', User.TRAINER) 
    #     user = super().save(**kwargs)
    #     user.set_password(password)
    #     user.role = role
    #     user.save()
    #     return user

    def create(self, validated_data):
        password = validated_data.pop('password')
        role = self.validated_data.get('role', User.TRAINER) 
        hashed_password = make_password(password)
        trainer = User.objects.create(password=hashed_password,role=role,**validated_data)
        return trainer

class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model=Feature
        fields='__all__'


class PlanSerializer(serializers.ModelSerializer):
    features = FeatureSerializer(many=True, required=False)

    class Meta:
        model = Plan
        fields = '__all__'

    def create(self, validated_data):
        features_data = validated_data.pop('features', '')
        print(features_data)
        features_list = [feature.strip() for feature in features_data.split(',') if feature.strip()]
        print(features_list)
        plan_instance = Plan.objects.create(**validated_data)

        for feature_data in features_list:
            feature = Feature.objects.create(entry=plan_instance)
            feature.feature_text = feature_data
            feature.save()

        return plan_instance
    
    def update(self, instance, validated_data):
        features_data = validated_data.pop('features', '')
        features_list = [feature.strip() for feature in features_data.split(',') if feature.strip()]

        instance.type = validated_data.get('type', instance.type)
        instance.amount = validated_data.get('amount', instance.amount)
        instance.save()

        existing_features = instance.features.all()
        existing_features.delete()

        for feature_data in features_list:
            feature = Feature.objects.create(entry=instance, feature_text=feature_data)
            feature.save()

        return instance

        
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model=Category
        fields="__all__"

class VideoSerializer(serializers.ModelSerializer):
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model=video
        fields="__all__"
    
    def get_thumbnail_url(self, obj):
        # Generate the thumbnail URL from the video URL
        yt = YouTube(obj.url)
        thumbnail_url = yt.thumbnail_url
        return thumbnail_url

from rest_framework import serializers

class ThreadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thread
        fields = '__all__'

class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = '__all__'