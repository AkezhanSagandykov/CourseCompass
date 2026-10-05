"""Email verification with signed tokens: no extra database table is needed."""
from django.conf import settings
from django.core import signing
from django.core.mail import send_mail

SALT = "coursecompass-email-verification"


def make_token(user):
    return signing.dumps({"user_id": user.pk}, salt=SALT)


def read_token(token):
    """Returns the user id, or None if the token is invalid or expired."""
    try:
        data = signing.loads(token, salt=SALT, max_age=settings.EMAIL_VERIFICATION_MAX_AGE)
    except signing.BadSignature:  # also covers SignatureExpired
        return None
    return data.get("user_id")


def send_verification_email(user):
    link = f"{settings.FRONTEND_URL}/verify?token={make_token(user)}"
    send_mail(
        subject="Confirm your CourseCompass account",
        message=(
            "Hi!\n\nOpen this link to confirm your KBTU email and start rating courses:\n"
            f"{link}\n\nThe link works for 48 hours. If you did not sign up, ignore this email."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
    )
