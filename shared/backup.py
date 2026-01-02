# Shared utilities

import shutil
import os

def duplicate_backup(source, dest1, dest2):
    shutil.copytree(source, dest1)
    shutil.copytree(source, dest2)

def independent_backup(source, service):
    # Placeholder for cloud backup
    pass