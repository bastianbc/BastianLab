from django.db import transaction
from django.core.management.base import BaseCommand
from django.apps import apps

# List of tables to copy in order
TABLES_TO_COPY = [
    "django_content_type",  # Must be copied first
    "auth_permission",
    "auth_group",
    "auth_group_permissions",
    "auth_user",
    "auth_user_groups",
    "auth_user_permissions",
]

class Command(BaseCommand):
    help = "Copy data from labdb to labdbproduction."

    def handle(self, *args, **kwargs):
        source_db = "labdb"  # Source database
        target_db = "default"  # Target database (labdbproduction)

        # Loop through tables to copy
        for table_name in TABLES_TO_COPY:
            self.stdout.write(f"Copying data for table: {table_name}...")

            try:
                # Handle special cases for table names
                if table_name == "django_content_type":
                    app_label, model_name = "contenttypes", "ContentType"
                else:
                    app_label, model_name = table_name.split("_", 1)
                    model_name = model_name.capitalize()

                # Get the model
                model = apps.get_model(app_label, model_name)

                # Fetch data from source database
                source_objects = model.objects.using(source_db).all()

                with transaction.atomic(using=target_db):
                    # Copy data to target database
                    for obj in source_objects:
                        obj.id = None  # Reset primary key for insertion
                        obj.save(using=target_db)

                self.stdout.write(
                    f"Successfully copied {source_objects.count()} records from {source_db} to {target_db}."
                )

            except Exception as e:
                self.stdout.write(f"Error copying data for {table_name}: {e}")

        self.stdout.write("Data copy completed.")

def run():
    print("Starting migration script...")

    # Add your data migration logic here
    # For example:
    print("start")
    c = Command()
    c.handle()
    print("end")



