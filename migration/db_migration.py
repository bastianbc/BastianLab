from django.db import transaction
from django.core.management.base import BaseCommand
from django.apps import apps


class Command(BaseCommand):
    help = "Copy Method data from labdb to labdbproduction using the slug field."

    def handle(self, *args, **kwargs):
        source_db = "labdb"  # Source database
        target_db = "default"  # Target database (labdbproduction)

        self.stdout.write("Starting data copy for Method...")

        try:
            # Get the Method model
            Method = apps.get_model("method", "Method")

            # Fetch all Method objects from the source database
            source_methods = Method.objects.using(source_db).all()

            with transaction.atomic(using=target_db):
                for method in source_methods:
                    try:
                        # Check if the Method already exists in the target database using the slug
                        Method.objects.using(target_db).get(slug=method.slug)
                        continue  # Skip if it already exists
                    except Method.DoesNotExist:
                        # Create the Method in the target database
                        Method.objects.using(target_db).create(
                            name=method.name,
                            slug=method.slug,
                        )

            self.stdout.write(
                f"Successfully copied {len(source_methods)} Method objects from {source_db} to {target_db}."
            )

        except Exception as e:
            self.stdout.write(f"Error copying data for Method: {e}")

        self.stdout.write("Data copy for Method completed.")


def run():
    print("Starting migration script...")

    # Add your data migration logic here
    # For example:
    print("start")
    c = Command()
    c.handle()
    print("end")



