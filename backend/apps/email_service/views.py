# File: backend/apps/email_service/views.py
# Purpose: API endpoint to verify SMTP email configuration.
# App: email_service

from __future__ import annotations

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .sender import send_test_email_safe


class EmailTestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        to_email = (request.data.get("to_email") or "").strip()
        if not to_email:
            return Response(
                {"status": "error", "message": "Field 'to_email' is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        sent_ok, reason = send_test_email_safe(to_email=to_email)
        if not sent_ok:
            return Response(
                {"status": "error", "message": reason},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response(
            {"status": "success", "message": f"Test email sent to {to_email}."},
            status=status.HTTP_200_OK,
        )
