"""Create fresh, editable Wagtail pages and introductory content."""
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.core.files import File
from wagtail.models import Page, Site
from wagtail.images import get_image_model

from core.models import HomePage, SectionPage, ServiceItemPage, SiteSettings, TeamMemberPage
from pathlib import Path
from PIL import Image as PillowImage


SECTIONS = [
    ("about", "About", "Improving access to essential care", "Medical Services Management Trust Nepal (MSMT Nepal) is a professional, socially driven organization established in 2004 A.D. (2060 B.S.) to improve access to quality medicines and healthcare, especially for poor and vulnerable communities."),
    ("team", "Our Team", "People behind the work", "Meet the Executive Committee and senior staff bringing experience in healthcare, finance, governance, quality and community service."),
    ("services", "Services", "Care and medicine access", "From a dependable supply of medicines and medical goods to community clinic care, health camps, humanitarian response and professional training, MSMT Nepal supports health providers and communities across Nepal."),
    ("notices", "Notices", "Notices and announcements", "Service updates and announcements from Medical Services Management Trust Nepal, listed by publication date."),
    ("media", "Media", "Stories, updates and resources", "Find approved news, stories, reports, photographs and videos from MSMT Nepal."),
    ("contact", "Contact Us", "Get in touch with MSMT Nepal", "For service information, organizational inquiries and partnerships, contact our team."),
]

ABOUT_BODY = """
<h2>Medicine access with communities in mind</h2>
<p>Medical Services Management Trust Nepal (MSMT Nepal) is a professional, socially driven organization established in 2004 A.D. (2060 B.S.). It grew from the localization of the Medical Services Department of United Mission to Nepal and International Nepal Fellowship. MSMT Nepal supplies quality medicines and medical products to healthcare providers delivering direct patient care, with a focus on poor and vulnerable communities.</p>
<p>MSMT Nepal brings together professionals from the medical, pharmaceutical and management sectors. Its work includes medicine supply, doorstep delivery for people requiring regular medication, a community health clinic, annual health camps, humanitarian support, and professional training for healthcare providers and administrators.</p>
<h2>Our objectives</h2>
<p>We work to ensure continuous access to essential medicines and medical equipment, provide affordable healthcare supplies, maintain efficient and sustainable operations, strengthen healthcare delivery through partnerships, and reinvest operating surpluses in service improvement.</p>
<h2>Quality and compliance</h2>
<p>MSMT Nepal's supplied organizational profile states that it is certified by ICS to ISO 9001:2015 for the distribution and sales of pharmaceutical products to different customers. It also states that the organization is recognized by Nepal's Department of Drug Administration for compliance with Good Storage and Distribution Practices (GSDP).</p>
<p>The organization's quality approach includes approved-supplier evaluation, in-house quality assurance, batch traceability and recall processes, expiry management, temperature-controlled storage, and attention to applicable government guidelines and regulatory requirements.</p>
<h2>Professional development and collaboration</h2>
<p>MSMT Nepal organizes workshops, seminars, policy dialogues and professional development programs, including hospital and pharmaceutical management workshops and good dispensing practice training. The organization works with local governments, healthcare providers and other organizations to support healthcare delivery and reach communities.</p>
"""

