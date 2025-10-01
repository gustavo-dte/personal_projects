2025-10-01T21:50:35.871Z] x-ms-version:2024-08-04
[2025-10-01T21:50:35.872Z] Accept:application/xml
[2025-10-01T21:50:35.873Z] x-ms-client-request-id:f6195025-3727-4090-b421-004dc3de4ff2
[2025-10-01T21:50:35.875Z] x-ms-return-client-request-id:true
[2025-10-01T21:50:35.877Z] User-Agent:azsdk-net-Storage.Blobs/12.21.2 (.NET 8.0.19; Microsoft Windows 10.0.22631)    
[2025-10-01T21:50:35.878Z] x-ms-date:Wed, 01 Oct 2025 21:50:35 GMT
[2025-10-01T21:50:35.880Z] Authorization:REDACTED
[2025-10-01T21:50:35.881Z] client assembly: Azure.Storage.Blobs
[2025-10-01T21:50:36.274Z] dte-notifications/Subscriptions/sms-notifications-80cbd383-e320-47dd-a589-97c2101b5e9b-Receiver: ReceiveBatchAsync done. Received '0' messages. LockTokens =
[2025-10-01T21:50:36.570Z] dte-notifications/Subscriptions/sms-notifications-80cbd383-e320-47dd-a589-97c2101b5e9b-Receiver: ReceiveBatchAsync start. MessageCount = 1[2025-10-01T21:50:36.909Z] dte-notifications/Subscriptions/sms-notifications-80cbd383-e320-47dd-a589-97c2101b5e9b-Receiver: ReceiveBatchAsync done. Received '0' messages. LockTokens =   

[2025-10-01T21:50:37.311Z] dte-notifications/Subscriptions/sms-notifications-80cbd383-e320-47dd-a589-97c2101b5e9b-Receiver: ReceiveBatchAsync start. MessageCount = 1[2025-10-01T21:50:37.312Z] dte-notifications/Subscriptions/sms-notifications-80cbd383-e320-47dd-a589-97c2101b5e9b-Receiver: ReceiveBatchAsync done. Received '0' messages. LockTokens =   

[2025-10-01T21:50:37.315Z] dte-notifications/Subscriptions/sms-notifications-80cbd383-e320-47dd-a589-97c2101b5e9b-Receiver: ReceiveBatchAsync start. MessageCount = 1
[2025-10-01T21:50:37.648Z] dte-notifications/Subscriptions/sms-notifications-80cbd383-e320-47dd-a589-97c2101b5e9b-Receiver: ReceiveBatchAsync done. Received '0' messages. LockTokens =
[2025-10-01T21:50:37.828Z] dte-notifications/Subscriptions/sms-notifications-80cbd383-e320-47dd-a589-97c2101b5e9b-Receiver: ReceiveBatchAsync start. MessageCount = 1[2025-10-01T21:50:38.154Z] dte-notifications/Subscriptions/sms-notifications-80cbd383-e320-47dd-a589-97c2101b5e9b-Receiver: ReceiveBatchAsync done. Received '0' messages. LockTokens =   
[2025-10-01T21:50:38.161Z] Request [f6195025-3727-4090-b421-004dc3de4ff2] exception Azure.RequestFailedException: No connection could be made because the target machine actively refused it. (127.0.0.1:10000)
[2025-10-01T21:50:38.567Z] dte-notifications/Subscriptions/sms-notifications-80cbd383-e320-47dd-a589-97c2101b5e9b-Receiver: ReceiveBatchAsync done. Received '0' messages. LockTokens =
[2025-10-01T21:50:38.940Z] dte-notifications/Subscriptions/sms-notifications-80cbd383-e320-47dd-a589-97c2101b5e9b-Receiver: ReceiveBatchAsync start. MessageCount = 1
[2025-10-01T21:50:39.687Z] dte-notifications/Subscriptions/sms-notifications-80cbd383-e320-47dd-a589-97c2101b5e9b-Receiver: ReceiveBatchAsync start. MessageCount = 1

