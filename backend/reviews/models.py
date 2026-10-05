"""Four tables from the team README: users (accounts app), professors, courses, reviews."""
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q


class Professor(models.Model):
    full_name = models.CharField(max_length=200)
    faculty = models.CharField(max_length=100, help_text='Faculty code, for example "SITE"')

    class Meta:
        ordering = ["full_name"]

    def __str__(self):
        return self.full_name


class Course(models.Model):
    code = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=200)

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} {self.title}"


class Review(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE, related_name="reviews")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(max_length=500, blank=True)
    # Every review starts as pending and appears on the site only after an admin approves it
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "professor", "course"], name="one_review_per_user_professor_course"
            ),
            models.CheckConstraint(condition=Q(rating__gte=1, rating__lte=5), name="review_rating_between_1_and_5"),
        ]

    def __str__(self):
        return f"{self.rating}/5 for {self.professor} ({self.course.code}, {self.status})"
