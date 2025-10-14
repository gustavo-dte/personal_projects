[2025-10-14T15:20:00.217Z] ✅ Configuration loaded successfully.
[2025-10-14T15:20:00.218Z] No Application Insights configuration found, using standard logging
[2025-10-14T15:20:00.219Z] Running replication direction: Primary → Secondary
[2025-10-14T15:20:00.219Z] Request URL: 'https://sbns-cu-dev-sos.servicebus.windows.net/$Resources/topics?$skip=REDACTED&$top=REDACTED&api-version=REDACTED'
Request method: 'GET'
Request headers:
    'Accept': 'application/xml, application/atom+xml'
    'x-ms-client-request-id': '3fe751a8-a911-11f0-9f2e-02ec101e00f4'
    'User-Agent': 'azsdk-python-servicebusmanagementclient/unknown Python/3.11.9 (Windows-10-10.0.22631-SP0)'     
    'Authorization': 'REDACTED'
No body was attached to the request
[2025-10-14T15:20:01.862Z] Response status: 200
Response headers:
    'Transfer-Encoding': 'chunked'
    'Content-Type': 'application/atom+xml;type=feed;charset=utf-8'
    'Server': 'Microsoft-HTTPAPI/2.0'
    'Date': 'Tue, 14 Oct 2025 15:20:01 GMT'
[2025-10-14T15:20:01.864Z] Found 1 topics: ['dte-notifications']
[2025-10-14T15:20:01.865Z] Request URL: 'https://sbns-cu-dev-sos.servicebus.windows.net/dte-notifications/subscriptions?$skip=REDACTED&$top=REDACTED&api-version=REDACTED'
Request method: 'GET'
Request headers:
    'Accept': 'application/xml, application/atom+xml'
    'x-ms-client-request-id': '410130f6-a911-11f0-8a83-02ec101e00f4'
    'User-Agent': 'azsdk-python-servicebusmanagementclient/unknown Python/3.11.9 (Windows-10-10.0.22631-SP0)'     
    'Authorization': 'REDACTED'
No body was attached to the request
[2025-10-14T15:20:01.904Z] Response status: 200
Response headers:
    'Transfer-Encoding': 'chunked'
    'Content-Type': 'application/atom+xml;type=feed;charset=utf-8'
    'ETag': '638932217405900000'
    'Server': 'Microsoft-HTTPAPI/2.0'
    'Strict-Transport-Security': 'REDACTED'
    'Date': 'Tue, 14 Oct 2025 15:20:01 GMT'
