from django.db.migrations.recorder import MigrationRecorder
from django.db import connection
from django.apps import apps
from django.db.migrations.loader import MigrationLoader

def check_migration_status(app_label):
    print(f"\n🔍 Checking migration status for app: '{app_label}'\n")

    loader = MigrationLoader(connection)
    graph = loader.graph

    # All migration names (in code)
    all_migrations = loader.disk_migrations
    app_migrations = [key for key in all_migrations if key[0] == app_label]

    # Applied migrations (in DB)
    recorder = MigrationRecorder(connection)
    applied = recorder.applied_migrations()
    
    for (app, name) in sorted(app_migrations, key=lambda x: x[1]):
        status = "✅ APPLIED" if (app, name) in applied else "❌ NOT APPLIED"
        print(f" - {name.ljust(30)} {status}")

    print("\n👉 Suggestion: Use --fake only for migrations already reflected in the DB schema but not marked as applied.")

# Example usage:
# check_migration_status("your_app_name")