[2025-10-01T21:50:39.355Z]  ---> System.Net.Http.HttpRequestException: No connection could be made because the target machine actively refused it. (127.0.0.1:10000)
[2025-10-01T21:50:40.233Z]  ---> System.Net.Sockets.SocketException (10061): No connection could be made because the target machine actively refused it.
[2025-10-01T21:50:41.065Z]    at System.Net.Sockets.Socket.AwaitableSocketAsyncEventArgs.ThrowException(SocketError error, CancellationToken cancellationToken)
[2025-10-01T21:50:41.327Z]    at System.Net.Sockets.Socket.AwaitableSocketAsyncEventArgs.System.Threading.Tasks.Sources.IValueTaskSource.GetResult(Int16 token)
[2025-10-01T21:50:41.328Z]    at System.Net.Sockets.Socket.<ConnectAsync>g__WaitForConnectWithCancellation|285_0(AwaitableSocketAsyncEventArgs saea, ValueTask connectTask, CancellationToken cancellationToken)
[2025-10-01T21:50:41.329Z]    at System.Net.Http.HttpConnectionPool.ConnectToTcpHostAsync(String host, Int32 port, HttpRequestMessage initialRequest, Boolean async, CancellationToken cancellationToken)
[2025-10-01T21:50:41.329Z]    --- End of inner exception stack trace ---
[2025-10-01T21:50:41.329Z]    at System.Net.Http.HttpConnectionPool.ConnectToTcpHostAsync(String host, Int32 port, HttpRequestMessage initialRequest, Boolean async, CancellationToken cancellationToken)
[2025-10-01T21:50:41.330Z]    at System.Net.Http.HttpConnectionPool.ConnectAsync(HttpRequestMessage request, Boolean async, CancellationToken cancellationToken)
[2025-10-01T21:50:41.330Z]    at System.Net.Http.HttpConnectionPool.CreateHttp11ConnectionAsync(HttpRequestMessage request, Boolean async, CancellationToken cancellationToken)
[2025-10-01T21:50:41.330Z]    at System.Net.Http.HttpConnectionPool.AddHttp11ConnectionAsync(QueueItem queueItem)    
[2025-10-01T21:50:41.331Z]    at System.Threading.Tasks.TaskCompletionSourceWithCancellation`1.WaitWithCancellationAsync(CancellationToken cancellationToken)
[2025-10-01T21:50:41.331Z]    at System.Net.Http.HttpConnectionPool.SendWithVersionDetectionAndRetryAsync(HttpRequestMessage request, Boolean async, Boolean doRequestAuth, CancellationToken cancellationToken)
[2025-10-01T21:50:41.331Z]    at System.Net.Http.HttpClient.<SendAsync>g__Core|83_0(HttpRequestMessage request, HttpCompletionOption completionOption, CancellationTokenSource cts, Boolean disposeCts, CancellationTokenSource pendingRequestsCts, CancellationToken originalCancellationToken)
[2025-10-01T21:50:41.332Z]    at Azure.Core.Pipeline.HttpClientTransport.ProcessSyncOrAsync(HttpMessage message, Boolean async)
[2025-10-01T21:50:41.333Z]    --- End of inner exception stack trace ---
[2025-10-01T21:50:41.336Z]    at Azure.Core.Pipeline.HttpClientTransport.ProcessSyncOrAsync(HttpMessage message, Boolean async)
[2025-10-01T21:50:41.336Z]    at Azure.Core.Pipeline.HttpPipelineTransportPolicy.ProcessAsync(HttpMessage message, ReadOnlyMemory`1 pipeline)
[2025-10-01T21:50:41.337Z]    at Azure.Core.Pipeline.ResponseBodyPolicy.ProcessAsync(HttpMessage message, ReadOnlyMemory`1 pipeline, Boolean async)
[2025-10-01T21:50:41.337Z]    at Azure.Core.Pipeline.LoggingPolicy.ProcessAsync(HttpMessage message, ReadOnlyMemory`1 pipeline, Boolean async)
[2025-10-01T21:50:42.032Z] Request [f6195025-3727-4090-b421-004dc3de4ff2] attempt number 1 took 05.7s
[2025-10-01T21:50:42.582Z] Request [f6195025-3727-4090-b421-004dc3de4ff2] HEAD http://127.0.0.1:10000/devstoreaccount1/azure-webjobs-hosts/locks/avd1371-2113432517/host[2025-10-01T21:50:42.686Z] dte-notifications/Subscriptions/sms-notifications-80cbd383-e320-47dd-a589-97c2101b5e9b-Receiver: ReceiveBatchAsync done. Received '0' messages. LockTokens =
 [2025-10-01T21:50:43.286Z] dte-notifications/Subscriptions/sms-notifications-80cbd383-e320-47dd-a589-97c2101b5e9b-Receiver: ReceiveBatchAsync done. Received '0' messages. LockTokens =
[2025-10-01T21:50:43.602Z] dte-notifications/Subscriptions/sms-notifications-80cbd383-e320-47dd-a589-97c2101b5e9b-Receiver: ReceiveBatchAsync done. Received '0' messages. LockTokens =
[2025-10-01T21:50:43.941Z] dte-notifications/Subscriptions/sms-notifications-80cbd383-e320-47dd-a589-97c2101b5e9b-Receiver: ReceiveBatchAsync start. MessageCount = 1

