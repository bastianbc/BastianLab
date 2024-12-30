from django.db import connections, transaction
from django.core.management.base import BaseCommand
from django.apps import apps


class Command(BaseCommand):
    help = "Copy SequencingFileSet and SequencingFile data from labdb to labdbproduction using Django ORM."

    def handle(self, *args, **kwargs):
        source_db = "labdb"  # Source database
        target_db = "default"  # Target database

        self.stdout.write("Starting data copy for SequencingFileSet and SequencingFile...")

        # Get the models
        SequencingFileSet = apps.get_model("sequencingfile", "SequencingFileSet")
        SequencingFile = apps.get_model("sequencingfile", "SequencingFile")
        SampleLib = apps.get_model("samplelib", "SampleLib")
        SequencingRun = apps.get_model("sequencingrun", "SequencingRun")

        # Fetch SequencingFileSets from the source database
        file_sets = SequencingFileSet.objects.using(source_db).all()

        with transaction.atomic(using=target_db):
            for file_set in file_sets:
                # Get related SampleLib and SequencingRun in the target database
                sample_lib = SampleLib.objects.using(target_db).filter(name=file_set.sample_lib.name).first() if file_set.sample_lib else None
                sequencing_run = SequencingRun.objects.using(target_db).filter(name=file_set.sequencing_run.name).first() if file_set.sequencing_run else None

                # Check if the SequencingFileSet already exists
                existing_file_set = SequencingFileSet.objects.using(target_db).filter(prefix=file_set.prefix).first()
                if existing_file_set:
                    self.stdout.write(f"SequencingFileSet {file_set.prefix} already exists, skipping.")
                    continue

                # Create the SequencingFileSet in the target database
                new_file_set = SequencingFileSet.objects.using(target_db).create(
                    sample_lib=sample_lib,
                    sequencing_run=sequencing_run,
                    prefix=file_set.prefix,
                    path=file_set.path,
                    date_added=file_set.date_added,
                )
                self.stdout.write(f"Created SequencingFileSet {file_set.prefix}.")

                # Copy related SequencingFiles
                sequencing_files = SequencingFile.objects.using(source_db).filter(sequencing_file_set=file_set)
                for sequencing_file in sequencing_files:
                    # Check if the SequencingFile already exists
                    existing_file = SequencingFile.objects.using(target_db).filter(name=sequencing_file.name).first()
                    if existing_file:
                        self.stdout.write(f"SequencingFile {sequencing_file.name} already exists, skipping.")
                        continue

                    # Create the SequencingFile in the target database
                    SequencingFile.objects.using(target_db).create(
                        sequencing_file_set=new_file_set,
                        name=sequencing_file.name,
                        checksum=sequencing_file.checksum,
                        type=sequencing_file.type,
                        date_added=sequencing_file.date_added,
                    )
                    self.stdout.write(f"Created SequencingFile {sequencing_file.name} for SequencingFileSet {file_set.prefix}.")

        self.stdout.write("Data copy for SequencingFileSet and SequencingFile completed.")


def run():
    print("Starting migration script...")

    # Add your data migration logic here
    # For example:
    print("start")
    c = Command()
    c.handle()
    print("end")



