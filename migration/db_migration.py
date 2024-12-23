from django.db import transaction
from django.core.management.base import BaseCommand
from django.apps import apps


class Command(BaseCommand):
    help = "Copy all Variant-related models data from labdb to labdbproduction."

    def handle(self, *args, **kwargs):
        source_db = "labdb"  # Source database
        target_db = "default"  # Target database (labdbproduction)

        self.stdout.write("Starting data copy for Variant-related models...")

        try:
            models_to_copy = [
                ("variant", "VariantFile"),
            ]
            # Models in dependency order

            # Mapping of source objects to target objects for foreign key relationships
            object_mappings = {model_name: {} for _, model_name in models_to_copy}

            with transaction.atomic(using=target_db):
                for app_label, model_name in models_to_copy:
                    self.stdout.write(f"Copying {model_name}...")
                    model = apps.get_model(app_label, model_name)

                    # Fetch all objects from the source database
                    source_objects = model.objects.using(source_db).all()

                    for obj in source_objects:
                        # Handle foreign key fields and create object in the target database
                        new_obj_data = {}
                        for field in obj._meta.fields:
                            if field.is_relation and field.remote_field:
                                # ForeignKey: Use the mapping to link related objects
                                related_model_name = field.remote_field.model._meta.object_name
                                related_object = getattr(obj, field.name)
                                if related_object:
                                    new_obj_data[field.name] = object_mappings[related_model_name].get(
                                        related_object.pk
                                    )
                            else:
                                # Copy regular fields
                                new_obj_data[field.name] = getattr(obj, field.name)

                        # Create the object in the target database
                        new_obj = model.objects.using(target_db).create(**new_obj_data)
                        # Store the mapping
                        object_mappings[model_name][obj.pk] = new_obj

            self.stdout.write("Successfully copied all Variant-related models.")

        except Exception as e:
            self.stdout.write(f"Error copying Variant data: {e}")

        self.stdout.write("Data copy for Variant-related models completed.")



def run():
    print("Starting migration script...")

    # Add your data migration logic here
    # For example:
    print("start")
    c = Command()
    c.handle()
    print("end")



