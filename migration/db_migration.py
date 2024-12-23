from django.db import transaction
from django.core.management.base import BaseCommand
from django.apps import apps


class Command(BaseCommand):
    help = "Copy Article data from labdb to labdbproduction using slug or title."

    def handle(self, *args, **kwargs):
        source_db = "labdb"  # Source database
        target_db = "default"  # Target database (labdbproduction)

        self.stdout.write("Starting data copy for articles...")

        try:
            # Get the Article model
            app_label, model_name = "wiki", "Article"
            model = apps.get_model(app_label, model_name)

            # Fetch all articles from the source database
            source_articles = model.objects.using(source_db).all()

            # Track a mapping of source slugs to target articles
            slug_mapping = {}

            with transaction.atomic(using=target_db):
                for article in source_articles:
                    # Check if the article already exists in the target database using slug or title
                    try:
                        target_article = model.objects.using(target_db).get(
                            slug=article.slug
                        )
                        slug_mapping[article.slug] = target_article
                        continue  # Skip if it already exists
                    except model.DoesNotExist:
                        # Create a new article in the target database
                        new_article = model.objects.using(target_db).create(
                            title=article.title,
                            content=article.content,
                            slug=article.slug,
                            created_at=article.created_at,
                        )
                        slug_mapping[article.slug] = new_article

                # Handle parent relationships
                for article in source_articles:
                    if article.parent:
                        parent_slug = article.parent.slug
                        parent_article = slug_mapping.get(parent_slug)

                        if parent_article:
                            target_article = slug_mapping.get(article.slug)
                            if target_article:
                                target_article.parent = parent_article
                                target_article.save(using=target_db)

            self.stdout.write(
                f"Successfully copied {len(source_articles)} articles from {source_db} to {target_db}."
            )

        except Exception as e:
            self.stdout.write(f"Error copying data for articles: {e}")

        self.stdout.write("Data copy for articles completed.")





def run():
    print("Starting migration script...")

    # Add your data migration logic here
    # For example:
    print("start")
    c = Command()
    c.handle()
    print("end")



