from django.db import models
from django.utils import timezone
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.documents import get_document_model_string
from wagtail.fields import RichTextField
from wagtail.models import Page
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.images import get_image_model_string


class HomePage(Page):
    """Editable landing page with the sections shown on the reference homepage."""
    hero_eyebrow = models.CharField(max_length=120, default="Healthcare access across Nepal")
    hero_heading = models.CharField(max_length=180, default="Essential medicine. Closer to everyone.")
    hero_intro = models.TextField(default="MSMT Nepal works to strengthen access to essential medicines and healthcare support through dependable supply and community-focused services.")
    hero_image = models.ForeignKey(get_image_model_string(), null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    founding_year = models.CharField(max_length=12, default="2004")
    impact_stat_two_value = models.CharField(max_length=32, default="20+")
    impact_stat_two_label = models.CharField(max_length=90, default="Years of services")
    impact_stat_three_value = models.CharField(max_length=32, default="50+")
    impact_stat_three_label = models.CharField(max_length=90, default="Partner hospitals and community clinics")
    impact_stat_four_value = models.CharField(max_length=32, default="70+")
    impact_stat_four_label = models.CharField(max_length=90, default="Districts reached")
    services_heading = models.CharField(max_length=160, default="Services that support healthier communities")
    services_intro = models.CharField(max_length=240, default="Reliable medicine supply and practical care, designed around community needs.")
    impact_heading = models.CharField(max_length=140, default="Better access, stronger health systems")
    impact_text = models.TextField(default="MSMT Nepal is a professional, socially driven trust established in 2004 to help make quality medicines and healthcare more accessible, especially for poor and vulnerable communities.")
    objective_heading = models.CharField(max_length=140, default="Reliable and affordable care")
    objective_text = models.TextField(default="Ensure continuous access to essential medicines and medical equipment, strengthen sustainable supply systems, build healthcare capacity, and reinvest surpluses in service improvement.")
    service_support_heading = models.CharField(max_length=140, default="Support from supply to community care")
    service_support_text = models.TextField(default="Medicine and medical goods supply, doorstep medicine delivery, community clinic care, annual health camps, humanitarian response, and professional training for healthcare providers.")
    approach_heading = models.CharField(max_length=140, default="Quality and reliability")
    approach_text = models.TextField(default="MSMT Nepal brings together medical, pharmaceutical and management professionals to support dependable medicine supply and stronger healthcare services.")
    approach_point_one = models.CharField(max_length=140, default="Working with health providers and communities")
    approach_point_two = models.CharField(max_length=140, default="Supporting sustainable medicine supply")
    approach_point_three = models.CharField(max_length=140, default="Building skills through training and collaboration")
    media_heading = models.CharField(max_length=140, default="Stories, updates and resources")
    media_intro = models.TextField(default="Contact MSMT Nepal to learn more about its services and work with communities.")

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel("hero_eyebrow"), FieldPanel("hero_heading"), FieldPanel("hero_intro"), FieldPanel("hero_image"),
        ], heading="Homepage introduction"),
        MultiFieldPanel([
            FieldPanel("founding_year"),
            FieldPanel("impact_stat_two_value"), FieldPanel("impact_stat_two_label"),
            FieldPanel("impact_stat_three_value"), FieldPanel("impact_stat_three_label"),
            FieldPanel("impact_stat_four_value"), FieldPanel("impact_stat_four_label"),
        ], heading="At a glance"),
        MultiFieldPanel([FieldPanel("services_heading"), FieldPanel("services_intro")], heading="Services introduction"),
        MultiFieldPanel([FieldPanel("impact_heading"), FieldPanel("impact_text"), FieldPanel("objective_heading"), FieldPanel("objective_text")], heading="Our purpose"),
        MultiFieldPanel([FieldPanel("service_support_heading"), FieldPanel("service_support_text")], heading="Purpose and services summary"),
        MultiFieldPanel([FieldPanel("approach_heading"), FieldPanel("approach_text"), FieldPanel("approach_point_one"), FieldPanel("approach_point_two"), FieldPanel("approach_point_three")], heading="Our approach"),
        MultiFieldPanel([FieldPanel("media_heading"), FieldPanel("media_intro")], heading="Stories and updates"),
    ]
    parent_page_types = ["wagtailcore.Page"]
    subpage_types = ["core.SectionPage"]
    max_count = 1
    template = "core/home_page.html"

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        services_page = SectionPage.objects.live().filter(section="services").first()
        media_page = SectionPage.objects.live().filter(section="media").first()
        context["featured_services"] = ServiceItemPage.objects.live().descendant_of(services_page)[:3] if services_page else []
        context["latest_media"] = MediaStoryPage.objects.live().descendant_of(media_page)[:1] if media_page else []
        return context

    class Meta:
        verbose_name = "Homepage"


