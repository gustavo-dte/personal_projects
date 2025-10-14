[2025-10-14T13:37:48.037Z] No HTTP routes mapped
[2025-10-14T13:37:48.035Z] HttpOptions
[2025-10-14T13:37:48.038Z]
[2025-10-14T13:37:48.038Z] {
[2025-10-14T13:37:48.157Z]   "DynamicThrottlesEnabled": false,
[2025-10-14T13:37:48.158Z]   "EnableChunkedRequestBinding": false,
[2025-10-14T13:37:48.158Z]   "MaxConcurrentRequests": -1,
[2025-10-14T13:37:48.158Z]   "MaxConcurrentRequests": -1,
[2025-10-14T13:37:48.159Z]   "MaxOutstandingRequests": -1,
[2025-10-14T13:37:48.159Z]   "RoutePrefix": "api"[2025-10-14T13:37:48.165Z] Host initialized (7386ms)    

[2025-10-14T13:37:48.632Z] }

Functions:

        src: timerTrigger

[2025-10-14T13:37:49.886Z] Successfully processed FunctionLoadRequest, request ID: c1f91f7b-384f-4990-844e-0c491b08e772, function ID: a87570e4-6b42-4a0a-999c-2dcbb0e91f77,function Name: src,programming model: V1
[2025-10-14T13:38:13.173Z] The listener for function 'Functions.src' was unable to start.
[2025-10-14T13:38:13.174Z] The listener for function 'Functions.src' was unable to start. Azure.Storage.Blobs: Service request failed.
[2025-10-14T13:38:13.174Z] Status: 500 (Internal Server Error)
[2025-10-14T13:38:13.175Z]
[2025-10-14T13:38:13.175Z] Headers:
[2025-10-14T13:38:13.176Z] Server: Azurite-Blob/3.35.0
[2025-10-14T13:38:13.176Z] Date: Tue, 14 Oct 2025 13:38:13 GMT
[2025-10-14T13:38:13.177Z] Connection: keep-alive
[2025-10-14T13:38:13.177Z] Keep-Alive: REDACTED
[2025-10-14T13:38:13.178Z] Content-Length: 0
[2025-10-14T13:38:13.178Z] .
[2025-10-14T13:38:13.186Z] Host started (32527ms)
[2025-10-14T13:38:13.187Z] Job host started
[2025-10-14T13:38:15.193Z] Retrying to start listener for function 'Functions.src' (Attempt 1)
[2025-10-14T13:38:15.197Z] Listener successfully started for function 'Functions.src' after 1 retries.   