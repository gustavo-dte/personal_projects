[2025-10-14T15:50:31.526Z] ✅ Configuration loaded successfully.
[2025-10-14T15:50:31.528Z] No Application Insights configuration found, using standard logging
[2025-10-14T15:50:31.822Z] Running replication direction: Primary → Secondary
[2025-10-14T15:50:32.166Z] Request URL: 'https://sbns-cu-dev-sos.servicebus.windows.net/$Resources/topics?$skip=REDACTED&$top=REDACTED&api-version=REDACTED'
Request method: 'GET'
Request headers:
    'Accept': 'application/xml, application/atom+xml'
    'x-ms-client-request-id': '82ab035f-a915-11f0-904a-02ec101e00f4'
    'User-Agent': 'azsdk-python-servicebusmanagementclient/unknown Python/3.11.9 (Windows-10-10.0.22631-SP0)'     
    'Authorization': 'REDACTED'
No body was attached to the request
[2025-10-14T15:50:32.215Z] Response status: 200
Response headers:
    'Transfer-Encoding': 'chunked'
    'Content-Type': 'application/atom+xml;type=feed;charset=utf-8'
    'Server': 'Microsoft-HTTPAPI/2.0'
    'Date': 'Tue, 14 Oct 2025 15:50:30 GMT'
[2025-10-14T15:50:32.216Z] Found 1 topics: ['dte-notifications']
[2025-10-14T15:50:32.217Z] Request URL: 'https://sbns-cu-dev-sos.servicebus.windows.net/dte-notifications/subscriptions?$skip=REDACTED&$top=REDACTED&api-version=REDACTED'
Request method: 'GET'
Request headers:
    'Accept': 'application/xml, application/atom+xml'
    'x-ms-client-request-id': '834c2997-a915-11f0-a318-02ec101e00f4'
    'User-Agent': 'azsdk-python-servicebusmanagementclient/unknown Python/3.11.9 (Windows-10-10.0.22631-SP0)'     
    'Authorization': 'REDACTED'
No body was attached to the request
[2025-10-14T15:50:32.528Z] Response status: 200
Response headers:
    'Transfer-Encoding': 'chunked'
    'Content-Type': 'application/atom+xml;type=feed;charset=utf-8'
    'ETag': '638932217405900000'
    'Server': 'Microsoft-HTTPAPI/2.0'
    'Strict-Transport-Security': 'REDACTED'
    'Date': 'Tue, 14 Oct 2025 15:50:30 GMT'