SERVICES = [
    ("medicines-and-medical-goods-supply", "Medicines and medical goods supply", "Quality medicines and medical products for hospitals, trusts, NGOs, community hospitals and other organizations providing direct patient care.", "current", "<p>MSMT Nepal supplies medicines and medical products to non-profit and socially driven organizations, including missionary hospitals, trusts, NGOs, community hospitals, welfare organizations and social enterprises providing direct patient care.</p><p>The supplied profile describes quality assurance, supplier evaluation, expiry management and storage and distribution practices as part of the organization's work. Contact MSMT Nepal to discuss product needs and current supply arrangements.</p>"),
    ("doorstep-medicine-delivery", "Doorstep medicine delivery", "Regular medicine support for people who need ongoing treatment, with registration, prescription review and home delivery.", "current", "<p>MSMT Nepal offers a doorstep medicine service for individuals who require lifelong medication. The supplied profile describes registering medical histories, regular follow-up with specialist doctors based on a person's health condition, and delivery of required medicines to the home at affordable cost.</p><p>The service infographic outlines registration, prescription checking, recording health details, medicine preparation and safe packaging, home delivery and transparent billing. Contact MSMT Nepal for eligibility and current service arrangements.</p>", "doorstep-medicine-delivery.jpeg"),
    ("community-health-clinic", "Community health clinic", "Affordable clinic services at MSMT premises for poor and vulnerable people, including consultations, laboratory tests and pharmacy support.", "current", "<p>Established at MSMT Nepal's premises in 2026, the community health clinic focuses on serving poor and vulnerable populations at subsidized and affordable costs. Services described in the supplied profile include doctor consultations, laboratory testing, dressing, pharmacy support and diagnostic facilities.</p><p>The clinic operates for a limited duration each day and primarily serves targeted individuals in need. Please contact MSMT Nepal for current opening hours and service details.</p>"),
    ("health-camps", "Health camps", "Annual general and specialized health camps with local governments, healthcare providers and partner organizations.", "current", "<p>MSMT Nepal conducts general and specialized health camps each year in collaboration with local governments, healthcare providers and other organizations, with a focus on poor and vulnerable communities.</p>"),
    ("humanitarian-support", "Humanitarian support", "Medicine, medical supplies and food support during natural disasters and health emergencies.", "current", "<p>MSMT Nepal describes providing humanitarian support during crises, including natural disasters and health emergencies such as COVID-19. Support has included medicines, medical materials and food for vulnerable communities, delivered in coordination with partners.</p>"),
    ("professional-training-and-development", "Professional training and development", "Workshops, policy dialogues and professional development for healthcare providers and administrators.", "current", "<p>MSMT Nepal organizes workshops, seminars and professional development programs to strengthen the skills and knowledge of healthcare providers and administrators. Programs described in the supplied profile include hospital and pharmaceutical management workshops, national policy dialogues and good dispensing practice training.</p><p>Resource persons have included external experts, Government of Nepal officials, policy advocates, senior pharmacists and industry professionals.</p>"),
    ("retail-pharmacy", "Retail pharmacy", "The supplied brochure lists a retail pharmacy service for people with prescriptions; confirm current availability directly with MSMT Nepal.", "confirm", "<p>The supplied brochure lists a retail pharmacy service for individuals with prescriptions. Please contact MSMT Nepal to confirm current availability and access details.</p>"),
]

