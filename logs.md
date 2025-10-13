[2025-10-13T19:20:02.816Z] Unexpected configuration error
[2025-10-13T19:20:02.817Z] Replication cron failed: Unexpected error loading configuration: Missing required environment variables for primary_to_secondary: SECONDARY_TOPIC_NAME
Traceback (most recent call last):
  File "C:\Users\u69819\Documents\DevOps\service_bus\personal_projects\src\main.py", line 72, in load_and_validate_config
    config = ReplicationConfig()
  File "C:\Users\u69819\Documents\DevOps\service_bus\personal_projects\.venv\Lib\site-packages\pydantic_settings\main.py", line 193, in __init__
    super().__init__(
  File "C:\Users\u69819\Documents\DevOps\service_bus\personal_projects\.venv\Lib\site-packages\pydantic\main.py", line 250, in __init__
    validated_self = self.__pydantic_validator__.validate_python(data, self_instance=self)
  File "C:\Users\u69819\Documents\DevOps\service_bus\personal_projects\src\config.py", line 187, in validate_connection_config
    raise ConfigError(
__app__.src.exceptions.ConfigError: Missing required environment variables for primary_to_secondary: SECONDARY_TOPIC_NAME

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "C:\Users\u69819\Documents\DevOps\service_bus\personal_projects\src\main.py", line 424, in main
    config = load_and_validate_config()
  File "C:\Users\u69819\Documents\DevOps\service_bus\personal_projects\src\main.py", line 104, in load_and_validate_config
    raise ConfigError(error_message) from unexpected_error
__app__.src.exceptions.ConfigError: Unexpected error loading configuration: Missing required environment variables for primary_to_secondary: SECONDARY_TOPIC_NAME     
[2025-10-13T19:20:02.872Z] Executed 'Functions.src' (Succeeded, Id=4fc4c98f-0d48-4194-a43f-8afe43f7b32c, Duration=2795ms)
[2025-10-13T19:20:15.092Z] Stopping host...
[2025-10-13T19:20:15.515Z] Stopping JobHost
[2025-10-13T19:20:15.520Z] Stopping the listener 'Microsoft.Azure.WebJobs.Host.Listeners.SingletonListener' for function 'src'
[2025-10-13T19:20:15.603Z] Stopped the listener 'Microsoft.Azure.WebJobs.Host.Listeners.SingletonListener' for function 'src'
[2025-10-13T19:20:15.615Z] Job host stopped
[2025-10-13T19:20:15.962Z] Host shutdown completed.
[2025-10-13T19:20:16.037Z] Shutting down language wo