from django.db import connections, transaction
from django.core.management.base import BaseCommand
from django.apps import apps


class Command(BaseCommand):
    help = "Copy SequencingLib and CL_SEQL_LINK data from labdb to labdbproduction using Django ORM."

    def handle(self, *args, **kwargs):
        source_db = "labdb"  # Source database
        target_db = "default"  # Target database

        self.stdout.write("Starting data copy for SequencingLib and CL_SEQL_LINK...")

        # Get the models
        SequencingLib = apps.get_model("sequencinglib", "SequencingLib")
        CL_SEQL_LINK = apps.get_model("sequencinglib", "CL_SEQL_LINK")
        CapturedLib = apps.get_model("capturedlib", "CapturedLib")

        # Fetch SequencingLibs from the source database
        sequencing_libs = SequencingLib.objects.using(source_db).all()

        with transaction.atomic(using=target_db):
            for seq_lib in sequencing_libs:
                # Check if the SequencingLib already exists
                existing_seq_lib = SequencingLib.objects.using(target_db).filter(name=seq_lib.name).first()
                if existing_seq_lib:
                    self.stdout.write(f"SequencingLib {seq_lib.name} already exists, skipping.")
                    continue

                # Create the SequencingLib object in the target database
                SequencingLib.objects.using(target_db).create(
                    name=seq_lib.name,
                    date=seq_lib.date,
                    nmol=seq_lib.nmol,
                    target_vol=seq_lib.target_vol,
                    buffer=seq_lib.buffer,
                    pdf=seq_lib.pdf,
                    notes=seq_lib.notes,
                )
                self.stdout.write(f"Created SequencingLib {seq_lib.name}.")

        # Fetch CL_SEQL_LINK from the source database
        cl_seql_links = CL_SEQL_LINK.objects.using(source_db).all()

        with transaction.atomic(using=target_db):
            for link in cl_seql_links:
                # Get the related SequencingLib and CapturedLib in the target database
                sequencing_lib = SequencingLib.objects.using(target_db).filter(name=link.sequencing_lib.name).first()
                if not sequencing_lib:
                    self.stdout.write(f"SequencingLib {link.sequencing_lib.name} not found, skipping CL_SEQL_LINK.")
                    continue

                captured_lib = CapturedLib.objects.using(target_db).filter(name=link.captured_lib.name).first()
                if not captured_lib:
                    self.stdout.write(f"CapturedLib {link.captured_lib.name} not found, skipping CL_SEQL_LINK.")
                    continue

                # Check if the CL_SEQL_LINK already exists
                if CL_SEQL_LINK.objects.using(target_db).filter(sequencing_lib=sequencing_lib, captured_lib=captured_lib).exists():
                    self.stdout.write(f"CL_SEQL_LINK for SequencingLib {sequencing_lib.name} and CapturedLib {captured_lib.name} already exists, skipping.")
                    continue

                # Create the CL_SEQL_LINK object in the target database
                CL_SEQL_LINK.objects.using(target_db).create(
                    sequencing_lib=sequencing_lib,
                    captured_lib=captured_lib,
                    volume=link.volume,
                    date=link.date,
                )
                self.stdout.write(f"Created CL_SEQL_LINK for SequencingLib {sequencing_lib.name} and CapturedLib {captured_lib.name}.")

        self.stdout.write("Data copy for SequencingLib and CL_SEQL_LINK completed.")



def run():
    print("Starting migration script...")

    # Add your data migration logic here
    # For example:
    print("start")
    c = Command()
    c.handle()
    print("end")



