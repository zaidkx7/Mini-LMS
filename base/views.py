from django.shortcuts import render
from .forms import RemarksForm, QuizAddingForm, StudentComplaintsForm
from .models import Quiz, Submission, Courses, User, StudentProfile, StudentComplaints
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.hashers import check_password
from django.shortcuts import render
from django.db.models import Sum, Count, Q
import httpagentparser

# ===============================
# Authentication Views
# ===============================

def loginUser(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        reg_no = request.POST.get('reg_no')
        password = request.POST.get('password')
        if not reg_no or not password:
            messages.error(request, 'Please enter both registration number and password')
            return redirect('login')
        user = authenticate(request, username=reg_no, password=password)
        if user is not None:
            if user.studentprofile.active_status:  
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, 'Account Suspended. Contact the Administrator.')
                return redirect('login')
        else:
            messages.error(request, 'Registration number or Password is incorrect')
    return render(request, 'base/login.html')

def logoutUser(request):
    logout(request)
    return redirect('login')

@login_required
def change_password(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        if not old_password or not new_password:
            messages.error(request, 'Please enter both old and new passwords')
            return redirect('change_password')
        confirm_password = request.POST.get('confirm_password')
        if not check_password(old_password, request.user.password):
            messages.error(request, 'Old password is incorrect')
            return redirect('change_password')
        if new_password != confirm_password:
            messages.error(request, 'New password and confirm password do not match')
            return redirect('change_password')
        user = request.user
        user.set_password(new_password)
        user.save()
        update_session_auth_hash(request, user)
        messages.success(request, 'Your password has been successfully updated!')
        return redirect('dashboard')
    return render(request, 'base/change_password.html')

# ===============================
# User Management Views
# ===============================

@staff_member_required(login_url='dashboard')
def register_student(request):
    if request.method == 'POST':
        reg_no = request.POST.get('reg_no')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        gender = request.POST.get('gender')
        if not reg_no or not password or not first_name or not last_name or not gender:
            messages.error(request, 'Please fill in all fields')
            return redirect('register_student')
        user = User.objects.create_user(username=reg_no, password=password, first_name=first_name, last_name=last_name)
        student_profile = StudentProfile.objects.create(user=user, gender=gender)
        messages.success(request, 'Student registered successfully')
        return redirect('dashboard')
    return render(request, 'base/register_student.html')

@staff_member_required(login_url='dashboard')
def registered_students(request):
    students = User.objects.filter(is_staff=False)
    staff = User.objects.filter(is_staff=True, is_superuser=False)
    super_users = User.objects.filter(is_superuser=True)
    return render(request, 'base/registered_students.html', {'students': students, 'staff': staff, 'super_users': super_users})

@staff_member_required(login_url='dashboard')
def edit_student(request, student_id):
    student = get_object_or_404(User, id=student_id)
    profile = get_object_or_404(StudentProfile, user=student)
    if request.method == 'POST':
        student.first_name = request.POST.get('first_name')
        student.last_name = request.POST.get('last_name')
        profile.gender = request.POST.get('gender')
        student.save()
        profile.save()
        messages.success(request, 'Student updated successfully')
        return redirect('registered_students')
    return render(request, 'base/edit_student.html', {'student': student, 'profile': profile})

@staff_member_required(login_url='dashboard')
def delete_student(request, student_id):
    student = get_object_or_404(User, id=student_id)
    if request.method == 'POST':
        student.delete()
        messages.success(request, 'Student deleted successfully')
        return redirect('registered_students')
    return render(request, 'base/delete_student.html', {'student': student})

@staff_member_required(login_url='dashboard')
def delete_staff(request, staff_id):
    staff = get_object_or_404(User, id=staff_id)
    if request.method == 'POST':
        staff.delete()
        messages.success(request, 'Staff deleted successfully')
        return redirect('registered_students')
    return render(request, 'base/delete_staff.html', {'staff': staff})

@staff_member_required(login_url='dashboard')
def change_role(request, student_id):
    student = get_object_or_404(User, id=student_id)
    if request.method == 'POST':
        role = request.POST.get('role')
        if not role:
            messages.error(request, 'Please select a role')
            return redirect('change_role', student_id)
        if role == 'student':
            student.is_staff = False
            student.is_superuser = False
        elif role == 'staff':
            student.is_staff = True
            student.is_superuser = False
        elif role == 'super_user':
            student.is_superuser = True
        student.save()
        messages.success(request, 'Role changed successfully')
        return redirect('registered_students')
    return render(request, 'base/change_role.html', {'student': student})

@staff_member_required(login_url='dashboard')
def suspend_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user_profile = get_object_or_404(StudentProfile, user=user)
    if user_profile.active_status:
        user_profile.active_status = False
        messages.success(request, 'User suspended successfully')
    else:
        user_profile.active_status = True
        messages.success(request, 'User activated successfully')
    user_profile.save()
    return redirect('registered_students')

# ===============================
# Dashboard Views
# ===============================

@login_required(login_url='login')
def dashboard(request):
    courses = Courses.objects.all()
    quizzes = Quiz.objects.all()
    submissions = Submission.objects.filter(student=request.user)
    submission_counts = {course.id: submissions.filter(course=course).count() for course in courses}
    marks_sums = {
    course.id: submissions.filter(course=course, marks__isnull=False).aggregate(Sum('marks'))['marks__sum'] or 0
        for course in courses
    }
    # Calculate totals for dashboard cards
    total_submissions = sum(submission_counts.values())
    total_marks = sum(marks_sums.values())

    user_agent = request.META.get('HTTP_USER_AGENT')
    user_ip = request.META.get('REMOTE_ADDR')
    device_info = httpagentparser.detect(user_agent)
    device_type = device_info.get("platform", {}).get("name", "Unknown Device")
    return render(request, 'base/dashboard.html', {'courses': courses, 'quizzes': quizzes, 'submissions': submissions, 'submission_counts': submission_counts, 'marks_sums': marks_sums, 'total_submissions': total_submissions, 'total_marks': total_marks, 'user_agent': user_agent, 'user_ip': user_ip, 'device_type': device_type})

# ===============================
# Course Management Views
# ===============================

@login_required(login_url='login')
def courses(request):
    courses = Courses.objects.all()
    return render(request, 'base/courses.html', {'courses': courses})

@staff_member_required(login_url='dashboard')
def add_course(request):
    if request.method == 'POST':
        course_title = request.POST.get('course_title')
        course_no = request.POST.get('course_no')
        if not course_title or not course_no:
            messages.error(request, 'Please fill in all fields')
            return redirect('add_course')
        Courses.objects.create(course_title=course_title, course_no=course_no)
        messages.success(request, 'Course added successfully')
        return redirect('courses')
    return render(request, 'base/add_course.html')

@staff_member_required(login_url='dashboard')
def edit_course(request, course_id):
    course = get_object_or_404(Courses, id=course_id)
    if request.method == 'POST':
        course.course_title = request.POST.get('course_title')
        course.course_no = request.POST.get('course_no')
        if not course.course_title or not course.course_no:
            messages.error(request, 'Please fill in all fields')
            return redirect('edit_course', course_id)
        course.save()
        messages.success(request, 'Course updated successfully')
        return redirect('courses')
    return render(request, 'base/edit_course.html', {'course': course})

@staff_member_required(login_url='dashboard')
def delete_course(request, course_id):
    course = get_object_or_404(Courses, id=course_id)
    if request.method == 'POST':
        course.delete()
        messages.success(request, 'Course deleted successfully')
        return redirect('courses')
    return render(request, 'base/delete_course.html', {'course': course})

# ===============================
# Quiz Management Views
# ===============================

@login_required(login_url='login')
def quizzes(request, course_id):
    course = get_object_or_404(Courses, id=course_id)
    quizzes = Quiz.objects.filter(course=course)
    submissions = Submission.objects.filter(student=request.user)
    submitted_quizzes = submissions.values_list('quiz_id', flat=True)
    now = timezone.now()
    return render(request, 'base/quizzes.html', {'quizzes': quizzes, 'course': course, 'submissions': submissions, 'submitted_quizzes': submitted_quizzes, 'now': now})

@staff_member_required(login_url='dashboard')
def add_quiz(request):
    courses = Courses.objects.all()
    form = QuizAddingForm()
    if request.method == 'POST':
        form = QuizAddingForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Quiz added successfully')
            return redirect('quizzes', form.cleaned_data['course'].id)
    return render(request, 'base/add_quiz.html', {'courses': None, 'form': form})

@staff_member_required(login_url='dashboard')
def edit_quiz(request, quiz_id):
    courses = Courses.objects.all()
    quiz = get_object_or_404(Quiz, id=quiz_id)
    form = QuizAddingForm(instance=quiz)
    if request.method == 'POST':
        form = QuizAddingForm(request.POST, request.FILES, instance=quiz)
        if form.is_valid():
            form.save()
            messages.success(request, 'Quiz updated successfully')
            return redirect('quizzes', form.cleaned_data['course'].id)
    return render(request, 'base/edit_quiz.html', {'quiz': quiz, 'courses': courses, 'form': form})

@staff_member_required(login_url='dashboard')
def delete_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if request.method == 'POST':
        quiz.delete()
        messages.success(request, 'Quiz deleted successfully')
        return redirect('quizzes', quiz.course.id)
    return render(request, 'base/delete_quiz.html', {'quiz': quiz})

# ===============================
# Submission Management Views
# ===============================

@login_required(login_url='login')
def submit_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    student = request.user
    if quiz.due_date <= timezone.now():
        messages.error(request, 'Quiz submission deadline has passed')
        return redirect('quizzes', quiz.course.id)
    if request.method == 'POST':
        file = request.FILES.get('file')
        extention = str(file.name).split('.')[-1]
        if file and extention.lower() in ['pdf', 'doc', 'docx', 'zip', 'txt', 'cpp', 'py']:
            if Submission.objects.filter(student=student, quiz=quiz).exists():
                # replace the file with the new one
                submission = Submission.objects.get(student=student, quiz=quiz)
                submission.file = file
                submission.save()
            else:
                Submission.objects.create(student=student, course=quiz.course, quiz=quiz, file=file)
            messages.success(request, 'Quiz submitted successfully')
            return redirect('quizzes', quiz.course.id)
        else:
            messages.error(request, 'Invalid file type. Please upload a PDF, DOC, DOCX, ZIP, or TXT file.')
            return redirect('submit_quiz', quiz.id)
    return render(request, 'base/submit_quiz.html', {'quiz': quiz})

@staff_member_required(login_url='dashboard')
def view_submissions(request, course_id):
    course = get_object_or_404(Courses, id=course_id)
    submissions = Submission.objects.filter(course=course)
    return render(request, 'base/submissions.html', {'submissions': submissions})

@login_required(login_url='login')
def view_quiz_submissions(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if request.user.is_staff or request.user.is_superuser or quiz.due_date <= timezone.now():
        users = User.objects.all()
        for user in users:
            submission = Submission.objects.filter(student=user, quiz=quiz).first()
            user.submission = submission
        return render(request, 'base/quiz_submissions.html', {'quiz': quiz, 'users': users})
    else:
        return redirect('quizzes', quiz.course.id)

@staff_member_required(login_url='dashboard')
def grade_submission(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id)
    if request.method == 'POST':
        marks = request.POST.get('marks')
        if int(marks) < 0 or int(marks) > 10:
            messages.error(request, 'Invalid marks. Please assign marks between 0 and 10.')
            return redirect('grade_submission', submission_id)
        else:
            submission.marks = int(marks)
            submission.save()
            messages.success(request, f'Marks assigned: {marks} to {submission.student.username}')
        return redirect('view_quiz_submissions', quiz_id=submission.quiz.id)
    return render(request, 'base/grade_submission.html', {'submission': submission})

@staff_member_required(login_url='dashboard')
def remarks(request, submission_id):
    form = RemarksForm()
    submission = get_object_or_404(Submission, id=submission_id)
    if request.method == 'POST':
        form = RemarksForm(request.POST)
        if form.is_valid():
            submission.remarks = form.cleaned_data['remarks']
            submission.save()
            messages.success(request, 'Remarks added successfully')
            return redirect('view_quiz_submissions', submission.quiz.id)
    return render(request, 'base/remarks.html', {'submission': submission, 'form': form})

@login_required(login_url='login')
def view_remarks(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id)
    return render(request, 'base/view_remarks.html', {'submission': submission})

# ===============================
# Complaints Management Views
# ===============================

@login_required
def submit_complaint(request):
    if request.method == "POST":
        form = StudentComplaintsForm(request.POST)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.student = request.user
            complaint.save()
            messages.success(request, "Complaint submitted successfully.")
            return redirect('dashboard')
        else:
            print("Form is not valid")
            print(form.errors.as_text)
    else:
        form = StudentComplaintsForm()
    return render(request, 'base/submit_complaint.html', {'form': form})

@staff_member_required(login_url='dashboard')
def view_complaints(request):
    complaints = StudentComplaints.objects.all()
    return render(request, 'base/view_complaints.html', {'complaints': complaints})

# ===============================
# Rankings Views
# ===============================

@login_required(login_url='login')
def view_overall_rank(request):
    total_possible_marks = Quiz.objects.count() * 10
    user_marks = User.objects.annotate(
        total_marks=Sum('submission__marks', filter=Q(submission__marks__isnull=False)),
        num_submissions=Count('submission', filter=Q(submission__marks__isnull=False))
    ).order_by('-total_marks')
    rankings = [{
        'student__username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'total_marks': user.total_marks or 0,
        'total_possible_marks': total_possible_marks,
        'student__id': user.id
    } for user in user_marks]
    
    for idx, user in enumerate(rankings):
        user['rank'] = idx + 1
    current_user_rank = next((item for item in rankings if item['student__id'] == request.user.id), None)
    return render(request, 'base/overall_rank.html', {'rankings': rankings, 'current_user_rank': current_user_rank})