class SectionPage(Page):
    SECTION_CHOICES = [
        ("about", "About"), ("team", "Our Team"), ("services", "Services"),
        ("notices", "Notices"), ("media", "Media"), ("contact", "Contact Us"),
    ]
    section = models.CharField(max_length=20, choices=SECTION_CHOICES, unique=True)
    introduction = models.TextField(blank=True)
    body = RichTextField(blank=True, features=["bold", "italic", "ol", "ul", "link", "document-link"])
    content_panels = Page.content_panels + [FieldPanel("section"), FieldPanel("introduction"), FieldPanel("body")]
    parent_page_types = ["core.HomePage"]
    subpage_types = ["core.ServiceItemPage", "core.TeamMemberPage", "core.NoticePage", "core.MediaStoryPage"]
    template = "core/section_page.html"

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        if self.section == "services":
            context["items"] = ServiceItemPage.objects.live().descendant_of(self).order_by("sort_order", "title")
        elif self.section == "team":
            context["items"] = TeamMemberPage.objects.live().descendant_of(self).order_by("sort_order", "title")
        elif self.section == "notices":
            context["items"] = NoticePage.objects.live().descendant_of(self).order_by("-published_on", "-first_published_at")
        elif self.section == "media":
            context["items"] = MediaStoryPage.objects.live().descendant_of(self).order_by("-first_published_at")
        return context

    class Meta:
        verbose_name = "Website section"


class OrderedContentPage(Page):
    sort_order = models.PositiveIntegerField(default=100)
    summary = models.TextField(blank=True)
    body = RichTextField(blank=True, features=["bold", "italic", "ol", "ul", "link", "document-link"])
    parent_page_types = ["core.SectionPage"]
    subpage_types = []

    class Meta:
        abstract = True


class ServiceItemPage(OrderedContentPage):
    AVAILABILITY_CHOICES = [("current", "Current service"), ("confirm", "Availability to confirm")]
    availability = models.CharField(max_length=20, choices=AVAILABILITY_CHOICES, default="current")
    icon_name = models.CharField(max_length=40, blank=True, help_text="Optional short icon key, for example medicines or clinic.")
    feature_image = models.ForeignKey(get_image_model_string(), null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    content_panels = Page.content_panels + [FieldPanel("summary"), FieldPanel("body"), FieldPanel("feature_image"), FieldPanel("availability"), FieldPanel("sort_order")]
    template = "core/item_page.html"


class TeamMemberPage(OrderedContentPage):
    role = models.CharField(max_length=140, blank=True)
    portrait = models.ForeignKey(get_image_model_string(), null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    content_panels = Page.content_panels + [FieldPanel("role"), FieldPanel("portrait"), FieldPanel("summary"), FieldPanel("body"), FieldPanel("sort_order")]
    template = "core/item_page.html"


class NoticePage(OrderedContentPage):
    published_on = models.DateField(default=timezone.localdate)
    attachment = models.ForeignKey(get_document_model_string(), null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    content_panels = Page.content_panels + [FieldPanel("published_on"), FieldPanel("summary"), FieldPanel("body"), FieldPanel("attachment"), FieldPanel("sort_order")]
    template = "core/item_page.html"


class MediaStoryPage(OrderedContentPage):
    cover_image = models.ForeignKey(get_image_model_string(), null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    resource = models.ForeignKey(get_document_model_string(), null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    external_url = models.URLField(blank=True)
    content_panels = Page.content_panels + [FieldPanel("cover_image"), FieldPanel("summary"), FieldPanel("body"), FieldPanel("resource"), FieldPanel("external_url")]
    template = "core/item_page.html"


@register_setting
class SiteSettings(BaseSiteSetting):
    organization_name = models.CharField(max_length=120, default="MSMT Nepal")
    tagline = models.CharField(max_length=180, default="Working to improve access to essential medicines and healthcare services in Nepal.")
    address = models.CharField(max_length=240, default="Chakupat, Lalitpur-11, Nepal")
    email = models.EmailField(default="msmt.ngo.nepal@gmail.com")
    phone = models.CharField(max_length=40, default="+977 9768533691")
    secondary_phone = models.CharField(max_length=40, blank=True)
    map_url = models.URLField(blank=True)
    map_embed_url = models.URLField(blank=True, default="https://maps.google.com/maps?q=27.6821339,85.3264003&z=16&output=embed")
    facebook_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    footer_note = models.CharField(max_length=220, default="Information on this site is for general organizational purposes.")
    panels = [FieldPanel("organization_name"), FieldPanel("tagline"), FieldPanel("address"), FieldPanel("email"), FieldPanel("phone"), FieldPanel("secondary_phone"), FieldPanel("map_url"), FieldPanel("map_embed_url", heading="Google Maps preview URL", help_text="Paste the Google Maps embed URL for the office map preview."), MultiFieldPanel([FieldPanel("facebook_url"), FieldPanel("youtube_url"), FieldPanel("instagram_url"), FieldPanel("linkedin_url")], heading="Social links"), FieldPanel("footer_note")]

    class Meta:
        verbose_name = "Website contact and footer"


class ContactInquiry(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    subject = models.CharField(max_length=160)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-submitted_at"]
        verbose_name = "Contact inquiry"
        verbose_name_plural = "Contact inquiries"

    def __str__(self):
        return f"{self.subject} — {self.name}"
