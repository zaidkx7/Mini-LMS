from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import include

urlpatterns = [
    # ===============================
    # Authentication URLs
    # ===============================
    path('login/', views.loginUser, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path('change_password/', views.change_password, name='change_password'),

    # ===============================
    # User Management URLs
    # ===============================
    path('register_student/', views.register_student, name='register_student'),
    path('registered_students/', views.registered_students, name='registered_students'),
    path('delete_student/<int:student_id>/', views.delete_student, name='delete_student'),
    path('delete_staff/<int:staff_id>/', views.delete_staff, name='delete_staff'),
    path('change_role/<int:student_id>/', views.change_role, name='change_role'),
    path('edit_student/<int:student_id>/', views.edit_student, name='edit_student'),
    path('suspend_user/<int:user_id>/', views.suspend_user, name='suspend_user'),

    # ===============================
    # Dashboard URL
    # ===============================
    path('', views.dashboard, name='dashboard'),

    # ===============================
    # Course Management URLs
    # ===============================
    path('add_course/', views.add_course, name='add_course'),
    path('courses/', views.courses, name='courses'),
    path('delete_course/<int:course_id>/', views.delete_course, name='delete_course'),
    path('edit_course/<int:course_id>/', views.edit_course, name='edit_course'),

    # ===============================
    # Quiz Management URLs
    # ===============================
    path('add_quiz/', views.add_quiz, name='add_quiz'),
    path('quizzes/<int:course_id>/', views.quizzes, name='quizzes'),
    path('edit_quiz/<int:quiz_id>/', views.edit_quiz, name='edit_quiz'),
    path('delete_quiz/<int:quiz_id>/', views.delete_quiz, name='delete_quiz'),

    # ===============================
    # Submission Management URLs
    # ===============================
    path('submit_quiz/<int:quiz_id>/', views.submit_quiz, name='submit_quiz'),
    path('view_submissions/<int:course_id>/', views.view_submissions, name='view_submissions'),
    path('view_quiz_submissions/<int:quiz_id>/', views.view_quiz_submissions, name='view_quiz_submissions'),
    path('grade_submission/<int:submission_id>/', views.grade_submission, name='grade_submission'),
    path('remarks/<int:submission_id>/', views.remarks, name='remarks'),
    path('view_remarks/<int:submission_id>/', views.view_remarks, name='view_remarks'),

    # ===============================
    # Complaints Management URLs
    # ===============================
    path('submit_complaint/', views.submit_complaint, name='submit_complaint'),
    path('view_complaints/', views.view_complaints, name='view_complaints'),

    # ===============================
    # Email Settings URL
    # ===============================
    path('email-settings/', views.email_settings, name='email_settings'),

    # ===============================
    # Rankings URL
    # ===============================
    path('view_overall_rank/', views.view_overall_rank, name='view_overall_rank'),

    # ===============================
    # Third Party URLs
    # ===============================
    path("ckeditor5/", include('django_ckeditor_5.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)