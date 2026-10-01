"""Create fresh, editable Wagtail pages and introductory content."""
from django.core.management.base import BaseCommand, CommandError
from wagtail.models import Page, Site

from core.models import HomePage, SectionPage, ServiceItemPage, SiteSettings


SECTIONS = [
    ("about", "About", "Improving access to essential care", "MSMT Nepal works to make essential medicines and healthcare more accessible, especially for poor and vulnerable communities."),
    ("team", "Our Team", "People behind the work", "Team profiles and approved portraits will appear here once supplied and approved."),
    ("services", "Services", "Care and medicine access", "From a dependable supply of medicines and medical goods to community clinic care, health camps, humanitarian response and professional training, MSMT Nepal supports health providers and communities across Nepal."),
    ("notices", "Notices", "Notices and announcements", "Service updates and announcements from Medical Services Management Trust Nepal, listed by publication date."),
    ("media", "Media", "Stories, updates and resources", "Find approved news, stories, reports, photographs and videos from MSMT Nepal."),
    ("contact", "Contact Us", "Get in touch with MSMT Nepal", "For service information, organizational inquiries and partnerships, contact our team."),
]

ABOUT_BODY = """
<h2>Medicine access with communities in mind</h2>
<p>Medical Services Management Trust Nepal (MSMT Nepal) is a professional, socially driven trust established in 2004 to help make quality medicines and healthcare more accessible, especially for poor and vulnerable communities.</p>
<p>MSMT Nepal grew from the localization of the Medical Services Department of United Mission to Nepal / International Nepal Fellowship. Since its establishment, MSMT has supplied medicines and medical products to hospitals and other organizations providing direct patient care.</p>
<p>The trust brings medical, pharmaceutical and management professionals together to strengthen healthcare delivery through training, advocacy, capacity building and collaboration with health stakeholders.</p>
<h2>Our objectives</h2>
<p>We work to ensure continuous access to essential medicines and medical equipment, make healthcare supplies affordable, maintain an efficient and sustainable supply chain, strengthen healthcare delivery through partnerships, and reinvest operating surpluses in service improvement.</p>
<h2>Services for people and health providers</h2>
<p>Our work includes medicine and medical goods supply, doorstep delivery for people requiring regular medicines, community clinic services, health camps, humanitarian support during emergencies, and professional development for healthcare providers and administrators.</p>
"""

SERVICES = [
    ("medicines-and-medical-goods-supply", "Medicines and medical goods supply", "Quality medicines and medical products supplied to hospitals, trusts, NGOs, community hospitals and other organizations providing direct patient care."),
    ("doorstep-medicine-delivery", "Doorstep medicine delivery", "Medicine support for people requiring lifelong medication, including health-history registration, specialist follow-up and home delivery at affordable cost."),
    ("community-health-clinic", "Community health clinic", "Clinic services at MSMT premises serving poor and vulnerable people at subsidized and affordable costs. Services include doctor consultations, laboratory tests, dressing, pharmacy and diagnostics."),
    ("health-camps", "Health camps", "Annual general and specialized health camps delivered with local governments, healthcare providers and partner organizations."),
    ("humanitarian-support", "Humanitarian support", "Medicine, medical supplies and food support during disasters and health emergencies, delivered with partners to help vulnerable communities."),
    ("professional-training-and-development", "Professional training and development", "Workshops, policy dialogues and professional development for healthcare providers and administrators, including hospital and pharmaceutical management and good dispensing practice."),
    ("retail-pharmacy", "Retail pharmacy", "The brochure lists a retail pharmacy for individuals with prescriptions. Contact MSMT Nepal for current availability and access details.", "confirm"),
]


class Command(BaseCommand):
    help = "Create initial public pages and editable reference content on a fresh database."

    def handle(self, *args, **options):
        root = Page.get_first_root_node()
        home = HomePage.objects.filter(slug="home").first()
        if not home:
            starter = root.get_children().filter(slug="home").first()
            if starter:
                if starter.title != "Welcome to your new Wagtail site!":
                    raise CommandError("A page already uses the homepage slug. Review the page tree before seeding.")
                # Free the default welcome-page slug before adding our new homepage.
                starter.slug = "welcome-placeholder"
                starter.title = "Welcome page (unused)"
                starter.live = False
                starter.save()
            home = HomePage(title="MSMT Nepal", slug="home")
            root.add_child(instance=home)
            home.save_revision().publish()
            self.stdout.write("Created the MSMT Nepal homepage.")
        else:
            self.stdout.write("Homepage already exists; leaving its content unchanged.")

        for key, title, heading, intro in SECTIONS:
            page = SectionPage.objects.filter(section=key).first()
            route_slug = "our-team" if key == "team" else key
            if not page:
                page = SectionPage(title=title, slug=route_slug, section=key, introduction=intro, body=ABOUT_BODY if key == "about" else "")
                home.add_child(instance=page)
                page.save_revision().publish()
                self.stdout.write(f"Created the {title} page.")
            elif key == "team" and page.slug == "team":
                # Keep the current site's public /our-team URL.
                page.slug = route_slug
                page.save_revision().publish()
            if key == "services":
                for order, item in enumerate(SERVICES, 1):
                    slug, item_title, summary, *status = item
                    service = ServiceItemPage.objects.filter(slug=slug, depth=page.depth + 1, path__startswith=page.path).first()
                    if not service:
                        service = ServiceItemPage(
                            title=item_title,
                            slug=slug,
                            summary=summary,
                            availability=status[0] if status else "current",
                            sort_order=order,
                        )
                        page.add_child(instance=service)
                        service.save_revision().publish()

        site, _ = Site.objects.get_or_create(is_default_site=True, defaults={"hostname": "localhost", "port": 8000, "root_page": home, "site_name": "MSMT Nepal"})
        if site.root_page_id != home.pk:
            site.root_page = home
            site.site_name = "MSMT Nepal"
            site.save()
        starter = Page.objects.filter(slug="welcome-placeholder", title="Welcome page (unused)").first()
        if starter:
            starter.delete()
        SiteSettings.objects.get_or_create(site=site, defaults={
            "secondary_phone": "+977 9768533692",
            "map_url": "https://www.google.com/maps/place/MSMT+Nepal/@27.682152,85.326448,15z/",
        })
        self.stdout.write(self.style.SUCCESS("Starter pages are ready. Add team profiles, notices, media, and approved photos in Wagtail."))
