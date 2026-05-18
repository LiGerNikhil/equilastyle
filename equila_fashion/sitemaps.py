from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from blog.models import Post
from products.models import Product, Category


class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = "weekly"

    def items(self):
        return [
            "products:home",
            "products:about",
            "products:product_list",
            "products:shipping",
            "products:returns",
            "products:size_guide",
            "products:privacy",
            "products:terms",
            "products:cookies",
            "blog:post_list",
        ]

    def location(self, item):
        return reverse(item)


class ProductSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return Product.objects.filter(is_active=True, is_available=True)

    def location(self, obj):
        return reverse("products:product_detail", kwargs={"slug": obj.slug})

    def lastmod(self, obj):
        return obj.updated_at if hasattr(obj, "updated_at") else obj.created_at


class CategorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Category.objects.all()

    def location(self, obj):
        return reverse("products:category_products", kwargs={"slug": obj.slug})


class BlogPostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return Post.objects.filter(status="published")

    def location(self, obj):
        return reverse("blog:post_detail", kwargs={"slug": obj.slug})

    def lastmod(self, obj):
        return obj.updated_at
