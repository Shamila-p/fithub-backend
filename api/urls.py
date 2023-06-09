from django.urls import path
from . import views


urlpatterns = [
    path('login/',views.MyTokenObtainPairView.as_view()),
    path('signup/',views.Signup.as_view()),
    path('get-user/',views.GetUser.as_view()),
    path('get-members/',views.GetMembers.as_view()),
    # path('add-user-data/',views.AddUserData.as_view()),
    path('edit/<int:user_id>', views.UserEdit.as_view()),
    path('user-entry/<int:user_id>', views.UserEntry.as_view()),
    path('verify-email/<str:verification_id>', views.VerifyEmail.as_view()),
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
    path('get-current-plan/<int:user_id>',views.GetCurrentPlan.as_view()),
    path('add-plan/',views.AddPlan.as_view()),
    path('assign-plan/',views.AssignPlan.as_view()),
    path('edit-plan/<int:plan_id>',views.EditPlan.as_view()),
    path('upgrade-plan/',views.UpgradePlan.as_view()),
    path('get-single-plan/<int:plan_id>',views.GetSinglePlan.as_view()),
    path('delete-plan/<int:plan_id>',views.DeletePlan.as_view()),
    path('categories/',views.Categories.as_view()),
    path('add-category/',views.AddCategory.as_view()),
    path('edit-category/<int:category_id>',views.EditCategory.as_view()),
    path('block-category/<int:category_id>',views.BlockCategory.as_view()),
    path('delete-category/<int:category_id>',views.DeleteCategory.as_view()),
    path('get-videos/<int:category_id>',views.GetVideos.as_view()),
    path('add-video/<int:category_id>',views.AddVideo.as_view()),
    path('edit-video/<int:video_id>',views.EditVideo.as_view()),
    path('delete-video/<int:video_id>',views.DeleteVideo.as_view()),
    path('show-videos/',views.ShowVideos.as_view()),
    path('show-videos/',views.ShowVideos.as_view()),
    path('upload_image/<int:user_id>',views.UploadImage.as_view()),
    path('change-password/',views.ChangePassword.as_view()),
    path('chat/',views.ChatConsumer.as_view()),
    path('get-message/<int:user_id>/<int:trainer_id>/<int:thread_id>',views.GetChat.as_view()),
    path('threads/',views.ThreadView.as_view()),
    path('get-assigned-users/<int:trainer_id>',views.GetAssignedUsers.as_view()),
    path('get-count/',views.GetCount.as_view()),
    path('statistics/',views.Statistics.as_view()),






    ]