TEAM = [
    ("kumar-jung-thakuri", "Kumar Jung Thakuri", "Chairperson, Executive Committee", "Finance and management professional with more than four decades of experience in financial management, human resources and governance.", "<p>Kumar Jung Thakuri is a finance and management professional with more than four decades of experience in financial management, human resource management and governance across international non-governmental organizations and private-sector institutions.</p><p>He holds a master's degree in business studies and is an ACCA Scholar. His expertise includes strategic planning, program development, institutional networking and resource mobilization. As Chairperson of MSMT Nepal's Executive Committee, he provides strategic leadership and governance oversight.</p>", "Kumar.png"),
    ("bina-maharjan", "Bina Maharjan", "Vice Chair, Executive Committee", "Social change advocate with experience in gender training, women's empowerment and community engagement.", "<p>Bina Maharjan is a founding member and Vice Chairperson of MSMT Nepal. She has academic training in gender equality and sociology and is pursuing a master's degree in Gender Studies.</p><p>She worked for 25 years at United Mission to Nepal as an Administrative Officer and Gender Trainer. She is also the founder and Chairperson of Sambhawana Nepal, where she promotes women's empowerment, and is a GBV activist and karate black belt.</p>", "Bina.png"),
    ("bikash-pandey", "Bikash Pandey", "Secretary, Executive Committee", "Microbiology professional with leadership experience in biotechnology, quality assurance and management systems.", "<p>Bikash Pandey is a microbiology professional with a master's degree in microbiology and leadership experience in biotechnology and quality management. He is a certified ISO and quality assurance auditor and has led quality, compliance and operational improvement initiatives.</p><p>His experience includes executive roles in national and international organizations and university lecturing. He is interested in pharmacovigilance and strengthening healthcare systems and access to quality medicines and diagnostic services.</p>", "Bikash.jpg"),
    ("kalyan-bikram-shah", "Kalyan Bikram Shah", "Treasurer, Executive Committee", "Finance and administration professional with more than 18 years of experience, including over 15 years in the development sector.", "<p>Kalyan Bikram Shah has experience in finance, administration and grants management, including budgeting, procurement, internal controls, compliance, audit coordination and donor-funded project management.</p><p>He holds a bachelor's degree in finance and has worked with private companies, cooperatives, hospitals, educational institutions, national NGOs and international NGOs. As Treasurer, he provides financial oversight and guidance to MSMT Nepal.</p>", "Kalyan.jpg"),
    ("bhim-prasad-pokhrel", "Bhim Prasad Pokhrel", "Executive Committee Member", "Organizational management and governance leader with more than three decades of development-sector experience.", "<p>Bhim Prasad Pokhrel serves part-time as the lead of MSMT Nepal. A founder chairperson, he has contributed to institutional leadership, strategic planning and organizational development over more than three decades in the development sector.</p><p>He also serves part-time as Executive Director of the Educational Resource Development Center Nepal (ERDCN) and holds volunteer board positions in local non-governmental organizations.</p>", "Bhim.jpg"),
    ("yagya-prasad-chapagai", "Yagya Prasad Chapagai", "Board Member", "Finance professional with more than four decades of experience across national and international NGOs and the private sector.", "<p>Yagya Prasad Chapagai has more than four decades of experience in financial management across national and international NGOs and the private sector. He previously served as Finance and Administration Director at MSMT Nepal and as the organization's Vice President.</p><p>He contributes institutional knowledge and experience to the Executive Committee and is active in advisory and governance roles with other organizations.</p>", "Yagya.jpg"),
    ("shyam-narayan-shrestha", "Shyam Narayan Shrestha", "Legal Advisor", "Senior Advocate with more than 30 years of legal practice and experience advising organizations.", "<p>Shyam Narayan Shrestha is a Senior Advocate with more than 30 years of legal practice. He holds a master's degree in Sociology and a law degree from Tribhuvan University and has represented clients at all levels of the judiciary, from District Courts to the Supreme Court.</p><p>He previously served as Chief Attorney of Bagmati Province and continues to provide legal services and advice to organizations.</p>", "Shyam.jpg"),
    ("bade-babu-thapa", "Bade Babu Thapa", "Pharmaceutical Advisor", "Senior pharmacist with more than 42 years of service in community health, immunization and pharmaceutical supply chains.", "<p>Bade Babu Thapa is a senior pharmacist and technical advisor with more than 42 years of service in community health, national immunization programs and pharmaceutical supply chain management within the Government of Nepal. He holds a master's degree.</p><p>His expertise includes vaccine lifecycle management, essential medicine supply chains and cold chain systems. He has also worked as a consultant with UNICEF and FHI Nepal. At MSMT Nepal, he advises on operational efficiency, regulatory compliance and sustainable management of medical infrastructure.</p>", "Bade.png"),
    ("puran-malla-thakuri", "Puran Malla Thakuri", "Operations Manager", "Operations manager with more than two decades of experience managing medicines and surgical supplies.", "<p>Puran Malla Thakuri serves as Operations Manager at MSMT Nepal and has more than two decades of experience in managing medicines and surgical supplies.</p><p>His work has included medicine store management, inventory control, procurement and supply chain management. He coordinates with NGOs, INGOs, suppliers and customers to support healthcare programs.</p>", "Puran.png"),
    ("jhabendra-prakash-bhattarai", "Jhabendra Prakash Bhattarai", "Administration and Finance Manager", "Administration and finance manager with more than 20 years of experience in financial and program management.", "<p>Jhabendra Prakash Bhattarai holds a master's degree in management from Tribhuvan University and has more than 20 years of professional experience in financial and program management across rural development, education, health and organizational strengthening.</p><p>Before joining MSMT Nepal in 2024, he worked with organizations including United Mission to Nepal (UMN), FIAN-Nepal, the Italian Foundation and Mission East. His work includes financial planning, budgeting, compliance and program administration.</p>", "Jhabendra.jpg"),
    ("bhumika-shrestha", "Bhumika Shrestha", "Pharmacy Officer", "Pharmacy professional with a Bachelor of Pharmacy, Diploma in Pharmacy and more than 10 years of hospital pharmacy experience.", "<p>Bhumika Shrestha holds a Bachelor of Pharmacy and a Diploma in Pharmacy and has more than 10 years of experience in hospital pharmacy services, with additional experience in the pharmaceutical industry.</p><p>Her work includes medication management, pharmaceutical care, dispensing, inventory control, quality assurance and pharmacy operations. She supports safe and rational medicine use, regulatory compliance and patient care.</p>", "Bhumika.png"),
]


