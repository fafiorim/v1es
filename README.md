# Migrating SmartFolders from a onprem DSM (Deep Security Manager) or from another Cloud One Workload Security tenant.

The script "List_smartfolders_with_PARENT_name_prefix.py" will create a CSV file (MigratedSmartFolders.csv) with all of the SmartFolders to be migrated.

The script "migrate_smartfolders_with_name_parent_prefix.py" will read the file MigratedSmartFolders.csv and create the SmartFolders in the new tenant, following up the preview structure of inheritance. As result you will have a CSV file (MigratedSmartFolders.csv) the migration status and if have error code and error detailed message.
