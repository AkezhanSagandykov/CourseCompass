from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from .admin import ReviewAdmin
from .models import Course, Professor, Review

User = get_user_model()


class ReviewApiTests(APITestCase):
    def setUp(self):
        self.professor = Professor.objects.create(full_name="Test Professor", faculty="SITE")
        self.other_professor = Professor.objects.create(full_name="Another Lecturer", faculty="BS")
        self.course = Course.objects.create(code="CSCI2208", title="Software Engineering")
        self.other_course = Course.objects.create(code="INFT3108", title="IT Project Management")
        self.student = User.objects.create_user(email="student@kbtu.kz", password="Str0ng-pass-123", is_active=True)

    def post_review(self, **overrides):
        payload = {"professor": self.professor.id, "course": self.course.id, "rating": 5, "comment": "Clear lectures."}
        payload.update(overrides)
        self.client.force_authenticate(self.student)
        return self.client.post("/api/reviews/", payload, format="json")

    def approve_all(self):
        Review.objects.update(status=Review.Status.APPROVED)

    def test_anonymous_user_cannot_post_review(self):
        response = self.client.post(
            "/api/reviews/", {"professor": self.professor.id, "course": self.course.id, "rating": 5}, format="json"
        )
        self.assertEqual(response.status_code, 401)

    def test_new_review_starts_as_pending_and_is_hidden(self):
        response = self.post_review()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["status"], Review.Status.PENDING)

        reviews = self.client.get(f"/api/professors/{self.professor.id}/reviews/")
        self.assertEqual(reviews.data["count"], 0)

    def test_approved_review_is_shown_and_counted(self):
        self.post_review(rating=4)
        self.approve_all()

        reviews = self.client.get(f"/api/professors/{self.professor.id}/reviews/")
        self.assertEqual(reviews.data["count"], 1)
        self.assertNotIn("user", reviews.data["results"][0])  # anonymous

        detail = self.client.get(f"/api/professors/{self.professor.id}/")
        self.assertEqual(detail.data["average_rating"], 4.0)
        self.assertEqual(detail.data["review_count"], 1)
        self.assertEqual(detail.data["rating_distribution"]["4"], 1)

    def test_pending_reviews_do_not_change_the_average(self):
        self.post_review(rating=1)
        response = self.client.get(f"/api/professors/{self.professor.id}/")
        self.assertIsNone(response.data["average_rating"])
        self.assertEqual(response.data["review_count"], 0)

    def test_rating_must_be_between_1_and_5(self):
        self.assertEqual(self.post_review(rating=0).status_code, 400)
        self.assertEqual(self.post_review(rating=6).status_code, 400)
        self.assertFalse(Review.objects.exists())

    def test_comment_is_limited_to_500_characters(self):
        self.assertEqual(self.post_review(comment="a" * 501).status_code, 400)

    def test_one_review_per_user_per_professor_per_course(self):
        self.assertEqual(self.post_review().status_code, 201)
        self.assertEqual(self.post_review(comment="Again").status_code, 400)
        # Same professor, different course is allowed
        self.assertEqual(self.post_review(course=self.other_course.id).status_code, 201)
        self.assertEqual(Review.objects.count(), 2)

    def test_search_and_faculty_filter(self):
        self.assertEqual(self.client.get("/api/professors/", {"search": "test"}).data["count"], 1)
        self.assertEqual(self.client.get("/api/professors/", {"faculty": "bs"}).data["count"], 1)
        self.assertEqual(self.client.get("/api/professors/faculties/").data, ["BS", "SITE"])

    def test_courses_list(self):
        response = self.client.get("/api/courses/")
        self.assertEqual([course["code"] for course in response.data], ["CSCI2208", "INFT3108"])

    def test_admin_approve_action(self):
        self.post_review()
        admin = ReviewAdmin(Review, AdminSite())
        admin.message_user = lambda *args, **kwargs: None
        admin.approve(request=None, queryset=Review.objects.all())
        self.assertEqual(Review.objects.get().status, Review.Status.APPROVED)
