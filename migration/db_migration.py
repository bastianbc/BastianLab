from django.db import transaction
from django.core.management.base import BaseCommand
from django.apps import apps


class Command(BaseCommand):
    help = "Copy Bait data from labdb to labdbproduction using unique fields."

    def handle(self, *args, **kwargs):
        source_db = "labdb"  # Source database
        target_db = "default"  # Target database (labdbproduction)

        self.stdout.write("Starting data copy for Bait...")

        try:
            # Get the Bait model
            app_label, model_name = "bait", "Bait"
            model = apps.get_model(app_label, model_name)

            # Fetch all baits from the source database
            source_baits = model.objects.using(source_db).all()

            with transaction.atomic(using=target_db):
                for bait in source_baits:
                    try:
                        # Check if the bait already exists in the target database using a unique field (e.g., name or slug)
                        target_bait = model.objects.using(target_db).get(name=bait.name)
                        continue  # Skip if it already exists
                    except model.DoesNotExist:
                        # Create a new bait in the target database
                        model.objects.using(target_db).create(
                            name=bait.name,
                            description=bait.description,  # Add other fields as needed
                            created_at=bait.created_at,
                        )

            self.stdout.write(
                f"Successfully copied {len(source_baits)} baits from {source_db} to {target_db}."
            )

        except Exception as e:
            self.stdout.write(f"Error copying data for Bait: {e}")

        self.stdout.write("Data copy for Bait completed.")




def run():
    print("Starting migration script...")

    # Add your data migration logic here
    # For example:
    print("start")
    c = Command()
    c.handle()
    print("end")



