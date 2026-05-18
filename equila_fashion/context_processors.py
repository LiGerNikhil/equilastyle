from django.conf import settings
from django.templatetags.static import static

from . import seo


def seo_context(request):
    site_url = getattr(settings, "SITE_URL", "https://www.equilastyle.com").rstrip("/")
    canonical = request.build_absolute_uri(request.path)

    og_image = site_url + static("images/logo.jpeg")

    return {
        "seo_site_name": seo.SITE_NAME,
        "seo_site_tagline": seo.SITE_TAGLINE,
        "seo_legal_name": seo.LEGAL_NAME,
        "seo_site_url": site_url,
        "seo_canonical_url": canonical,
        "seo_default_keywords": seo.DEFAULT_KEYWORDS,
        "seo_default_description": seo.DEFAULT_DESCRIPTION,
        "seo_og_image_default": og_image,
        "seo_twitter_site": "@equilastyle",
    }
