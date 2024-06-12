from django.db import models
from django.utils.text import slugify
from django.urls import reverse

class Article(models.Model):
    title = models.CharField(max_length=250)
    content = models.TextField()
    slug = models.SlugField(blank=True, null=True)
    parent = models.ForeignKey("self", blank=True, null=True, on_delete=models.CASCADE, related_name="children")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "article"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('article_detail', kwargs={'slug': self.slug})

    def get_parents(self):
        parents = []
        current_article = self
        while current_article.parent:
            parents.append(current_article.parent)
            current_article = current_article.parent
        return parents[::-1]  # Reverse to get the top-down order

    def get_childs(self):
        childs = []
        def _get_childs(page):
            for child in page.children.all():
                childs.append(child)
                _get_childs(child)
        _get_childs(self)
        return childs