def wagtail_image(title, relative_path, alt_text):
    image_model = get_image_model()
    existing = image_model.objects.filter(title=title).first()
    if existing:
        return existing
    source = Path(settings.BASE_DIR) / "static" / "images" / relative_path
    if not source.is_file():
        raise CommandError(f"Required supplied image is missing: {source}")
    with PillowImage.open(source) as opened:
        width, height = opened.size
    with source.open("rb") as handle:
        image = image_model(title=title, file=File(handle, name=source.name), width=width, height=height, description=alt_text)
        image.save()
    return image


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

        # Use the supplied MSMT premises photograph where no homepage image is set.
        if not home.hero_image_id:
            home.hero_image = wagtail_image("MSMT Nepal premises", "msmt-office.webp", "MSMT Nepal premises in Chakupat, Lalitpur")
            home.save_revision().publish()
        old_stats = [
            ("impact_stat_two_value", "50+", "20+"),
            ("impact_stat_two_label", "Partner hospitals and community clinics", "Years of services"),
            ("impact_stat_three_value", "70+", "50+"),
            ("impact_stat_three_label", "Districts reached", "Partner hospitals and community clinics"),
            ("impact_stat_four_value", "ISO 9001:2015", "70+"),
            ("impact_stat_four_label", "Quality management certification", "Districts reached"),
        ]
        stats_changed = False
        for field, old_value, new_value in old_stats:
            if getattr(home, field) == old_value:
                setattr(home, field, new_value)
                stats_changed = True
        if stats_changed:
            home.save_revision().publish()
        # Fill the approved brochure facts only while these values still contain defaults.
        for key, title, heading, intro in SECTIONS:
            page = SectionPage.objects.filter(section=key).first()
            route_slug = "our-team" if key == "team" else key
            if not page:
                page = SectionPage(title=title, slug=route_slug, section=key, introduction=intro, body=ABOUT_BODY if key == "about" else "")
                home.add_child(instance=page)
                page.save_revision().publish()
                self.stdout.write(f"Created the {title} page.")
            else:
                changed = False
                if key == "team" and page.slug == "team":
                    # Keep the current site's public /our-team URL.
                    page.slug = route_slug
                    changed = True
                if key == "team" and page.introduction in {
                    "Team profiles and approved portraits will appear here once supplied and approved.",
                    "Meet the people who provide governance, technical advice and day-to-day leadership for MSMT Nepal.",
                }:
                    page.introduction = intro
                    changed = True
                if key == "about":
                    if "MSMT Nepal is a professional, socially driven trust established in 2004" in page.body:
                        page.body = ABOUT_BODY
                        changed = True
                    elif not page.body:
                        page.body = ABOUT_BODY
                        changed = True
                    if page.introduction == "MSMT Nepal works to make essential medicines and healthcare more accessible, especially for poor and vulnerable communities.":
                        page.introduction = intro
                        changed = True
                if changed:
                    page.save_revision().publish()
            if key == "services":
                for order, item in enumerate(SERVICES, 1):
                    slug, item_title, summary, availability, body, *feature = item
                    service = ServiceItemPage.objects.filter(slug=slug, depth=page.depth + 1, path__startswith=page.path).first()
                    if not service:
                        service = ServiceItemPage(
                            title=item_title,
                            slug=slug,
                            summary=summary,
                            body=body,
                            availability=availability,
                            sort_order=order,
                        )
                        page.add_child(instance=service)
                    else:
                        if not service.body:
                            service.body = body
                        if feature and not service.feature_image_id:
                            service.feature_image = wagtail_image(
                                "Doorstep medicine delivery service",
                                feature[0],
                                "Steps in MSMT Nepal's doorstep medicine delivery service",
                            )
                    if feature and not service.feature_image_id:
                        service.feature_image = wagtail_image(
                            "Doorstep medicine delivery service",
                            feature[0],
                            "Steps in MSMT Nepal's doorstep medicine delivery service",
                        )
                    service.save_revision().publish()
            if key == "team":
                for order, profile in enumerate(TEAM, 1):
                    slug, name, role, summary, body, portrait_file = profile
                    member = TeamMemberPage.objects.filter(slug=slug, depth=page.depth + 1, path__startswith=page.path).first()
                    if member:
                        continue
                    portrait = wagtail_image(f"MSMT staff portrait - {name}", f"team/{portrait_file}", f"Portrait of {name}")
                    member = TeamMemberPage(
                        title=name,
                        slug=slug,
                        role=role,
                        summary=summary,
                        body=body,
                        portrait=portrait,
                        sort_order=order,
                    )
                    page.add_child(instance=member)
                    member.save_revision().publish()

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
        self.stdout.write(self.style.SUCCESS("Starter pages, supplied team profiles, portraits and service content are ready. Add notices and media stories in Wagtail."))
