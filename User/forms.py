from typing import Sequence, Type
from django import forms
from .models import User


class AdminForm(forms.ModelForm):
    class Meta:
        model: Type[User] = User
        fields: Sequence[str] = (
            'email',
            'name',
            'firstname',
            'is_active',
            'is_superuser',
            'is_staff',
            'user_permissions',
        )

    def save(self, commit: bool = True) -> User:
        user: User = super().save(commit=False)
        user.set_password(self.cleaned_data.get('password1'))
        if commit:
            user.save()
        return user


class SignUpForm(AdminForm):
    class Meta:
        model: Type[User] = User
        fields: Sequence[str] = ('email', 'firstname')
