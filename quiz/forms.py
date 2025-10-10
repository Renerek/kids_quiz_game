from django import forms
from django.contrib.auth.models import User
from django.utils import timezone

from .models import Assignment

class CustomPasswordResetRequestForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=254, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your email address',
        'required': 'required',
    }))

class CustomSetPasswordForm(forms.Form):
    new_password1 = forms.CharField(
        label="New password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'New password', 'required': 'required'})
    )
    new_password2 = forms.CharField(
        label="Confirm new password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm new password', 'required': 'required'})
    )

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("new_password1")
        password2 = cleaned_data.get("new_password2")
        if password1 and password2 and password1 != password2:
            self.add_error('new_password2', "Passwords do not match.")
        return cleaned_data


class AddChildForm(forms.Form):
    child_identifier = forms.CharField(
        label="Child Username or Email",
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter child username or email'})
    )

    def clean_child_identifier(self):
        identifier = self.cleaned_data['child_identifier'].strip()
        try:
            user = User.objects.get(username__iexact=identifier)
        except User.DoesNotExist:
            try:
                user = User.objects.get(email__iexact=identifier)
            except User.DoesNotExist as exc:
                raise forms.ValidationError("No user found with that username or email.") from exc
        if not hasattr(user, 'profile'):
            raise forms.ValidationError("This user does not have a learner profile configured yet.")
        return user


class AssignmentForm(forms.ModelForm):
    due_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        label="Due Date & Time",
    )

    class Meta:
        model = Assignment
        fields = ['assigned_to', 'game', 'due_date', 'notes']
        widgets = {
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'game': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional instructions or encouragement'}),
        }

    def __init__(self, *args, **kwargs):
        children_queryset = kwargs.pop('children_queryset', User.objects.none())
        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].queryset = children_queryset

    def clean_due_date(self):
        due_date = self.cleaned_data['due_date']
        if timezone.is_naive(due_date):
            due_date = timezone.make_aware(due_date, timezone.get_current_timezone())
        if due_date <= timezone.now():
            raise forms.ValidationError("Due date must be in the future.")
        return due_date


class ParentGateForm(forms.Form):
    age = forms.IntegerField(
        label="Confirm Your Age",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter your age'}),
        error_messages={'required': "Please enter your age."},
    )
    birth_year = forms.IntegerField(
        label="Year of Birth",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter your birth year'}),
        error_messages={'required': "Please enter your year of birth."},
    )

    def clean(self):
        cleaned_data = super().clean()
        age = cleaned_data.get("age")
        birth_year = cleaned_data.get("birth_year")

        if age is None or birth_year is None:
            return cleaned_data

        current_year = timezone.now().year

        if birth_year > current_year or birth_year < current_year - 120:
            self.add_error("birth_year", "Enter a valid birth year.")
            return cleaned_data

        if age <= 0:
            self.add_error("age", "Enter a valid age.")
            return cleaned_data

        calculated_age = current_year - birth_year
        if age not in {calculated_age, calculated_age - 1}:
            message = "Age must match the birth year provided."
            self.add_error("age", message)
            self.add_error("birth_year", message)

        if age < 18:
            self.add_error("age", "Only adults 18 or older can use the parent dashboard.")

        return cleaned_data
