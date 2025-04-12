from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Note, Unit, Course


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(max_length=30, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    widget = MultipleFileInput()

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        clean_single_file = super().clean
        if isinstance(data, (list, tuple)):
            return [clean_single_file(d, initial) for d in data]
        return clean_single_file(data, initial)


class NoteForm(forms.ModelForm):
    file = MultipleFileField()

    class Meta:
        model = Note
        fields = "__all__"
        # Optional: uncomment if you want to exclude specific fields
        # exclude = ['department', 'unit_topic']


class UnitForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = [
            "name",
            "course",
            "year_of_study",
            "sem",
        ]  # Adjusted based on the current model

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "course" in self.data:
            try:
                course_id = int(self.data.get("course"))
                self.fields["course"].queryset = Course.objects.filter(id=course_id)
            except (ValueError, TypeError):
                self.fields["course"].queryset = Course.objects.none()
        elif self.instance.pk:
            self.fields["course"].queryset = Course.objects.filter(
                id=self.instance.course_id
            )
