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
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        if isinstance(data, (list, tuple)):
            return [super().clean(d, initial) for d in data]
        return super().clean(data, initial)


class NoteForm(forms.ModelForm):
    file = MultipleFileField()

    class Meta:
        model = Note
        fields = "__all__"


class UnitForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = ["name", "course", "year_of_study", "sem"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        course_field = self.fields.get("course")
        course_id = self.data.get("course")

        if course_id:
            try:
                course_field.queryset = Course.objects.filter(id=int(course_id))
            except (ValueError, TypeError):
                course_field.queryset = Course.objects.none()
        elif self.instance.pk:
            course_field.queryset = Course.objects.filter(id=self.instance.course_id)
