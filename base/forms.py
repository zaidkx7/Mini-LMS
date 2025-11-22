from django import forms
from django_ckeditor_5.widgets import CKEditor5Widget
from .models import Quiz, Submission, StudentComplaints, EmailSettings


class QuizAddingForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['quiz_title'].required = True
        self.fields['quiz_no'].required = True
        self.fields['description'].required = True
        self.fields['due_date'].required = True
        self.fields['course'].required = True


        for field_name in self.fields:
            self.fields[field_name].help_text = ''

    class Meta:
        model = Quiz
        fields = "__all__"
        widgets = {
            "quiz_title": forms.TextInput(attrs={"class": "block w-full rounded-md border border-gray-300 py-2.5 px-3 text-gray-900 placeholder-gray-400 focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-600/20 sm:text-sm"}),
            "quiz_no": forms.TextInput(attrs={"class": "block w-full rounded-md border border-gray-300 py-2.5 px-3 text-gray-900 placeholder-gray-400 font-mono focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-600/20 sm:text-sm"}),
            "description": CKEditor5Widget(attrs={"class": "django_ckeditor_5", "config_name": "extends"}),
            "help_file": forms.FileInput(attrs={"class": "block w-full text-sm text-gray-900 border border-gray-300 rounded-md cursor-pointer bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-600/20 focus:border-blue-600 file:mr-4 file:py-2 file:px-4 file:rounded-l-md file:border-0 file:text-sm file:font-medium file:bg-gray-900 file:text-white hover:file:bg-gray-800"}),
            "due_date": forms.DateTimeInput(attrs={"class": "block w-full rounded-md border border-gray-300 py-2.5 px-3 text-gray-900 placeholder-gray-400 focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-600/20 sm:text-sm", "type": "datetime-local"}),
            "course": forms.Select(attrs={"class": "block w-full rounded-md border border-gray-300 py-2.5 px-3 text-gray-900 focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-600/20 sm:text-sm"}),
        }
        labels = {
            "quiz_title": "Quiz Title",
            "quiz_no": "Quiz Number",
            "description": "Quiz Description",
            "help_file": "Help File (Optional)",
            "due_date": "Due Date & Time",
            "course": "Course",
        }

class RemarksForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ["remarks"]
        widgets = {
            "remarks": CKEditor5Widget(attrs={"class": "django_ckeditor_5 block w-full rounded-md border border-gray-300", "config_name": "extends"})
        }
        labels = {
            "remarks": "Feedback & Remarks"
        }
    
class StudentComplaintsForm(forms.ModelForm):
    class Meta:
        model = StudentComplaints
        fields = ["complaint"]
        widgets = {
            "complaint": CKEditor5Widget(attrs={"class": "django_ckeditor_5", "config_name": "extends"})
        }
        labels = {
            "complaint": "Complaint"
        }

class EmailSettingsForm(forms.ModelForm):
    class Meta:
        model = EmailSettings
        fields = ["enable_quiz_upload_notifications", "enable_submission_notifications"]
        widgets = {
            "enable_quiz_upload_notifications": forms.CheckboxInput(attrs={"class": "h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-600"}),
            "enable_submission_notifications": forms.CheckboxInput(attrs={"class": "h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-600"}),
        }
        labels = {
            "enable_quiz_upload_notifications": "Send email when a quiz is uploaded",
            "enable_submission_notifications": "Send email when a quiz is submitted",
        }