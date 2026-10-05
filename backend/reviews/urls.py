from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import CourseListView, ProfessorViewSet, ReviewCreateView

router = DefaultRouter()
router.register("professors", ProfessorViewSet, basename="professor")

urlpatterns = [
    path("courses/", CourseListView.as_view(), name="course-list"),
    path("reviews/", ReviewCreateView.as_view(), name="review-create"),
    *router.urls,
]
