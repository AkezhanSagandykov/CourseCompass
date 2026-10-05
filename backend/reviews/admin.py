from django.contrib import admin

from .models import Course, Professor, Review


@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = ["full_name", "faculty"]
    list_filter = ["faculty"]
    search_fields = ["full_name"]


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ["code", "title"]
    search_fields = ["code", "title"]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Moderation happens here: filter by Pending, select reviews, run Approve or Reject."""

    list_display = ["id", "professor", "course", "rating", "short_comment", "status", "created_at"]
    list_filter = ["status", "rating"]
    search_fields = ["comment", "professor__full_name", "course__code"]
    actions = ["approve", "reject"]

    @admin.display(description="Comment")
    def short_comment(self, obj):
        return obj.comment[:60] + ("…" if len(obj.comment) > 60 else "")

    @admin.action(description="Approve selected reviews")
    def approve(self, request, queryset):
        updated = queryset.update(status=Review.Status.APPROVED)
        self.message_user(request, f"Approved {updated} review(s).")

    @admin.action(description="Reject selected reviews")
    def reject(self, request, queryset):
        updated = queryset.update(status=Review.Status.REJECTED)
        self.message_user(request, f"Rejected {updated} review(s).")