[2025-10-01T21:50:43.939Z] x-ms-version:2024-08-04
[2025-10-01T21:50:43.945Z] Accept:application/xml
[2025-10-01T21:50:43.946Z] x-ms-client-request-id:f6195025-3727-4090-b421-004dc3de4ff2[2025-10-01T21:50:43.944Z] dte-notifications/Subscriptions/sms-notifications-80cbd383-e320-47dd-a589-97c2101b5e9b-Receiver: ReceiveBatchAsync start. MessageCount = 1
[2025-10-01T21:50:43.824Z] dte-notifications/Subscriptions/sms-notifications-80cbd383-e320-47dd-a589-97c2101b5e9b-Receiver: ReceiveBatchAsync done. Received '0' messages. LockTokens =
[2025-10-01T21:50:43.943Z] dte-notifications/Subscriptions/sms-notifications-80cbd383-e320-47dd-a589-97c2101b5e9b-Receiver: ReceiveBatchAsync done. Received '0' messages. LockTokens =
[2025-10-01T21:50:44.556Z] dte-notifications/Subscriptions/sms-notifications-80cbd383-e320-47dd-a589-97c2101b5e9b-Receiver: ReceiveBatchAsync start. MessageCount = 1
[2025-10-01T21:50:43.824Z] dte-notifications/Subscriptions/sms-notifications-80cbd383-e320-47dd-a589-97c2101b5e9b-Receiver: ReceiveBatchAsync done. Received '0' messages. LockTokens =

[2025-10-01T21:50:44.561Z] x-ms-return-client-request-id:true
[2025-10-01T21:50:44.562Z] User-Agent:azsdk-net-Storage.Blobs/12.21.2 (.NET 8.0.19; Microsoft Windows 10.0.22631)    
[2025-10-01T21:50:44.566Z] x-ms-date:Wed, 01 Oct 2025 21:50:42 GMT
[2025-10-01T21:50:44.567Z] Authorization:REDACTED
[2025-10-01T21:50:44.572Z] client assembly: Azure.Storage.Blobs

