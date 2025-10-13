[2025-10-13T20:20:00.294Z] Replication cron failed: 'ServiceBusClient' object has no attribute '_management_client'
Traceback (most recent call last):
  File "C:\Users\u69819\Documents\DevOps\service_bus\personal\personal_projects\src\main.py", line 430, in main
    topics = [t.name for t in client._management_client.list_topics()]  # or via mgmt API
AttributeError: 'ServiceBusClient' object has no attribute '_management_client'