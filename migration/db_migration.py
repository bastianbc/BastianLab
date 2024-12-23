from django.db import connections, transaction
from django.core.management.base import BaseCommand
from django.apps import apps


class Command(BaseCommand):
    help = "Copy SequencingRun data from labdb to labdbproduction using Django ORM."

    def handle(self, *args, **kwargs):
        source_db = "labdb"  # Source database
        target_db = "default"  # Target database

        self.stdout.write("Starting data copy for SequencingRun...")

        # Get the models
        SequencingRun = apps.get_model("sequencingrun", "SequencingRun")
        SequencingLib = apps.get_model("sequencinglib", "SequencingLib")

        # Fetch SequencingRuns from the source database
        sequencing_runs = SequencingRun.objects.using(source_db).all()

        with transaction.atomic(using=target_db):
            for seq_run in sequencing_runs:
                # Check if the SequencingRun already exists
                existing_seq_run = SequencingRun.objects.using(target_db).filter(name=seq_run.name).first()
                if existing_seq_run:
                    self.stdout.write(f"SequencingRun {seq_run.name} already exists, skipping.")
                    continue

                # Create the SequencingRun object in the target database
                new_seq_run = SequencingRun.objects.using(target_db).create(
                    name=seq_run.name,
                    date_run=seq_run.date_run,
                    date=seq_run.date,
                    facility=seq_run.facility,
                    sequencer=seq_run.sequencer,
                    pe=seq_run.pe,
                    amp_cycles=seq_run.amp_cycles,
                    notes=seq_run.notes,
                )
                self.stdout.write(f"Created SequencingRun {seq_run.name}.")

                # Add SequencingLib relationships
                sequencing_libs = seq_run.sequencing_libs.using(source_db).all()
                for seq_lib in sequencing_libs:
                    target_seq_lib = SequencingLib.objects.using(target_db).filter(name=seq_lib.name).first()
                    if not target_seq_lib:
                        self.stdout.write(f"SequencingLib {seq_lib.name} not found, skipping relationship for SequencingRun {seq_run.name}.")
                        continue
                    new_seq_run.sequencing_libs.add(target_seq_lib)
                    self.stdout.write(f"Added SequencingLib {seq_lib.name} to SequencingRun {seq_run.name}.")

        self.stdout.write("Data copy for SequencingRun completed.")



def run():
    print("Starting migration script...")

    # Add your data migration logic here
    # For example:
    print("start")
    c = Command()
    c.handle()
    print("end")