[2025-10-14T15:20:01.905Z] Found 2 subscriptions for topic 'dte-notifications': ['email-notifications', 'sms-notifications']
[2025-10-14T15:20:01.906Z] Processing dte-notifications/email-notifications
[2025-10-14T15:20:02.795Z] Connection state changed: None -> <ConnectionState.START: 0>
[2025-10-14T15:20:02.796Z] Connection state changed: <ConnectionState.START: 0> -> <ConnectionState.HDR_SENT: 2>  
[2025-10-14T15:20:02.797Z] Connection state changed: <ConnectionState.HDR_SENT: 2> -> <ConnectionState.HDR_SENT: 2>
[2025-10-14T15:20:02.798Z] Connection state changed: <ConnectionState.HDR_SENT: 2> -> <ConnectionState.OPEN_PIPE: 4>
[2025-10-14T15:20:02.798Z] Session state changed: <SessionState.UNMAPPED: 0> -> <SessionState.BEGIN_SENT: 1>      
[2025-10-14T15:20:02.799Z] Link state changed: <LinkState.DETACHED: 0> -> <LinkState.ATTACH_SENT: 1>
[2025-10-14T15:20:02.799Z] Management link receiver state changed: <LinkState.DETACHED: 0> -> <LinkState.ATTACH_SENT: 1>
[2025-10-14T15:20:02.800Z] Link state changed: <LinkState.DETACHED: 0> -> <LinkState.ATTACH_SENT: 1>
[2025-10-14T15:20:02.800Z] Management link sender state changed: <LinkState.DETACHED: 0> -> <LinkState.ATTACH_SENT: 1>
[2025-10-14T15:20:02.805Z] Connection state changed: <ConnectionState.OPEN_PIPE: 4> -> <ConnectionState.OPEN_SENT: 7>
[2025-10-14T15:20:02.958Z] Connection state changed: <ConnectionState.OPEN_SENT: 7> -> <ConnectionState.OPENED: 9>
[2025-10-14T15:20:03.003Z] Session state changed: <SessionState.BEGIN_SENT: 1> -> <SessionState.MAPPED: 3>        
[2025-10-14T15:20:03.096Z] Link state changed: <LinkState.ATTACH_SENT: 1> -> <LinkState.ATTACHED: 3>
[2025-10-14T15:20:03.112Z] Management link receiver state changed: <LinkState.ATTACH_SENT: 1> -> <LinkState.ATTACHED: 3>
[2025-10-14T15:20:03.146Z] Link state changed: <LinkState.ATTACH_SENT: 1> -> <LinkState.ATTACHED: 3>
[2025-10-14T15:20:03.150Z] Management link sender state changed: <LinkState.ATTACH_SENT: 1> -> <LinkState.ATTACHED: 3>
[2025-10-14T15:20:03.587Z] Link state changed: <LinkState.DETACHED: 0> -> <LinkState.ATTACH_SENT: 1>
[2025-10-14T15:20:03.619Z] Link state changed: <LinkState.ATTACH_SENT: 1> -> <LinkState.ATTACHED: 3>
[2025-10-14T15:20:08.805Z] No new messages for dte-notifications/email-notifications
[2025-10-14T15:20:08.809Z] Link state changed: <LinkState.ATTACHED: 3> -> <LinkState.DETACH_SENT: 4>
[2025-10-14T15:20:08.810Z] Link state changed: <LinkState.ATTACHED: 3> -> <LinkState.DETACH_SENT: 4>
[2025-10-14T15:20:08.811Z] Management link receiver state changed: <LinkState.ATTACHED: 3> -> <LinkState.DETACH_SENT: 4>
[2025-10-14T15:20:08.811Z] Link state changed: <LinkState.ATTACHED: 3> -> <LinkState.DETACH_SENT: 4>
[2025-10-14T15:20:08.812Z] Management link sender state changed: <LinkState.ATTACHED: 3> -> <LinkState.DETACH_SENT: 4>
[2025-10-14T15:20:08.813Z] Session state changed: <SessionState.MAPPED: 3> -> <SessionState.END_SENT: 4>
[2025-10-14T15:20:08.813Z] Connection state changed: <ConnectionState.OPENED: 9> -> <ConnectionState.CLOSE_SENT: 11>
[2025-10-14T15:20:08.815Z] Connection state changed: <ConnectionState.CLOSE_SENT: 11> -> <ConnectionState.END: 13>
[2025-10-14T15:20:08.816Z] Session state changed: <SessionState.END_SENT: 4> -> <SessionState.DISCARDING: 6>      
[2025-10-14T15:20:08.817Z] Link state changed: <LinkState.DETACH_SENT: 4> -> <LinkState.DETACHED: 0>
[2025-10-14T15:20:08.817Z] Management link sender state changed: <LinkState.DETACH_SENT: 4> -> <LinkState.DETACHED: 0>
[2025-10-14T15:20:08.818Z] Link state changed: <LinkState.DETACH_SENT: 4> -> <LinkState.DETACHED: 0>
[2025-10-14T15:20:08.819Z] Management link receiver state changed: <LinkState.DETACH_SENT: 4> -> <LinkState.DETACHED: 0>
[2025-10-14T15:20:08.965Z] Link state changed: <LinkState.DETACH_SENT: 4> -> <LinkState.DETACHED: 0>
[2025-10-14T15:20:09.607Z] Processing dte-notifications/sms-notifications
[2025-10-14T15:20:10.301Z] Connection state changed: None -> <ConnectionState.START: 0>
[2025-10-14T15:20:10.390Z] Connection state changed: <ConnectionState.START: 0> -> <ConnectionState.HDR_SENT: 2>
[2025-10-14T15:20:10.404Z] Connection state changed: <ConnectionState.HDR_SENT: 2> -> <ConnectionState.HDR_SENT: 2>
[2025-10-14T15:20:10.405Z] Connection state changed: <ConnectionState.HDR_SENT: 2> -> <ConnectionState.OPEN_PIPE: 4>
[2025-10-14T15:20:10.405Z] Session state changed: <SessionState.UNMAPPED: 0> -> <SessionState.BEGIN_SENT: 1>      
[2025-10-14T15:20:10.406Z] Link state changed: <LinkState.DETACHED: 0> -> <LinkState.ATTACH_SENT: 1>
[2025-10-14T15:20:10.406Z] Management link receiver state changed: <LinkState.DETACHED: 0> -> <LinkState.ATTACH_SENT: 1>
[2025-10-14T15:20:10.407Z] Link state changed: <LinkState.DETACHED: 0> -> <LinkState.ATTACH_SENT: 1>
[2025-10-14T15:20:10.408Z] Management link sender state changed: <LinkState.DETACHED: 0> -> <LinkState.ATTACH_SENT: 1>
[2025-10-14T15:20:10.411Z] Connection state changed: <ConnectionState.OPEN_PIPE: 4> -> <ConnectionState.OPEN_SENT: 7>
[2025-10-14T15:20:10.589Z] Connection state changed: <ConnectionState.OPEN_SENT: 7> -> <ConnectionState.OPENED: 9>
[2025-10-14T15:20:10.591Z] Session state changed: <SessionState.BEGIN_SENT: 1> -> <SessionState.MAPPED: 3>        
[2025-10-14T15:20:10.668Z] Link state changed: <LinkState.ATTACH_SENT: 1> -> <LinkState.ATTACHED: 3>
[2025-10-14T15:20:10.717Z] Management link receiver state changed: <LinkState.ATTACH_SENT: 1> -> <LinkState.ATTACHED: 3>
[2025-10-14T15:20:10.720Z] Link state changed: <LinkState.ATTACH_SENT: 1> -> <LinkState.ATTACHED: 3>
[2025-10-14T15:20:10.720Z] Management link sender state changed: <LinkState.ATTACH_SENT: 1> -> <LinkState.ATTACHED: 3>
[2025-10-14T15:20:10.969Z] Link state changed: <LinkState.DETACHED: 0> -> <LinkState.ATTACH_SENT: 1>
[2025-10-14T15:20:11.013Z] Link state changed: <LinkState.ATTACH_SENT: 1> -> <LinkState.ATTACHED: 3>
[2025-10-14T15:20:16.209Z] No new messages for dte-notifications/sms-notifications
[2025-10-14T15:20:16.420Z] Link state changed: <LinkState.ATTACHED: 3> -> <LinkState.DETACH_SENT: 4>
[2025-10-14T15:20:16.451Z] Link state changed: <LinkState.ATTACHED: 3> -> <LinkState.DETACH_SENT: 4>
[2025-10-14T15:20:16.550Z] Management link receiver state changed: <LinkState.ATTACHED: 3> -> <LinkState.DETACH_SENT: 4>
[2025-10-14T15:20:16.551Z] Link state changed: <LinkState.ATTACHED: 3> -> <LinkState.DETACH_SENT: 4>
[2025-10-14T15:20:16.551Z] Management link sender state changed: <LinkState.ATTACHED: 3> -> <LinkState.DETACH_SENT: 4>
[2025-10-14T15:20:16.552Z] Session state changed: <SessionState.MAPPED: 3> -> <SessionState.END_SENT: 4>
[2025-10-14T15:20:16.553Z] Connection state changed: <ConnectionState.OPENED: 9> -> <ConnectionState.CLOSE_SENT: 11>
[2025-10-14T15:20:16.554Z] Connection state changed: <ConnectionState.CLOSE_SENT: 11> -> <ConnectionState.END: 13>
[2025-10-14T15:20:16.554Z] Session state changed: <SessionState.END_SENT: 4> -> <SessionState.DISCARDING: 6>      
[2025-10-14T15:20:16.621Z] Link state changed: <LinkState.DETACH_SENT: 4> -> <LinkState.DETACHED: 0>
[2025-10-14T15:20:16.624Z] Management link sender state changed: <LinkState.DETACH_SENT: 4> -> <LinkState.DETACHED: 0>
[2025-10-14T15:20:16.627Z] Link state changed: <LinkState.DETACH_SENT: 4> -> <LinkState.DETACHED: 0>
[2025-10-14T15:20:16.629Z] Management link receiver state changed: <LinkState.DETACH_SENT: 4> -> <LinkState.DETACHED: 0>
[2025-10-14T15:20:16.838Z] Link state changed: <LinkState.DETACH_SENT: 4> -> <LinkState.DETACHED: 0>
[2025-10-14T15:20:17.413Z] ✅ Replication cycle completed successfully.