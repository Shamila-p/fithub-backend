from django.urls import path
from . import views


urlpatterns = [
    path('login/',views.MyTokenObtainPairView.as_view()),
    path('signup/',views.Signup.as_view()),
    path('get-user/',views.GetUser.as_view()),
    path('edit/<int:user_id>', views.UserEdit.as_view()),
    path('view-user/<int:user_id>', views.UserView.as_view()),
    path('block-user/<int:user_id>', views.UserBlock.as_view()),
    path('delete-user/<int:user_id>', views.UserDelete.as_view()),
    path('get-trainers/',views.GetTrainers.as_view()),
    path('get-trainer/<int:trainer_id>',views.GetTrainer.as_view()),
    path('add-trainer/',views.AddTrainer.as_view()),
    path('assign-trainer/<int:user_id>',views.AssignTrainer.as_view()),
    path('edit-trainer/<int:trainer_id>',views.EditTrainer.as_view()),
    path('block-trainer/<int:trainer_id>',views.BlockTrainer.as_view()),
    path('delete-trainer/<int:trainer_id>',views.DeleteTrainer.as_view()),
    path('get-plans/',views.GetPlans.as_view()),
    path('add-plan/',views.AddPlan.as_view()),
    path('assign-plan/',views.AssignPlan.as_view()),
    path('edit-plan/<int:plan_id>',views.EditPlan.as_view()),
    path('delete-plan/<int:plan_id>',views.DeletePlan.as_view()),
    path('categories/',views.Categories.as_view()),
    path('add-category/',views.AddCategory.as_view()),
    path('get-videos/<int:category_id>',views.GetVideos.as_view()),
    path('add-video/<int:category_id>',views.AddVideo.as_view()),
    path('show-videos/',views.ShowVideos.as_view()),
    path('show-videos/',views.ShowVideos.as_view()),
    path('upload_image/<int:user_id>',views.UploadImage.as_view()),
    path('change-password/',views.ChangePassword.as_view()),






    ]