[2025-10-01T21:50:44.553Z] dte-notifications/Subscriptions/sms-notifications-80cbd383-e320-47dd-a589-97c2101b5e9b-Receiver: ReceiveBatchAsync done. Received '0' messages. LockTokens =
[2025-10-01T21:50:44.554Z] dte-notifications/Subscriptions/sms-notifications-80cbd383-e320-47dd-a589-97c2101b5e9b-Receiver: ReceiveBatchAsync start. MessageCount = 1
[2025-10-01T21:50:44.844Z] dte-notifications/Subscriptions/sms-notifications-80cbd383-e320-47dd-a589-97c2101b5e9b-Receiver: ReceiveBatchAsync start. MessageCount = 1
[2025-10-01T21:50:44.850Z] dte-notifications/Subscriptions/sms-notifications-80cbd383-e320-47dd-a589-97c2101b5e9b-Receiver: ReceiveBatchAsync start. MessageCount = 1
[2025-10-01T21:50:44.851Z] dte-notifications/Subscriptions/sms-notifications-80cbd383-e320-47dd-a589-97c2101b5e9b-Receiver: ReceiveBatchAsync done. Received '0' messages. LockTokens =
[2025-10-01T21:50:44.852Z] dte-notifications/Subscriptions/sms-notifications-80cbd383-e320-47dd-a589-97c2101b5e9b-Receiver: ReceiveBatchAsync done. Received '0' messages. LockTokens =
[2025-10-01T21:50:44.854Z] dte-notifications/Subscriptions/sms-notifications-80cbd383-e320-47dd-a589-97c2101b5e9b-Receiver: ReceiveBatchAsync start. MessageCount = 1
[2025-10-01T21:50:44.560Z] dte-notifications/Subscriptions/sms-notifications-80cbd383-e320-47dd-a589-97c2101b5e9b-Receiver: ReceiveBatchAsync start. MessageCount = 1
[2025-10-01T21:50:44.854Z] dte-notifications/Subscriptions/sms-notifications-80cbd383-e320-47dd-a589-97c2101b5e9b-Receiver: ReceiveBatchAsync start. MessageCount = 1
[2025-10-01T21:50:44.558Z] dte-notifications/Subscriptions/sms-notifications-80cbd383-e320-47dd-a589-97c2101b5e9b-Receiver: ReceiveBatchAsync done. Received '0' messages. LockTokens =
[2025-10-01T21:50:44.858Z] dte-notifications/Subscriptions/sms-notifications-80cbd383-e320-47dd-a589-97c2101b5e9b-Receiver: ReceiveBatchAsync start. MessageCount = 1
[2025-10-01T21:50:47.644Z] Request [f6195025-3727-4090-b421-004dc3de4ff2] exception Azure.RequestFailedException: No connection could be made because the target machine actively refused it. (127.0.0.1:10000)
[2025-10-01T21:50:47.830Z]  ---> System.Net.Http.HttpRequestException: No connection could be made because the target machine actively refused it. (127.0.0.1:10000)
[2025-10-01T21:50:47.831Z]  ---> System.Net.Sockets.SocketException (10061): No connection could be made because the target machine actively refused it.
[2025-10-01T21:50:47.832Z]    at System.Net.Sockets.Socket.AwaitableSocketAsyncEventArgs.ThrowException(SocketError error, CancellationToken cancellationToken)
[2025-10-01T21:50:48.243Z]    at System.Net.Sockets.Socket.AwaitableSocketAsyncEventArgs.System.Threading.Tasks.Sources.IValueTaskSource.GetResult(Int16 token)
[2025-10-01T21:50:48.509Z]    at System.Net.Sockets.Socket.<ConnectAsync>g__WaitForConnectWithCancellation|285_0(AwaitableSocketAsyncEventArgs saea, ValueTask connectTask, CancellationToken cancellationToken)
[2025-10-01T21:50:48.860Z]    at System.Net.Http.HttpConnectionPool.ConnectToTcpHostAsync(String host, Int32 port, HttpRequestMessage initialRequest, Boolean async, CancellationToken cancellationToken)
[2025-10-01T21:50:48.861Z]    --- End of inner exception stack trace ---
[2025-10-01T21:50:48.861Z]    at System.Net.Http.HttpConnectionPool.ConnectToTcpHostAsync(String host, Int32 port, HttpRequestMessage initialRequest, Boolean async, CancellationToken cancellationToken)
[2025-10-01T21:50:48.862Z]    at System.Net.Http.HttpConnectionPool.ConnectAsync(HttpRequestMessage request, Boolean async, CancellationToken cancellationToken)
[2025-10-01T21:50:48.862Z]    at System.Net.Http.HttpConnectionPool.CreateHttp11ConnectionAsync(HttpRequestMessage request, Boolean async, CancellationToken cancellationToken)
[2025-10-01T21:50:48.863Z]    at System.Net.Http.HttpConnectionPool.AddHttp11ConnectionAsync(QueueItem queueItem)    
[2025-10-01T21:50:48.863Z]    at System.Threading.Tasks.TaskCompletionSourceWithCancellation`1.WaitWithCancellationAsync(CancellationToken cancellationToken)
[2025-10-01T21:50:48.864Z]    at System.Net.Http.HttpConnectionPool.SendWithVersionDetectionAndRetryAsync(HttpRequestMessage request, Boolean async, Boolean doRequestAuth, CancellationToken cancellationToken)
[2025-10-01T21:50:48.924Z]    at System.Net.Http.HttpClient.<SendAsync>g__Core|83_0(HttpRequestMessage request, HttpCompletionOption completionOption, CancellationTokenSource cts, Boolean disposeCts, CancellationTokenSource pendingRequestsCts, CancellationToken originalCancellationToken)
[2025-10-01T21:50:48.926Z]    at Azure.Core.Pipeline.HttpClientTransport.ProcessSyncOrAsync(HttpMessage message, Boolean async)
[2025-10-01T21:50:48.926Z]    --- End of inner exception stack trace ---
[2025-10-01T21:50:48.927Z]    at Azure.Core.Pipeline.HttpClientTransport.ProcessSyncOrAsync(HttpMessage message, Boolean async)
[2025-10-01T21:50:48.955Z]    at Azure.Core.Pipeline.HttpPipelineTransportPolicy.ProcessAsync(HttpMessage message, ReadOnlyMemory`1 pipeline)
[2025-10-01T21:50:48.957Z]    at Azure.Core.Pipeline.ResponseBodyPolicy.ProcessAsync(HttpMessage message, ReadOnlyMemory`1 pipeline, Boolean async)
[2025-10-01T21:50:48.961Z]    at Azure.Core.Pipeline.LoggingPolicy.ProcessAsync(HttpMessage message, ReadOnlyMemory`1 pipeline, Boolean async)
[2025-10-01T21:50:50.381Z] Request [f6195025-3727-4090-b421-004dc3de4ff2] attempt number 2 took 06.5s
[2025-10-01T21:50:51.026Z] Request [f6195025-3727-4090-b421-004dc3de4ff2] HEAD http://127.0.0.1:10000/devstoreaccount1/azure-webjobs-hosts/locks/avd1371-2113432517/host[2025-10-01T21:50:51.139Z] Stopping host...