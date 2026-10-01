from django.contrib import messages
from django.conf import settings
from django.http import FileResponse, Http404
from django.shortcuts import redirect
from django.utils.http import content_disposition_header
from django.views.decorators.http import require_POST
from pathlib import Path
import mimetypes

from .forms import InquiryForm
from .models import ContactInquiry


@require_POST
def inquiry(request):
    form = InquiryForm(request.POST)
    if form.is_valid() and not form.cleaned_data.get("company"):
        ContactInquiry.objects.create(**{key: form.cleaned_data[key] for key in ("name", "email", "phone", "subject", "message")})
        messages.success(request, "Thank you. Your inquiry has been received.")
    else:
        messages.error(request, "Please check the form and try again.")
    return redirect("/contact/#inquiry")


def public_media(request, path):
    """Serve Wagtail's public uploads when cPanel has no separate media alias."""
    root = Path(settings.MEDIA_ROOT).resolve()
    target = (root / path).resolve()
    if not target.is_relative_to(root) or not target.is_file():
        raise Http404
    content_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
    response = FileResponse(target.open("rb"), content_type=content_type)
    response["X-Content-Type-Options"] = "nosniff"
    response["Content-Disposition"] = content_disposition_header(False, target.name)
    return response