[2025-10-14T15:50:32.530Z] Found 2 subscriptions for topic 'dte-notifications': ['email-notifications', 'sms-notifications']
[2025-10-14T15:50:32.531Z] Processing dte-notifications/email-notifications
[2025-10-14T15:50:32.531Z] Connection state changed: None -> <ConnectionState.START: 0>
[2025-10-14T15:50:32.539Z] Connection state changed: <ConnectionState.START: 0> -> <ConnectionState.HDR_SENT: 2>
[2025-10-14T15:50:32.540Z] Connection state changed: <ConnectionState.HDR_SENT: 2> -> <ConnectionState.HDR_SENT: 2>
[2025-10-14T15:50:32.542Z] Connection state changed: <ConnectionState.HDR_SENT: 2> -> <ConnectionState.OPEN_PIPE: 4>
[2025-10-14T15:50:32.543Z] Session state changed: <SessionState.UNMAPPED: 0> -> <SessionState.BEGIN_SENT: 1>      
[2025-10-14T15:50:32.543Z] Link state changed: <LinkState.DETACHED: 0> -> <LinkState.ATTACH_SENT: 1>
[2025-10-14T15:50:32.544Z] Management link receiver state changed: <LinkState.DETACHED: 0> -> <LinkState.ATTACH_SENT: 1>
[2025-10-14T15:50:32.545Z] Link state changed: <LinkState.DETACHED: 0> -> <LinkState.ATTACH_SENT: 1>
[2025-10-14T15:50:32.546Z] Management link sender state changed: <LinkState.DETACHED: 0> -> <LinkState.ATTACH_SENT: 1>
[2025-10-14T15:50:32.546Z] Connection state changed: <ConnectionState.OPEN_PIPE: 4> -> <ConnectionState.OPEN_SENT: 7>
[2025-10-14T15:50:32.549Z] Connection state changed: <ConnectionState.OPEN_SENT: 7> -> <ConnectionState.OPENED: 9>
[2025-10-14T15:50:32.550Z] Session state changed: <SessionState.BEGIN_SENT: 1> -> <SessionState.MAPPED: 3>        
[2025-10-14T15:50:32.550Z] Link state changed: <LinkState.ATTACH_SENT: 1> -> <LinkState.ATTACHED: 3>
[2025-10-14T15:50:32.551Z] Management link receiver state changed: <LinkState.ATTACH_SENT: 1> -> <LinkState.ATTACHED: 3>
[2025-10-14T15:50:32.645Z] Link state changed: <LinkState.ATTACH_SENT: 1> -> <LinkState.ATTACHED: 3>
[2025-10-14T15:50:32.645Z] Management link sender state changed: <LinkState.ATTACH_SENT: 1> -> <LinkState.ATTACHED: 3>
[2025-10-14T15:50:33.145Z] Link state changed: <LinkState.DETACHED: 0> -> <LinkState.ATTACH_SENT: 1>
[2025-10-14T15:50:33.247Z] Link state changed: <LinkState.ATTACH_SENT: 1> -> <LinkState.ATTACHED: 3>
[2025-10-14T15:50:38.403Z] No new messages for dte-notifications/email-notifications
[2025-10-14T15:50:38.404Z] Link state changed: <LinkState.ATTACHED: 3> -> <LinkState.DETACH_SENT: 4>
[2025-10-14T15:50:38.405Z] Link state changed: <LinkState.ATTACHED: 3> -> <LinkState.DETACH_SENT: 4>
[2025-10-14T15:50:38.406Z] Management link receiver state changed: <LinkState.ATTACHED: 3> -> <LinkState.DETACH_SENT: 4>
[2025-10-14T15:50:38.406Z] Link state changed: <LinkState.ATTACHED: 3> -> <LinkState.DETACH_SENT: 4>
[2025-10-14T15:50:38.407Z] Management link sender state changed: <LinkState.ATTACHED: 3> -> <LinkState.DETACH_SENT: 4>
[2025-10-14T15:50:38.408Z] Session state changed: <SessionState.MAPPED: 3> -> <SessionState.END_SENT: 4>
[2025-10-14T15:50:38.519Z] Connection state changed: <ConnectionState.OPENED: 9> -> <ConnectionState.CLOSE_SENT: 11>
[2025-10-14T15:50:38.651Z] Connection state changed: <ConnectionState.CLOSE_SENT: 11> -> <ConnectionState.END: 13>
[2025-10-14T15:50:38.652Z] Session state changed: <SessionState.END_SENT: 4> -> <SessionState.DISCARDING: 6>      
[2025-10-14T15:50:38.653Z] Link state changed: <LinkState.DETACH_SENT: 4> -> <LinkState.DETACHED: 0>
[2025-10-14T15:50:38.654Z] Management link sender state changed: <LinkState.DETACH_SENT: 4> -> <LinkState.DETACHED: 0>
[2025-10-14T15:50:38.654Z] Link state changed: <LinkState.DETACH_SENT: 4> -> <LinkState.DETACHED: 0>
[2025-10-14T15:50:38.815Z] Management link receiver state changed: <LinkState.DETACH_SENT: 4> -> <LinkState.DETACHED: 0>
[2025-10-14T15:50:38.821Z] Link state changed: <LinkState.DETACH_SENT: 4> -> <LinkState.DETACHED: 0>
[2025-10-14T15:50:38.827Z] Processing dte-notifications/sms-notifications
[2025-10-14T15:50:39.582Z] Connection state changed: None -> <ConnectionState.START: 0>
[2025-10-14T15:50:39.675Z] Connection state changed: <ConnectionState.START: 0> -> <ConnectionState.HDR_SENT: 2>
[2025-10-14T15:50:39.747Z] Connection state changed: <ConnectionState.HDR_SENT: 2> -> <ConnectionState.HDR_SENT: 2>
[2025-10-14T15:50:39.748Z] Connection state changed: <ConnectionState.HDR_SENT: 2> -> <ConnectionState.OPEN_PIPE: 4>
[2025-10-14T15:50:39.749Z] Session state changed: <SessionState.UNMAPPED: 0> -> <SessionState.BEGIN_SENT: 1>      
[2025-10-14T15:50:39.750Z] Link state changed: <LinkState.DETACHED: 0> -> <LinkState.ATTACH_SENT: 1>
[2025-10-14T15:50:39.750Z] Management link receiver state changed: <LinkState.DETACHED: 0> -> <LinkState.ATTACH_SENT: 1>
[2025-10-14T15:50:39.751Z] Link state changed: <LinkState.DETACHED: 0> -> <LinkState.ATTACH_SENT: 1>
[2025-10-14T15:50:39.753Z] Management link sender state changed: <LinkState.DETACHED: 0> -> <LinkState.ATTACH_SENT: 1>
[2025-10-14T15:50:39.887Z] Connection state changed: <ConnectionState.OPEN_PIPE: 4> -> <ConnectionState.OPEN_SENT: 7>
[2025-10-14T15:50:39.888Z] Connection state changed: <ConnectionState.OPEN_SENT: 7> -> <ConnectionState.OPENED: 9>
[2025-10-14T15:50:39.888Z] Session state changed: <SessionState.BEGIN_SENT: 1> -> <SessionState.MAPPED: 3>        
[2025-10-14T15:50:40.074Z] Link state changed: <LinkState.ATTACH_SENT: 1> -> <LinkState.ATTACHED: 3>
[2025-10-14T15:50:40.076Z] Management link receiver state changed: <LinkState.ATTACH_SENT: 1> -> <LinkState.ATTACHED: 3>
[2025-10-14T15:50:40.182Z] Link state changed: <LinkState.ATTACH_SENT: 1> -> <LinkState.ATTACHED: 3>
[2025-10-14T15:50:40.183Z] Management link sender state changed: <LinkState.ATTACH_SENT: 1> -> <LinkState.ATTACHED: 3>
[2025-10-14T15:50:40.415Z] Link state changed: <LinkState.DETACHED: 0> -> <LinkState.ATTACH_SENT: 1>
[2025-10-14T15:50:40.487Z] Link state changed: <LinkState.ATTACH_SENT: 1> -> <LinkState.ATTACHED: 3>
[2025-10-14T15:50:45.711Z] No new messages for dte-notifications/sms-notifications
[2025-10-14T15:50:45.712Z] Link state changed: <LinkState.ATTACHED: 3> -> <LinkState.DETACH_SENT: 4>
[2025-10-14T15:50:45.714Z] Link state changed: <LinkState.ATTACHED: 3> -> <LinkState.DETACH_SENT: 4>
[2025-10-14T15:50:45.714Z] Management link sender state changed: <LinkState.ATTACHED: 3> -> <LinkState.DETACH_SENT: 4>
[2025-10-14T15:50:45.715Z] Session state changed: <SessionState.MAPPED: 3> -> <SessionState.END_SENT: 4>
[2025-10-14T15:50:45.716Z] Connection state changed: <ConnectionState.OPENED: 9> -> <ConnectionState.CLOSE_SENT: 11>
[2025-10-14T15:50:45.717Z] Connection state changed: <ConnectionState.CLOSE_SENT: 11> -> <ConnectionState.END: 13>[2025-10-14T15:50:45.783Z] Session state changed: <SessionState.END_SENT: 4> -> <SessionState.DISCARDING: 6>      
[2025-10-14T15:50:45.908Z] Link state changed: <LinkState.DETACH_SENT: 4> -> <LinkState.DETACHED: 0>
[2025-10-14T15:50:45.908Z] Management link sender state changed: <LinkState.DETACH_SENT: 4> -> <LinkState.DETACHED: 0>
[2025-10-14T15:50:45.913Z] Link state changed: <LinkState.DETACH_SENT: 4> -> <LinkState.DETACHED: 0>
[2025-10-14T15:50:45.915Z] Management link receiver state changed: <LinkState.DETACH_SENT: 4> -> <LinkState.DETACHED: 0>
[2025-10-14T15:50:45.916Z] Link state changed: <LinkState.DETACH_SENT: 4> -> <LinkState.DETACHED: 0>
[2025-10-14T15:50:46.313Z] ✅ Replication cycle completed successfully.