[2025-10-14T15:05:00.326Z] ✅ Configuration loaded successfully.
[2025-10-14T15:05:00.327Z] No Application Insights configuration found, using standard logging
[2025-10-14T15:05:00.327Z] Running replication direction: Primary → Secondary
[2025-10-14T15:05:00.328Z] Request URL: 'https://sbns-cu-dev-sos.servicebus.windows.net/$Resources/topics?$skip=REDACTED&$top=REDACTED&api-version=REDACTED'
Request method: 'GET'
Request headers:
    'Accept': 'application/xml, application/atom+xml'
    'x-ms-client-request-id': '277765ba-a90f-11f0-a4ed-02ec101e00f4'
    'User-Agent': 'azsdk-python-servicebusmanagementclient/unknown Python/3.11.9 (Windows-10-10.0.22631-SP0)'     
    'Authorization': 'REDACTED'
No body was attached to the request
[2025-10-14T15:05:01.187Z] Response status: 200
Response headers:
    'Transfer-Encoding': 'chunked'
    'Content-Type': 'application/atom+xml;type=feed;charset=utf-8'
    'Server': 'Microsoft-HTTPAPI/2.0'
    'Date': 'Tue, 14 Oct 2025 15:05:00 GMT'
[2025-10-14T15:05:01.188Z] Found 1 topics: ['dte-notifications']
[2025-10-14T15:05:01.188Z] Request URL: 'https://sbns-cu-dev-sos.servicebus.windows.net/dte-notifications/subscriptions?$skip=REDACTED&$top=REDACTED&api-version=REDACTED'
Request method: 'GET'
Request headers:
    'Accept': 'application/xml, application/atom+xml'
    'x-ms-client-request-id': '2827b98c-a90f-11f0-a376-02ec101e00f4'
    'User-Agent': 'azsdk-python-servicebusmanagementclient/unknown Python/3.11.9 (Windows-10-10.0.22631-SP0)'     
    'Authorization': 'REDACTED'
No body was attached to the request
[2025-10-14T15:05:01.299Z] Response status: 200
Response headers:
    'Transfer-Encoding': 'chunked'
    'Content-Type': 'application/atom+xml;type=feed;charset=utf-8'
    'ETag': '638932217405900000'
    'Server': 'Microsoft-HTTPAPI/2.0'
    'Strict-Transport-Security': 'REDACTED'
    'Date': 'Tue, 14 Oct 2025 15:05:00 GMT'
