from django.db import connections, transaction
from django.core.management.base import BaseCommand
from django.apps import apps


class Command(BaseCommand):
    help = "Import Blocks using a custom SQL query."

    def handle(self, *args, **kwargs):
        source_db = "labdb"  # Source database
        target_db = "default"  # Target database

        self.stdout.write("Starting data import for Blocks...")

        try:
            # Get the models
            Block = apps.get_model("blocks", "Block")
            Patient = apps.get_model("lab", "Patient")
            Body = apps.get_model("body", "Body")
            Project = apps.get_model("projects", "Project")

            # Open a connection to the source database
            with connections[source_db].cursor() as cursor:
                # Execute the custom query
                cursor.execute("""
                    SELECT b.*, bd.name AS body, p.name AS project, pa.pat_id AS patient
                    FROM BLOCKS b
                    LEFT JOIN body bd ON bd.id = b.body_site_id
                    LEFT JOIN projects p ON p.pr_id = b.project_id
                    LEFT JOIN patients pa ON pa.pa_id = b.patient
                """)
                rows = cursor.fetchall()

                # Get column names
                columns = [col[0] for col in cursor.description]

            with transaction.atomic(using=target_db):
                for row in rows:
                    block_data = dict(zip(columns, row))

                    # Get or create related objects
                    patient = None
                    if block_data["patient"]:
                        patient = Patient.objects.using(target_db).filter(pat_id=block_data["patient"]).first()

                    body = None
                    if block_data["body"]:
                        body = Body.objects.using(target_db).filter(name=block_data["body"]).first()

                    project = None
                    if block_data["project"]:
                        project = Project.objects.using(target_db).filter(name=block_data["project"]).first()

                    # Check if the block already exists
                    if Block.objects.using(target_db).filter(name=block_data["name"]).exists():
                        self.stdout.write(f"Block {block_data['name']} already exists, skipping.")
                        continue

                    # Create the Block object
                    block = Block.objects.using(target_db).create(
                        name=block_data["name"],
                        patient=patient,
                        body_site=body,
                        age=block_data.get("age"),
                        ulceration=block_data.get("ulceration"),
                        thickness=block_data.get("thickness"),
                        mitoses=block_data.get("mitoses"),
                        p_stage=block_data.get("p_stage"),
                        prim=block_data.get("prim"),
                        subtype=block_data.get("subtype"),
                        slides=block_data.get("slides"),
                        slides_left=block_data.get("slides_left"),
                        fixation=block_data.get("fixation"),
                        storage=block_data.get("storage"),
                        scan_number=block_data.get("scan_number"),
                        icd10=block_data.get("icd10"),
                        diagnosis=block_data.get("diagnosis"),
                        notes=block_data.get("notes"),
                        micro=block_data.get("micro"),
                        gross=block_data.get("gross"),
                        clinical=block_data.get("clinical"),
                        date_added=block_data.get("date_added"),
                        old_body_site=block_data.get("old_body_site"),
                        path_note=block_data.get("path_note"),
                        ip_dx=block_data.get("ip_dx"),
                    )

                    # Associate the block with the project (Many-to-Many relationship)
                    if project:
                        block.block_projects.add(project)

            self.stdout.write("Successfully imported Blocks.")

        except Exception as e:
            self.stdout.write(f"Error importing Blocks: {e}")

        self.stdout.write("Data import for Blocks completed.")



def run():
    print("Starting migration script...")

    # Add your data migration logic here
    # For example:
    print("start")
    c = Command()
    c.handle()
    print("end")



