from rest_framework import serializers

from .models import Course, Professor, Review


def rounded(value):
    return round(value, 1) if value is not None else None


class ProfessorSerializer(serializers.ModelSerializer):
    """List item: average rating and count use approved reviews only."""

    average_rating = serializers.SerializerMethodField()
    review_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Professor
        fields = ["id", "full_name", "faculty", "average_rating", "review_count"]

    def get_average_rating(self, obj):
        return rounded(getattr(obj, "average_rating", None))


class ProfessorDetailSerializer(ProfessorSerializer):
    """One professor: adds how many approved reviews gave 1, 2, 3, 4 and 5."""

    rating_distribution = serializers.SerializerMethodField()

    class Meta(ProfessorSerializer.Meta):
        fields = ProfessorSerializer.Meta.fields + ["rating_distribution"]

    def get_rating_distribution(self, obj):
        counts = {str(stars): 0 for stars in range(1, 6)}
        for rating in obj.reviews.filter(status=Review.Status.APPROVED).values_list("rating", flat=True):
            counts[str(rating)] += 1
        return counts


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ["id", "code", "title"]


class ReviewSerializer(serializers.ModelSerializer):
    """Public review: the author is never returned, reviews are anonymous."""

    course = CourseSerializer()

    class Meta:
        model = Review
        fields = ["id", "course", "rating", "comment", "created_at"]


class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["id", "professor", "course", "rating", "comment", "status"]
        read_only_fields = ["id", "status"]
        validators = []  # the one-review rule is checked below with a clear message

    def validate(self, attrs):
        user = self.context["request"].user
        if Review.objects.filter(user=user, professor=attrs["professor"], course=attrs["course"]).exists():
            raise serializers.ValidationError(
                {"non_field_errors": ["You have already reviewed this professor for this course."]}
            )
        return attrs
