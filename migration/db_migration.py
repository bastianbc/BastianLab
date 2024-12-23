from django.db import connections, transaction
from django.core.management.base import BaseCommand
from django.apps import apps


class Command(BaseCommand):
    help = "Copy Projects data from labdb to labdbproduction."

    def handle(self, *args, **kwargs):
        source_db = "labdb"  # Source database
        target_db = "default"  # Target database (labdbproduction)

        self.stdout.write("Starting data copy for Projects...")

        try:
            # Get the target Project model
            Project = apps.get_model("projects", "Project")
            User = apps.get_model("auth", "User")
            Block = apps.get_model("blocks", "Block")

            # Open a direct connection to the source database
            with connections[source_db].cursor() as cursor:
                # Fetch all projects from the source database
                cursor.execute("SELECT * FROM projects")
                source_projects = cursor.fetchall()

                # Fetch column names for mapping
                columns = [col[0] for col in cursor.description]

            # Mapping of source IDs to target objects for M2M relationships
            user_mapping = {user.pk: user for user in User.objects.using(target_db).all()}
            block_mapping = {block.pk: block for block in Block.objects.using(target_db).all()}

            with transaction.atomic(using=target_db):
                for row in source_projects:
                    project_data = dict(zip(columns, row))

                    # Check if the project already exists in the target database
                    try:
                        target_project = Project.objects.using(target_db).get(
                            abbreviation=project_data["abbreviation"]
                        )
                        self.stdout.write(f"Project {project_data['name']} already exists, skipping.")
                        continue
                    except Project.DoesNotExist:
                        # Create the project in the target database
                        target_project = Project.objects.using(target_db).create(
                            name=project_data["name"],
                            abbreviation=project_data["abbreviation"],
                            pi=project_data["pi"],
                            speedtype=project_data["speedtype"],
                            description=project_data["description"],
                            date_start=project_data["date_start"],
                            date=project_data["date"],
                        )

                    # Add Many-to-Many relationships for technician, researcher, and blocks
                    for technician_id in project_data.get("technician", []):
                        target_technician = user_mapping.get(technician_id)
                        if target_technician:
                            target_project.technician.add(target_technician)

                    for researcher_id in project_data.get("researcher", []):
                        target_researcher = user_mapping.get(researcher_id)
                        if target_researcher:
                            target_project.researcher.add(target_researcher)

                    for block_id in project_data.get("blocks", []):
                        target_block = block_mapping.get(block_id)
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



