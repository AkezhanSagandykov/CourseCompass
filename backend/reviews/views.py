from django.db import IntegrityError
from django.db.models import Avg, Count, F, Q
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .models import Course, Professor, Review
from .serializers import (
    CourseSerializer,
    ProfessorDetailSerializer,
    ProfessorSerializer,
    ReviewCreateSerializer,
    ReviewSerializer,
)

APPROVED = Q(reviews__status=Review.Status.APPROVED)
ORDERINGS = {
    "rating": F("average_rating").desc(nulls_last=True),
    "reviews": F("review_count").desc(),
    "name": F("full_name").asc(),
}


class ProfessorViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/professors/?search=&faculty=&ordering=rating|reviews|name
    GET /api/professors/<id>/
    GET /api/professors/<id>/reviews/
    GET /api/professors/faculties/
    """

    def get_queryset(self):
        queryset = Professor.objects.annotate(
            average_rating=Avg("reviews__rating", filter=APPROVED),
            review_count=Count("reviews", filter=APPROVED),
        )
        params = self.request.query_params
        if search := params.get("search", "").strip():
            queryset = queryset.filter(full_name__icontains=search)
        if faculty := params.get("faculty", "").strip():
            queryset = queryset.filter(faculty__iexact=faculty)
        return queryset.order_by(ORDERINGS.get(params.get("ordering"), ORDERINGS["name"]))

    def get_serializer_class(self):
        return ProfessorDetailSerializer if self.action == "retrieve" else ProfessorSerializer

    @action(detail=True)
    def reviews(self, request, pk=None):
        professor = self.get_object()
        queryset = professor.reviews.filter(status=Review.Status.APPROVED).select_related("course")
        page = self.paginate_queryset(queryset)
        return self.get_paginated_response(ReviewSerializer(page, many=True).data)

    @action(detail=False, pagination_class=None)
    def faculties(self, request):
        codes = Professor.objects.order_by("faculty").values_list("faculty", flat=True).distinct()
        return Response(list(codes))


class CourseListView(generics.ListAPIView):
    """GET /api/courses/ — all courses, for the review form."""

    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = None


class ReviewCreateView(generics.CreateAPIView):
    """POST /api/reviews/ — the review starts as pending until an admin approves it."""

    serializer_class = ReviewCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        try:
            serializer.save(user=self.request.user, status=Review.Status.PENDING)
        except IntegrityError:  # two identical requests at the same moment
            raise ValidationError({"non_field_errors": ["You have already reviewed this professor for this course."]})

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        response.data["detail"] = "Thanks! Your review will appear after a moderator approves it."
        return response
