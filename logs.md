[2025-10-14T15:30:30.253Z] ✅ Configuration loaded successfully.
[2025-10-14T15:30:30.254Z] No Application Insights configuration found, using standard logging
[2025-10-14T15:30:30.432Z] Running replication direction: Primary → Secondary
[2025-10-14T15:30:30.432Z] Request URL: 'https://sbns-cu-dev-sos.servicebus.windows.net/$Resources/topics?$skip=REDACTED&$top=REDACTED&api-version=REDACTED'
Request method: 'GET'
Request headers:
    'Accept': 'application/xml, application/atom+xml'
    'x-ms-client-request-id': 'b781957e-a912-11f0-96fb-02ec101e00f4'
    'User-Agent': 'azsdk-python-servicebusmanagementclient/unknown Python/3.11.9 (Windows-10-10.0.22631-SP0)'     
    'Authorization': 'REDACTED'
No body was attached to the request
[2025-10-14T15:30:31.302Z] Response status: 200
Response headers:
    'Transfer-Encoding': 'chunked'
    'Content-Type': 'application/atom+xml;type=feed;charset=utf-8'
    'Server': 'Microsoft-HTTPAPI/2.0'
    'Date': 'Tue, 14 Oct 2025 15:30:31 GMT'
[2025-10-14T15:30:31.312Z] Found 1 topics: ['dte-notifications']
[2025-10-14T15:30:31.313Z] Request URL: 'https://sbns-cu-dev-sos.servicebus.windows.net/dte-notifications/subscriptions?$skip=REDACTED&$top=REDACTED&api-version=REDACTED'
Request method: 'GET'
Request headers:
    'Accept': 'application/xml, application/atom+xml'
    'x-ms-client-request-id': 'b82e3364-a912-11f0-b7e8-02ec101e00f4'
    'User-Agent': 'azsdk-python-servicebusmanagementclient/unknown Python/3.11.9 (Windows-10-10.0.22631-SP0)'     
    'Authorization': 'REDACTED'
No body was attached to the request
[2025-10-14T15:30:31.364Z] Response status: 200
Response headers:
    'Transfer-Encoding': 'chunked'
    'Content-Type': 'application/atom+xml;type=feed;charset=utf-8'
    'ETag': '638932217405900000'
    'Server': 'Microsoft-HTTPAPI/2.0'
    'Strict-Transport-Security': 'REDACTED'
    'Date': 'Tue, 14 Oct 2025 15:30:31 GMT'
[2025-10-14T15:30:31.626Z] Found 2 subscriptions for topic 'dte-notifications': ['email-notifications', 'sms-notifications']
[2025-10-14T15:30:31.718Z] Processing dte-notifications/email-notifications
[2025-10-14T15:30:31.719Z] ❌ Replication cron failed: process_subscription_messages() missing 4 required positional arguments: 'dest_conn', 'config', 'direction', and 'logger'
Traceback (most recent call last):
  File "C:\Users\u69819\Documents\DevOps\service_bus\personal\personal_projects\src\main.py", line 46, in main    
    process_subscription_messages(topic, sub, config)
TypeError: process_subscription_messages() missing 4 required positional arguments: 'dest_conn', 'config', 'direction', and 'logger'
[2025-10-14T15:30:31.827Z] Executed 'Functions.src' (Succeeded, Id=f185d2f9-c58a-4875-a9a0-92ab8d21b2b4, Duration=1768ms)