[2025-10-14T15:05:01.465Z] Found 2 subscriptions for topic 'dte-notifications': ['email-notifications', 'sms-notifications']
[2025-10-14T15:05:01.465Z] Processing dte-notifications/email-notifications
[2025-10-14T15:05:02.014Z] Connection state changed: None -> <ConnectionState.START: 0>
[2025-10-14T15:05:02.136Z] Connection state changed: <ConnectionState.START: 0> -> <ConnectionState.HDR_SENT: 2>
[2025-10-14T15:05:02.144Z] Connection state changed: <ConnectionState.HDR_SENT: 2> -> <ConnectionState.HDR_SENT: 2>
[2025-10-14T15:05:02.144Z] Connection state changed: <ConnectionState.HDR_SENT: 2> -> <ConnectionState.OPEN_PIPE: 4>
[2025-10-14T15:05:02.145Z] Session state changed: <SessionState.UNMAPPED: 0> -> <SessionState.BEGIN_SENT: 1>      
[2025-10-14T15:05:02.166Z] Link state changed: <LinkState.DETACHED: 0> -> <LinkState.ATTACH_SENT: 1>
[2025-10-14T15:05:02.167Z] Management link receiver state changed: <LinkState.DETACHED: 0> -> <LinkState.ATTACH_SENT: 1>
[2025-10-14T15:05:02.168Z] Link state changed: <LinkState.DETACHED: 0> -> <LinkState.ATTACH_SENT: 1>
[2025-10-14T15:05:02.168Z] Management link sender state changed: <LinkState.DETACHED: 0> -> <LinkState.ATTACH_SENT: 1>
[2025-10-14T15:05:02.171Z] Connection state changed: <ConnectionState.OPEN_PIPE: 4> -> <ConnectionState.OPEN_SENT: 7>
[2025-10-14T15:05:02.190Z] Connection state changed: <ConnectionState.OPEN_SENT: 7> -> <ConnectionState.OPENED: 9>
[2025-10-14T15:05:02.266Z] Session state changed: <SessionState.BEGIN_SENT: 1> -> <SessionState.MAPPED: 3>
[2025-10-14T15:05:02.379Z] Link state changed: <LinkState.ATTACH_SENT: 1> -> <LinkState.ATTACHED: 3>
[2025-10-14T15:05:02.480Z] Management link receiver state changed: <LinkState.ATTACH_SENT: 1> -> <LinkState.ATTACHED: 3>
[2025-10-14T15:05:02.483Z] Link state changed: <LinkState.ATTACH_SENT: 1> -> <LinkState.ATTACHED: 3>
[2025-10-14T15:05:02.484Z] Management link sender state changed: <LinkState.ATTACH_SENT: 1> -> <LinkState.ATTACHED: 3>
[2025-10-14T15:05:02.674Z] Link state changed: <LinkState.DETACHED: 0> -> <LinkState.ATTACH_SENT: 1>
[2025-10-14T15:05:02.799Z] Link state changed: <LinkState.ATTACH_SENT: 1> -> <LinkState.ATTACHED: 3>
[2025-10-14T15:05:07.966Z] No new messages for dte-notifications/email-notifications
[2025-10-14T15:05:07.968Z] Link state changed: <LinkState.ATTACHED: 3> -> <LinkState.DETACH_SENT: 4>
[2025-10-14T15:05:07.969Z] Link state changed: <LinkState.ATTACHED: 3> -> <LinkState.DETACH_SENT: 4>
[2025-10-14T15:05:07.969Z] Management link receiver state changed: <LinkState.ATTACHED: 3> -> <LinkState.DETACH_SENT: 4>
[2025-10-14T15:05:07.970Z] Link state changed: <LinkState.ATTACHED: 3> -> <LinkState.DETACH_SENT: 4>
[2025-10-14T15:05:07.971Z] Management link sender state changed: <LinkState.ATTACHED: 3> -> <LinkState.DETACH_SENT: 4>
[2025-10-14T15:05:07.972Z] Session state changed: <SessionState.MAPPED: 3> -> <SessionState.END_SENT: 4>
[2025-10-14T15:05:07.974Z] Connection state changed: <ConnectionState.OPENED: 9> -> <ConnectionState.CLOSE_SENT: 11>
[2025-10-14T15:05:07.974Z] Connection state changed: <ConnectionState.CLOSE_SENT: 11> -> <ConnectionState.END: 13>
[2025-10-14T15:05:07.975Z] Session state changed: <SessionState.END_SENT: 4> -> <SessionState.DISCARDING: 6>      
[2025-10-14T15:05:07.975Z] Link state changed: <LinkState.DETACH_SENT: 4> -> <LinkState.DETACHED: 0>
[2025-10-14T15:05:07.976Z] Management link sender state changed: <LinkState.DETACH_SENT: 4> -> <LinkState.DETACHED: 0>
[2025-10-14T15:05:07.977Z] Link state changed: <LinkState.DETACH_SENT: 4> -> <LinkState.DETACHED: 0>
[2025-10-14T15:05:07.977Z] Management link receiver state changed: <LinkState.DETACH_SENT: 4> -> <LinkState.DETACHED: 0>
[2025-10-14T15:05:07.978Z] Link state changed: <LinkState.DETACH_SENT: 4> -> <LinkState.DETACHED: 0>
[2025-10-14T15:05:09.571Z] Processing dte-notifications/sms-notifications
[2025-10-14T15:05:09.572Z] Connection state changed: None -> <ConnectionState.START: 0>
[2025-10-14T15:05:09.573Z] Connection state changed: <ConnectionState.START: 0> -> <ConnectionState.HDR_SENT: 2>  
[2025-10-14T15:05:09.573Z] Connection state changed: <ConnectionState.HDR_SENT: 2> -> <ConnectionState.HDR_SENT: 2>
[2025-10-14T15:05:09.574Z] Connection state changed: <ConnectionState.HDR_SENT: 2> -> <ConnectionState.OPEN_PIPE: 4>
[2025-10-14T15:05:09.574Z] Session state changed: <SessionState.UNMAPPED: 0> -> <SessionState.BEGIN_SENT: 1>      
[2025-10-14T15:05:09.576Z] Link state changed: <LinkState.DETACHED: 0> -> <LinkState.ATTACH_SENT: 1>
[2025-10-14T15:05:09.576Z] Management link receiver state changed: <LinkState.DETACHED: 0> -> <LinkState.ATTACH_SENT: 1>
[2025-10-14T15:05:09.577Z] Link state changed: <LinkState.DETACHED: 0> -> <LinkState.ATTACH_SENT: 1>
[2025-10-14T15:05:09.578Z] Management link sender state changed: <LinkState.DETACHED: 0> -> <LinkState.ATTACH_SENT: 1>
[2025-10-14T15:05:09.579Z] Connection state changed: <ConnectionState.OPEN_PIPE: 4> -> <ConnectionState.OPEN_SENT: 7>
[2025-10-14T15:05:09.579Z] Connection state changed: <ConnectionState.OPEN_SENT: 7> -> <ConnectionState.OPENED: 9>
[2025-10-14T15:05:09.580Z] Session state changed: <SessionState.BEGIN_SENT: 1> -> <SessionState.MAPPED: 3>        
[2025-10-14T15:05:09.581Z] Link state changed: <LinkState.ATTACH_SENT: 1> -> <LinkState.ATTACHED: 3>
[2025-10-14T15:05:09.581Z] Management link receiver state changed: <LinkState.ATTACH_SENT: 1> -> <LinkState.ATTACHED: 3>
[2025-10-14T15:05:09.582Z] Link state changed: <LinkState.ATTACH_SENT: 1> -> <LinkState.ATTACHED: 3>
[2025-10-14T15:05:09.583Z] Management link sender state changed: <LinkState.ATTACH_SENT: 1> -> <LinkState.ATTACHED: 3>
[2025-10-14T15:05:09.769Z] Link state changed: <LinkState.DETACHED: 0> -> <LinkState.ATTACH_SENT: 1>
[2025-10-14T15:05:09.863Z] Link state changed: <LinkState.ATTACH_SENT: 1> -> <LinkState.ATTACHED: 3>
[2025-10-14T15:05:15.008Z] No new messages for dte-notifications/sms-notifications
[2025-10-14T15:05:15.010Z] Link state changed: <LinkState.ATTACHED: 3> -> <LinkState.DETACH_SENT: 4>
[2025-10-14T15:05:15.010Z] Link state changed: <LinkState.ATTACHED: 3> -> <LinkState.DETACH_SENT: 4>
[2025-10-14T15:05:15.013Z] Management link receiver state changed: <LinkState.ATTACHED: 3> -> <LinkState.DETACH_SENT: 4>
[2025-10-14T15:05:15.014Z] Link state changed: <LinkState.ATTACHED: 3> -> <LinkState.DETACH_SENT: 4>
[2025-10-14T15:05:15.017Z] Management link sender state changed: <LinkState.ATTACHED: 3> -> <LinkState.DETACH_SENT: 4>
[2025-10-14T15:05:15.018Z] Session state changed: <SessionState.MAPPED: 3> -> <SessionState.END_SENT: 4>
[2025-10-14T15:05:15.019Z] Connection state changed: <ConnectionState.OPENED: 9> -> <ConnectionState.CLOSE_SENT: 11>
[2025-10-14T15:05:15.020Z] Connection state changed: <ConnectionState.CLOSE_SENT: 11> -> <ConnectionState.END: 13>
[2025-10-14T15:05:15.021Z] Session state changed: <SessionState.END_SENT: 4> -> <SessionState.DISCARDING: 6>      
[2025-10-14T15:05:15.023Z] Link state changed: <LinkState.DETACH_SENT: 4> -> <LinkState.DETACHED: 0>
[2025-10-14T15:05:15.093Z] Management link sender state changed: <LinkState.DETACH_SENT: 4> -> <LinkState.DETACHED: 0>
[2025-10-14T15:05:15.094Z] Link state changed: <LinkState.DETACH_SENT: 4> -> <LinkState.DETACHED: 0>
[2025-10-14T15:05:15.094Z] Management link receiver state changed: <LinkState.DETACH_SENT: 4> -> <LinkState.DETACHED: 0>
[2025-10-14T15:05:15.095Z] Link state changed: <LinkState.DETACH_SENT: 4> -> <LinkState.DETACHED: 0>
[2025-10-14T15:05:15.602Z] ✅ Replication cycle completed successfully.