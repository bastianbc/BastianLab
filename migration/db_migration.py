from django.db import transaction
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group


class Command(BaseCommand):
    help = "Copy data for auth_user_groups from labdb to labdbproduction using names."

    def handle(self, *args, **kwargs):
        source_db = "labdb"  # Source database
        target_db = "default"  # Target database (labdbproduction)

        self.stdout.write("Starting data copy for auth_user_groups...")

        try:
            # Fetch all users and groups from the target database
            target_users = {user.username: user for user in User.objects.using(target_db).all()}
            target_groups = {group.name: group for group in Group.objects.using(target_db).all()}

            # Fetch all user-group relationships from the source database
            source_user_groups = User.groups.through.objects.using(source_db).all()

            with transaction.atomic(using=target_db):
                for user_group in source_user_groups:
                    # Get user and group names from the source database
                    source_user = User.objects.using(source_db).get(pk=user_group.user_id)
                    source_group = Group.objects.using(source_db).get(pk=user_group.group_id)

                    # Map source user and group names to target database objects
                    target_user = target_users.get(source_user.username)
                    target_group = target_groups.get(source_group.name)

                    if not target_user or not target_group:
                        self.stdout.write(
                            f"Skipping: User '{source_user.username}' or Group '{source_group.name}' not found in target database."
                        )
                        continue

                    # Check if the relationship already exists in the target database
                    if User.groups.through.objects.using(target_db).filter(
                        user=target_user, group=target_group
                    ).exists():
                        continue

                    # Create the relationship in the target database
                    User.groups.through.objects.using(target_db).create(
                        user=target_user, group=target_group
                    )

            self.stdout.write(
                f"Successfully copied {len(source_user_groups)} relationships from {source_db} to {target_db}."
            )

        except Exception as e:
            self.stdout.write(f"Error copying auth_user_groups: {e}")

        self.stdout.write("Data copy for auth_user_groups completed.")


def run():
    print("Starting migration script...")

    # Add your data migration logic here
    # For example:
    print("start")
    c = Command()
    c.handle()
    print("end")



