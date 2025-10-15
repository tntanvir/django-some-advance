from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


# ✅ Step 1: Custom User Manager
class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user"""
        if not email:
            raise ValueError("The Email field must be set")

        email = self.normalize_email(email)
        extra_fields.setdefault("username", email.split("@")[0])
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser with default premium settings"""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_verified", True)
        extra_fields.setdefault("is_subscribed", True)
        extra_fields.setdefault("subscribed_model", "pro")

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


# ✅ Step 2: Custom User Model
class User(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    fullname = models.CharField(max_length=200, blank=True)
    social_auth_provider = models.CharField(max_length=50, blank=True, null=True)
    is_subscribed = models.BooleanField(default=False)
    subscribed_model = models.CharField(
        choices=[
            ('go', 'go'),
            ('plus', 'Plus'),
            ('pro', 'Pro')
        ],
        max_length=20,
        blank=True,
        null=True
    )
    profile_picture = models.URLField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)

    # Fix for reverse relationship clash
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='authsystem_users',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='authsystem_users_permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    # ✅ Connect the custom manager
    objects = UserManager()

    def __str__(self):
        return self.email
