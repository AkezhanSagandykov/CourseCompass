"""Optional demo data: 30 professors from 3 faculties, 11 courses, demo users and sample reviews.

All names and reviews here are FICTIONAL. Replace them with real data before a pilot.
Run: python manage.py seed_demo
"""
import random

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from reviews.models import Course, Professor, Review

User = get_user_model()

COURSES = [
    ("INFT3108", "IT Project Management"),
    ("INFT3107", "Fundamentals of Information Systems"),
    ("INFT4245", "Application Development in Go"),
    ("CSCI2208", "Software Engineering"),
    ("CSCI2105", "Data Structures and Algorithms"),
    ("MGMT2101", "Principles of Management"),
    ("FIN2201", "Corporate Finance"),
    ("MKT2301", "Marketing"),
    ("MATH1101", "Calculus I"),
    ("MATH2201", "Linear Algebra"),
    ("STAT2301", "Probability and Statistics"),
]
PROFESSORS_PER_FACULTY = {"SITE": 12, "BS": 9, "SAM": 9}  # 30 in total

MALE_FIRST = ["Daniyar", "Nurlan", "Yerlan", "Timur", "Arman", "Bauyrzhan", "Sanzhar", "Ruslan"]
FEMALE_FIRST = ["Aigerim", "Madina", "Zhanna", "Dana", "Saule", "Aruzhan", "Kamila", "Assel"]
SURNAMES = ["Akhmetov", "Bekov", "Zhumabayev", "Sarsenov", "Omarov", "Nurpeisov", "Kassymov", "Tulegenov"]

SAMPLE_COMMENTS = [
    "Clear lectures and weekly quizzes keep you on track.",
    "Heavy workload before the midterm, but the grading is fair.",
    "Practical tasks are close to real work. Start the project early.",
    "Slides are enough for the exam if you attend every class.",
    "Hard at first, but answers questions patiently.",
    "",
]


class Command(BaseCommand):
    help = "Fill the database with fictional demo data for CourseCompass."

    @transaction.atomic
    def handle(self, *args, **options):
        rng = random.Random(42)  # same data on every run

        names = [f"{first} {last}" for first in MALE_FIRST for last in SURNAMES]
        names += [f"{first} {last}a" for first in FEMALE_FIRST for last in SURNAMES]  # Akhmetov -> Akhmetova
        rng.shuffle(names)
        name_iter = iter(names)

        professors = []
        for faculty, count in PROFESSORS_PER_FACULTY.items():
            for _ in range(count):
                professor, _ = Professor.objects.get_or_create(full_name=next(name_iter), faculty=faculty)
                professors.append(professor)

        courses = [Course.objects.get_or_create(code=code, defaults={"title": title})[0] for code, title in COURSES]

        moderator, created = User.objects.get_or_create(
            email="moderator@kbtu.kz", defaults={"is_staff": True, "is_superuser": True, "is_active": True}
        )
        if created:
            moderator.set_password("moderator-demo-2026")
            moderator.save()

        students = []
        for number in range(1, 6):
            student, created = User.objects.get_or_create(email=f"student{number}@kbtu.kz", defaults={"is_active": True})
            if created:
                student.set_password("student-demo-2026")
                student.save()
            students.append(student)

        created_reviews = 0
        for student in students:
            for professor in rng.sample(professors, k=8):
                course = rng.choice(courses)
                _, was_created = Review.objects.get_or_create(
                    user=student,
                    professor=professor,
                    course=course,
                    defaults={
                        "rating": rng.choice([2, 3, 4, 4, 5, 5]),
                        "comment": rng.choice(SAMPLE_COMMENTS),
                        # most demo reviews are approved; a few stay pending to show moderation in /admin/
                        "status": Review.Status.PENDING if rng.random() < 0.15 else Review.Status.APPROVED,
                    },
                )
                created_reviews += was_created

        self.stdout.write(self.style.SUCCESS(
            f"Demo data ready: {Professor.objects.count()} professors, {Course.objects.count()} courses, "
            f"{created_reviews} new reviews."
        ))
        self.stdout.write("Admin / moderator: moderator@kbtu.kz / moderator-demo-2026")
        self.stdout.write("Students: student1@kbtu.kz ... student5@kbtu.kz / student-demo-2026")
