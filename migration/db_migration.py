from django.db import transaction
from django.core.management.base import BaseCommand
from django.apps import apps


class Command(BaseCommand):
    help = "Copy Buffer data from labdb to labdbproduction using the slug field."

    def handle(self, *args, **kwargs):
        source_db = "labdb"  # Source database
        target_db = "default"  # Target database (labdbproduction)

        self.stdout.write("Starting data copy for Buffer...")

        try:
            # Get the Buffer model
            Buffer = apps.get_model("buffer", "Buffer")

            # Fetch all Buffer objects from the source database
            source_buffers = Buffer.objects.using(source_db).all()

            with transaction.atomic(using=target_db):
                for buffer in source_buffers:
                    try:
                        # Check if the Buffer already exists in the target database using the slug
                        Buffer.objects.using(target_db).get(slug=buffer.slug)
                        continue  # Skip if it already exists
                    except Buffer.DoesNotExist:
                        # Create the Buffer in the target database
                        Buffer.objects.using(target_db).create(
                            name=buffer.name,
                            slug=buffer.slug,
                        )

            self.stdout.write(
                f"Successfully copied {len(source_buffers)} Buffer objects from {source_db} to {target_db}."
            )

        except Exception as e:
            self.stdout.write(f"Error copying data for Buffer: {e}")

        self.stdout.write("Data copy for Buffer completed.")


def run():
    print("Starting migration script...")

    # Add your data migration logic here
    # For example:
    print("start")
    c = Command()
    c.handle()
    print("end")



