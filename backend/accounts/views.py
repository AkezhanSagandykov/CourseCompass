from django.contrib.auth import get_user_model
from rest_framework import permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import LoginSerializer, RegisterSerializer, UserSerializer
from .verification import read_token, send_verification_email

User = get_user_model()


class RegisterView(APIView):
    """POST /api/auth/register/ — sign up with a KBTU email; sends a verification link."""

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        send_verification_email(user)
        return Response(
            {"detail": "Check your KBTU email and open the link to activate your account."},
            status=status.HTTP_201_CREATED,
        )


class VerifyEmailView(APIView):
    """GET /api/auth/verify/?token=... — activates the account."""

    def get(self, request):
        user_id = read_token(request.query_params.get("token", ""))
        if user_id is None:
            return Response(
                {"detail": "This link is invalid or has expired. Sign up again to get a new one."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = User.objects.filter(pk=user_id).first()
        if user is None:
            return Response({"detail": "Account not found."}, status=status.HTTP_404_NOT_FOUND)
        if not user.is_active:
            user.is_active = True
            user.save(update_fields=["is_active"])
        return Response({"detail": "Email confirmed. You can log in now."})


class LoginView(APIView):
    """POST /api/auth/login/ — returns an API token for the React app."""

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"].lower()
        user = User.objects.filter(email=email).first()

        if user is None or not user.check_password(serializer.validated_data["password"]):
            return Response({"detail": "Wrong email or password."}, status=status.HTTP_400_BAD_REQUEST)
        if not user.is_active:
            return Response(
                {"detail": "Confirm your email first: open the link we sent to your KBTU inbox."},
                status=status.HTTP_403_FORBIDDEN,
            )

        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "user": UserSerializer(user).data})


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)
