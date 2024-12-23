from django.db import connections, transaction
from django.core.management.base import BaseCommand
from django.apps import apps


class Command(BaseCommand):
    help = "Copy AnalysisRun data from labdb to labdbproduction using Django ORM."

    def handle(self, *args, **kwargs):
        source_db = "labdb"  # Source database
        target_db = "default"  # Target database

        self.stdout.write("Starting data copy for AnalysisRun...")

        # Get the models
        AnalysisRun = apps.get_model("analysisrun", "AnalysisRun")
        User = apps.get_model("auth", "User")

        # Fetch AnalysisRuns from the source database
        analysis_runs = AnalysisRun.objects.using(source_db).all()

        with transaction.atomic(using=target_db):
            for analysis_run in analysis_runs:
                # Check if the AnalysisRun already exists
                existing_analysis_run = AnalysisRun.objects.using(target_db).filter(name=analysis_run.name).first()
                if existing_analysis_run:
                    self.stdout.write(f"AnalysisRun {analysis_run.name} already exists, skipping.")
                    continue

                # Get the related User in the target database
                user = User.objects.using(target_db).filter(username=analysis_run.user.username).first()
                if not user:
                    self.stdout.write(f"User {analysis_run.user.username} not found, skipping AnalysisRun {analysis_run.name}.")
                    continue

                # Create the AnalysisRun object in the target database
                AnalysisRun.objects.using(target_db).create(
                    user=user,
                    name=analysis_run.name,
                    pipeline=analysis_run.pipeline,
                    genome=analysis_run.genome,
                    date=analysis_run.date,
                    sheet=analysis_run.sheet,
                    sheet_name=analysis_run.sheet_name,
                    status=analysis_run.status,
                )
                self.stdout.write(f"Created AnalysisRun {analysis_run.name}.")

        self.stdout.write("Data copy for AnalysisRun completed.")


def run():
    print("Starting migration script...")

    # Add your data migration logic here
    # For example:
    print("start")
    c = Command()
    c.handle()
    print("end")



