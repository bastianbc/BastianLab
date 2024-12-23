from django.db import connections, transaction
from django.core.management.base import BaseCommand
from django.apps import apps


class Command(BaseCommand):
    help = "Copy Patient data from labdb to labdbproduction using direct DB connection."

    def handle(self, *args, **kwargs):
        source_db = "labdb"  # Source database
        target_db = "default"  # Target database

        self.stdout.write("Starting data copy for Patient...")

        try:
            # Get the target Patient model
            Patient = apps.get_model("lab", "Patient")

            # Open a connection to the source database
            with connections[source_db].cursor() as source_cursor:
                # Fetch all data from the patients table
                source_cursor.execute("SELECT * FROM patients")
                rows = source_cursor.fetchall()

                # Fetch column names
                column_names = [col[0] for col in source_cursor.description]

            with transaction.atomic(using=target_db):
                for row in rows:
                    patient_data = dict(zip(column_names, row))

                    # Check if a patient with the same `pat_id` already exists in the target database
                    if Patient.objects.using(target_db).filter(pat_id=patient_data["pat_id"]).exists():
                        self.stdout.write(f"Patient {patient_data['pat_id']} already exists, skipping.")
                        continue

                    # Insert the patient into the target database
                    Patient.objects.using(target_db).create(
                        pat_id=patient_data["pat_id"],
                        sex=patient_data.get("sex"),
                        consent=patient_data.get("consent"),
                        dob=patient_data.get("dob"),
                        race=patient_data.get("race"),
                        source=patient_data.get("source"),
                        blocks_temp=patient_data.get("blocks_temp"),
                        notes=patient_data.get("notes"),
                        pat_ip_id=patient_data.get("pat_ip_id"),
                        date_added=patient_data.get("date_added"),
                    )

            self.stdout.write(f"Successfully copied {len(rows)} Patients from {source_db} to {target_db}.")

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



