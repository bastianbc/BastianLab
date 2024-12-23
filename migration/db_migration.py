from django.db import transaction
from django.core.management.base import BaseCommand
from django.apps import apps


class Command(BaseCommand):
    help = "Copy Projects data from labdb to labdbproduction."

    def handle(self, *args, **kwargs):
        source_db = "labdb"  # Source database
        target_db = "default"  # Target database (labdbproduction)

        self.stdout.write("Starting data copy for Projects...")

        try:
            # Get the Projects and related models
            SourceProject = apps.get_model("projects", "Projects")
            TargetProject = apps.get_model("projects", "Project")
            User = apps.get_model("auth", "User")
            Block = apps.get_model("blocks", "Block")

            # Fetch all projects from the source database
            source_projects = SourceProject.objects.using(source_db).all()

            # Map for tracking Many-to-Many relationships
            user_mapping = {user.pk: user for user in User.objects.using(target_db).all()}
            block_mapping = {block.pk: block for block in Block.objects.using(target_db).all()}

            with transaction.atomic(using=target_db):
                for project in source_projects:
                    # Check if the project already exists in the target database using `abbreviation`
                    try:
                        target_project = TargetProject.objects.using(target_db).get(
                            abbreviation=project.abbreviation
                        )
                        self.stdout.write(f"Project {project.name} already exists, skipping.")
                        continue
                    except TargetProject.DoesNotExist:
                        # Create the project in the target database
                        target_project = TargetProject.objects.using(target_db).create(
                            name=project.name,
                            abbreviation=project.abbreviation,
                            pi=project.pi,
                            speedtype=project.speedtype,
                            description=project.description,
                            date_start=project.date_start,
                            date=project.date,
                        )

                    # Add Many-to-Many relationships
                    # Add Technicians
                    for technician in project.technician.all():
                        target_technician = user_mapping.get(technician.pk)
                        if target_technician:
                            target_project.technician.add(target_technician)

                    # Add Researchers
                    for researcher in project.researcher.all():
                        target_researcher = user_mapping.get(researcher.pk)
                        if target_researcher:
                            target_project.researcher.add(target_researcher)

                    # Add Blocks
                    for block in project.blocks.all():
                        target_block = block_mapping.get(block.pk)
                        if target_block:
                            target_project.blocks.add(target_block)

            self.stdout.write(
                f"Successfully copied {len(source_projects)} Projects from {source_db} to {target_db}."
            )

        except Exception as e:
            self.stdout.write(f"Error copying Projects data: {e}")

        self.stdout.write("Data copy for Projects completed.")




def run():
    print("Starting migration script...")

    # Add your data migration logic here
    # For example:
    print("start")
    c = Command()
    c.handle()
    print("end")



