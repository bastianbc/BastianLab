from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os

class CustomFileSystemStorage(FileSystemStorage):
    def __init__(self, *args, **kwargs):
        # Default directory to store files
        kwargs['location'] = settings.SEQUENCING_FILES_SOURCE_DIRECTORY
        # prevent any chmod() calls
        kwargs['file_permissions_mode'] = None
        kwargs['directory_permissions_mode'] = None
        super(CustomFileSystemStorage, self).__init__(*args, **kwargs)

    def get_available_name(self, name, max_length=None):
        # Override to prevent name collision
        if self.exists(name):
            name = self.get_alternative_name(name)
        return super(CustomFileSystemStorage, self).get_available_name(name, max_length)

    def get_alternative_name(self, name):
        # Generate a unique name for the file if it already exists
        base, ext = os.path.splitext(name)
        counter = 1
        new_name = f"{base}_{counter}{ext}"
        while self.exists(new_name):
            counter += 1
            new_name = f"{base}_{counter}{ext}"
        return new_name


# Custom storage to write files under SEQUENCING_FILES_SOURCE_DIRECTORY
def analysis_run_upload_to(instance, filename):
    # Saves to: <SEQUENCING_FILES_SOURCE_DIRECTORY>/<run_name>/<filename>
    return f"sequencingdata/ProcessedData/{instance.name}_{instance.pipeline}_{instance.genome}/{filename}"


def cns_upload_to(instance, filename):
    # Organize attachments under a consistent structure
    return f"uploads/cns_attachments/{instance.sample_lib_id or 'unknown'}/{filename}"
