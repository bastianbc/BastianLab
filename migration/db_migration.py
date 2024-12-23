from django.db import transaction
from django.core.management.base import BaseCommand
from django.apps import apps


class Command(BaseCommand):
    help = "Copy Patient data from labdb to labdbproduction."

    def handle(self, *args, **kwargs):
        source_db = "labdb"  # Source database
        target_db = "default"  # Target database (labdbproduction)

        self.stdout.write("Starting data copy for Patient...")

        try:
            # Get the Patient model
            SourcePatient = apps.get_model("lab", "Patient")  # Source model
            TargetPatient = apps.get_model("lab", "Patient")  # Target model (with auto-generated ID)

            # Fetch all Patient objects from the source database
            source_patients = SourcePatient.objects.using(source_db).all()

            with transaction.atomic(using=target_db):
                for patient in source_patients:
                    # Check if the Patient already exists in the target database using pat_id
                    if TargetPatient.objects.using(target_db).filter(pat_id=patient.pat_id).exists():
                        self.stdout.write(f"Patient {patient.pat_id} already exists, skipping.")
                        continue

                    # Create the Patient in the target database
                    TargetPatient.objects.using(target_db).create(
                        pat_id=patient.pat_id,  # Unique identifier
                        sex=patient.sex,
                        consent=patient.consent,
                        dob=patient.dob,
                        race=patient.race,
                        source=patient.source,
                        blocks_temp=patient.blocks_temp,
                        notes=patient.notes,
                        pat_ip_id=patient.pat_ip_id,
                        date_added=patient.date_added,
                    )

            self.stdout.write(
                f"Successfully copied {len(source_patients)} Patients from {source_db} to {target_db}."
            )

        except Exception as e:
            self.stdout.write(f"Error copying Patient data: {e}")

        self.stdout.write("Data copy for Patient completed.")


def run():
    print("Starting migration script...")

    # Add your data migration logic here
    # For example:
    print("start")
    c = Command()
    c.handle()
    print("end")



