from .models import HomePage, SectionPage


def website(request):
    home = HomePage.objects.live().first()
    sections = []
    if home:
        sections = list(SectionPage.objects.live().child_of(home).order_by("path"))
    return {"site_home": home, "site_navigation": sections, "site_sections": {item.section: item for item in sections}}
