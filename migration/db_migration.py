from django.db import transaction
from django.core.management.base import BaseCommand
from django.apps import apps


class Command(BaseCommand):
    help = "Copy Body data from labdb to labdbproduction while handling parent relationships."

    def handle(self, *args, **kwargs):
        source_db = "labdb"  # Source database
        target_db = "default"  # Target database (labdbproduction)

        self.stdout.write("Starting data copy for Body...")

        try:
            # Get the Body model
            Body = apps.get_model("body", "Body")

            # Fetch all Body objects from the source database
            source_bodies = Body.objects.using(source_db).all()

            # Track a mapping of source Body IDs to target Body objects
            body_mapping = {}

            with transaction.atomic(using=target_db):
                # Copy all Body objects without setting parents
                for body in source_bodies:
                    try:
                        # Check if the Body already exists in the target database using the name
                        target_body = Body.objects.using(target_db).get(name=body.name)
                        body_mapping[body.id] = target_body
                        continue  # Skip if it already exists
                    except Body.DoesNotExist:
                        # Create the Body in the target database without the parent
                        target_body = Body.objects.using(target_db).create(
                            name=body.name,
                            parent=None,  # Parent will be set later
                        )
                        body_mapping[body.id] = target_body

                # Set parent relationships
                for body in source_bodies:
                    if body.parent:
                        parent_body = body_mapping.get(body.parent_id)
                        target_body = body_mapping.get(body.id)

                        if parent_body and target_body:
                            target_body.parent = parent_body
                            target_body.save(using=target_db)

            self.stdout.write(
                f"Successfully copied {len(source_bodies)} Body objects from {source_db} to {target_db}."
            )

        except Exception as e:
            self.stdout.write(f"Error copying data for Body: {e}")

        self.stdout.write("Data copy for Body completed.")


def run():
    print("Starting migration script...")

    # Add your data migration logic here
    # For example:
    print("start")
    c = Command()
    c.handle()
    print("end")



