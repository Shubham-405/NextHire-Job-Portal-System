from django.urls import path
from . import views

urlpatterns = [
    path('', views.Index_Page, name="index"),
    path('jobs/', views.job_listing, name='job_listing'),
    path('about/', views.about, name='about'),
    path('contact/',views.contact,name='contact'),
    path('candidate-register/', views.candidate_register, name='candidate_register'),
    path('candidate-login/', views.candidate_login, name='candidate_login'),
    path('candidate-dashboard/', views.candidate_dashboard, name='candidate_dashboard'),
    path('candidate/update-profile/', views.candidate_update_profile,name='candidate_update_profile'),
    path('candidate/jobs/', views.candidate_job_list, name='candidate_job_list'),
    path("candidate/job-details/<int:job_id>/", views.candidate_job_details, name="candidate_job_details"),
    path("apply-job/<int:job_id>/", views.apply_job_ajax, name="apply_job_ajax"),
        # ...your other paths
    path("candidate/saved-jobs/", views.saved_jobs_list, name="saved_jobs_list"),
    path("chatbot/", views.chatbot, name="chatbot"),
    path('save-job/<int:job_id>/', views.save_job, name='save_job'),
    path('candidate_logout/', views.candidate_logout, name='candidate_logout'),

########################------Company Dashboard------########################################
    path('company-register/', views.company_register, name='company_register'),
    path('company-login/', views.company_login, name='company_login'),
    path('company-dashboard/',views.company_dashboard,name='company_dashboard'),
    path('company/profile/', views.company_profile, name='company_profile'),
    # ✅ Job Posting URL (New)
    path('company/post-job/', views.post_job, name='post_job'),
    path('company/job-list/', views.job_listings, name='job_list'),
    path('company/applications/', views.view_applications, name='view_applications'),
    path('applications/<int:app_id>/', views.application_details, name='application_details'),

    
##########################-------Admin-------################################################
    path("admin-login/", views.admin_login, name="admin_login"),
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),  # example dashboard
    path("custom-admin/userlist/",views.Adminuserlist,name='user_list'),
    path("custom-admin/companylist/", views.Admincompanylist,name="company_list"),
    path('admin/user/delete/<int:user_id>/', views.delete_user, name='delete_user'),
    path("delete-company/<int:company_id>/", views.delete_company, name="delete_company"),
    path('toggle-verification/<int:user_id>/', views.toggle_company_verification, name='toggle_company_verification'),
    path('logout/', views.admin_logout, name='logout'),
]
