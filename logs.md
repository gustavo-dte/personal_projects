[2025-10-01T23:55:20.883Z] x-ms-version:2024-08-04
[2025-10-01T23:55:20.884Z] Accept:application/xml
[2025-10-01T23:55:20.885Z] x-ms-client-request-id:f27ef14f-60fe-4bc8-b032-4eb9d22f2f01
[2025-10-01T23:55:21.027Z] x-ms-return-client-request-id:true
[2025-10-01T23:55:21.044Z] User-Agent:azsdk-net-Storage.Blobs/12.21.2 (.NET 8.0.19; Microsoft Windows 10.0.22631)    
[2025-10-01T23:55:21.045Z] x-ms-date:Wed, 01 Oct 2025 23:55:20 GMT
[2025-10-01T23:55:21.046Z] Authorization:REDACTED
[2025-10-01T23:55:21.047Z] client assembly: Azure.Storage.Blobs
[2025-10-01T23:55:23.081Z] Request [f27ef14f-60fe-4bc8-b032-4eb9d22f2f01] exception Azure.RequestFailedException: No connection could be made because the target machine actively refused it. (127.0.0.1:10000)
[2025-10-01T23:55:23.082Z]  ---> System.Net.Http.HttpRequestException: No connection could be made because the target machine actively refused it. (127.0.0.1:10000)
[2025-10-01T23:55:23.083Z]  ---> System.Net.Sockets.SocketException (10061): No connection could be made because the target machine actively refused it.
[2025-10-01T23:55:23.084Z]    at System.Net.Sockets.Socket.AwaitableSocketAsyncEventArgs.ThrowException(SocketError error, CancellationToken cancellationToken)
[2025-10-01T23:55:23.085Z]    at System.Net.Sockets.Socket.AwaitableSocketAsyncEventArgs.System.Threading.Tasks.Sources.IValueTaskSource.GetResult(Int16 token)
[2025-10-01T23:55:23.158Z]    at System.Net.Sockets.Socket.<ConnectAsync>g__WaitForConnectWithCancellation|285_0(AwaitableSocketAsyncEventArgs saea, ValueTask connectTask, CancellationToken cancellationToken)
[2025-10-01T23:55:23.159Z]    at System.Net.Http.HttpConnectionPool.ConnectToTcpHostAsync(String host, Int32 port, HttpRequestMessage initialRequest, Boolean async, CancellationToken cancellationToken)
[2025-10-01T23:55:23.160Z]    --- End of inner exception stack trace ---
[2025-10-01T23:55:23.161Z]    at System.Net.Http.HttpConnectionPool.ConnectToTcpHostAsync(String host, Int32 port, HttpRequestMessage initialRequest, Boolean async, CancellationToken cancellationToken)
[2025-10-01T23:55:23.162Z]    at System.Net.Http.HttpConnectionPool.ConnectAsync(HttpRequestMessage request, Boolean async, CancellationToken cancellationToken)
[2025-10-01T23:55:23.163Z]    at System.Net.Http.HttpConnectionPool.CreateHttp11ConnectionAsync(HttpRequestMessage request, Boolean async, CancellationToken cancellationToken)
[2025-10-01T23:55:23.163Z]    at System.Net.Http.HttpConnectionPool.AddHttp11ConnectionAsync(QueueItem queueItem)    
[2025-10-01T23:55:23.164Z]    at System.Threading.Tasks.TaskCompletionSourceWithCancellation`1.WaitWithCancellationAsync(CancellationToken cancellationToken)
[2025-10-01T23:55:23.164Z]    at System.Net.Http.HttpConnectionPool.SendWithVersionDetectionAndRetryAsync(HttpRequestMessage request, Boolean async, Boolean doRequestAuth, CancellationToken cancellationToken)
[2025-10-01T23:55:23.165Z]    at System.Net.Http.HttpClient.<SendAsync>g__Core|83_0(HttpRequestMessage request, HttpCompletionOption completionOption, CancellationTokenSource cts, Boolean disposeCts, CancellationTokenSource pendingRequestsCts, CancellationToken originalCancellationToken)
[2025-10-01T23:55:23.166Z]    at Azure.Core.Pipeline.HttpClientTransport.ProcessSyncOrAsync(HttpMessage message, Boolean async)
[2025-10-01T23:55:23.166Z]    --- End of inner exception stack trace ---
[2025-10-01T23:55:23.168Z]    at Azure.Core.Pipeline.HttpClientTransport.ProcessSyncOrAsync(HttpMessage message, Boolean async)
[2025-10-01T23:55:23.169Z]    at Azure.Core.Pipeline.HttpPipelineTransportPolicy.ProcessAsync(HttpMessage message, ReadOnlyMemory`1 pipeline)
[2025-10-01T23:55:23.169Z]    at Azure.Core.Pipeline.ResponseBodyPolicy.ProcessAsync(HttpMessage message, ReadOnlyMemory`1 pipeline, Boolean async)
[2025-10-01T23:55:23.170Z]    at Azure.Core.Pipeline.LoggingPolicy.ProcessAsync(HttpMessage message, ReadOnlyMemory`1 pipeline, Boolean async)
[2025-10-01T23:55:24.688Z] Request [f27ef14f-60fe-4bc8-b032-4eb9d22f2f01] attempt number 2 took 02.3s
[2025-10-01T23:55:24.690Z] Request [f27ef14f-60fe-4bc8-b032-4eb9d22f2f01] HEAD http://127.0.0.1:10000/devstoreaccount1/azure-webjobs-hosts/locks/avd1371-2113432517/host
[2025-10-01T23:55:24.691Z] x-ms-version:2024-08-04
[2025-10-01T23:55:24.691Z] Accept:application/xml
[2025-10-01T23:55:24.693Z] x-ms-client-request-id:f27ef14f-60fe-4bc8-b032-4eb9d22f2f01
[2025-10-01T23:55:24.694Z] x-ms-return-client-request-id:true
[2025-10-01T23:55:24.695Z] User-Agent:azsdk-net-Storage.Blobs/12.21.2 (.NET 8.0.19; Microsoft Windows 10.0.22631)    
[2025-10-01T23:55:24.696Z] x-ms-date:Wed, 01 Oct 2025 23:55:24 GMT
[2025-10-01T23:55:24.696Z] Authorization:REDACTED
[2025-10-01T23:55:24.697Z] client assembly: Azure.Storage.Blobs
[2025-10-01T23:55:26.782Z] Request [f27ef14f-60fe-4bc8-b032-4eb9d22f2f01] exception Azure.RequestFailedException: No connection could be made because the target machine actively refused it. (127.0.0.1:10000)
[2025-10-01T23:55:26.782Z]  ---> System.Net.Http.HttpRequestException: No connection could be made because the target machine actively refused it. (127.0.0.1:10000)
[2025-10-01T23:55:26.783Z]  ---> System.Net.Sockets.SocketException (10061): No connection could be made because the target machine actively refused it.
[2025-10-01T23:55:26.783Z]    at System.Net.Sockets.Socket.AwaitableSocketAsyncEventArgs.ThrowException(SocketError error, CancellationToken cancellationToken)
[2025-10-01T23:55:26.784Z]    at System.Net.Sockets.Socket.AwaitableSocketAsyncEventArgs.System.Threading.Tasks.Sources.IValueTaskSource.GetResult(Int16 token)
[2025-10-01T23:55:26.785Z]    at System.Net.Sockets.Socket.<ConnectAsync>g__WaitForConnectWithCancellation|285_0(AwaitableSocketAsyncEventArgs saea, ValueTask connectTask, CancellationToken cancellationToken)
[2025-10-01T23:55:26.785Z]    at System.Net.Http.HttpConnectionPool.ConnectToTcpHostAsync(String host, Int32 port, HttpRequestMessage initialRequest, Boolean async, CancellationToken cancellationToken)
[2025-10-01T23:55:26.786Z]    --- End of inner exception stack trace ---
[2025-10-01T23:55:26.786Z]    at System.Net.Http.HttpConnectionPool.ConnectToTcpHostAsync(String host, Int32 port, HttpRequestMessage initialRequest, Boolean async, CancellationToken cancellationToken)
[2025-10-01T23:55:26.788Z]    at System.Net.Http.HttpConnectionPool.ConnectAsync(HttpRequestMessage request, Boolean async, CancellationToken cancellationToken)
[2025-10-01T23:55:26.789Z]    at System.Net.Http.HttpConnectionPool.CreateHttp11ConnectionAsync(HttpRequestMessage request, Boolean async, CancellationToken cancellationToken)
[2025-10-01T23:55:26.790Z]    at System.Net.Http.HttpConnectionPool.AddHttp11ConnectionAsync(QueueItem queueItem)    
[2025-10-01T23:55:26.790Z]    at System.Threading.Tasks.TaskCompletionSourceWithCancellation`1.WaitWithCancellationAsync(CancellationToken cancellationToken)
[2025-10-01T23:55:26.791Z]    at System.Net.Http.HttpConnectionPool.SendWithVersionDetectionAndRetryAsync(HttpRequestMessage request, Boolean async, Boolean doRequestAuth, CancellationToken cancellationToken)
[2025-10-01T23:55:26.792Z]    at System.Net.Http.HttpClient.<SendAsync>g__Core|83_0(HttpRequestMessage request, HttpCompletionOption completionOption, CancellationTokenSource cts, Boolean disposeCts, CancellationTokenSource pendingRequestsCts, CancellationToken originalCancellationToken)
[2025-10-01T23:55:26.793Z]    at Azure.Core.Pipeline.HttpClientTransport.ProcessSyncOrAsync(HttpMessage message, Boolean async)
[2025-10-01T23:55:26.839Z]    --- End of inner exception stack trace ---
[2025-10-01T23:55:26.859Z]    at Azure.Core.Pipeline.HttpClientTransport.ProcessSyncOrAsync(HttpMessage message, Boolean async)
[2025-10-01T23:55:26.860Z]    at Azure.Core.Pipeline.HttpPipelineTransportPolicy.ProcessAsync(HttpMessage message, ReadOnlyMemory`1 pipeline)
[2025-10-01T23:55:26.861Z]    at Azure.Core.Pipeline.ResponseBodyPolicy.ProcessAsync(HttpMessage message, ReadOnlyMemory`1 pipeline, Boolean async)
[2025-10-01T23:55:26.862Z]    at Azure.Core.Pipeline.LoggingPolicy.ProcessAsync(HttpMessage message, ReadOnlyMemory`1 pipeline, Boolean async)
[2025-10-01T23:55:30.263Z] Request [f27ef14f-60fe-4bc8-b032-4eb9d22f2f01] attempt number 3 took 02.2s
[2025-10-01T23:55:30.264Z] Request [f27ef14f-60fe-4bc8-b032-4eb9d22f2f01] HEAD http://127.0.0.1:10000/devstoreaccount1/azure-webjobs-hosts/locks/avd1371-2113432517/host
[2025-10-01T23:55:30.264Z] x-ms-version:2024-08-04
[2025-10-01T23:55:30.265Z] Accept:application/xml
[2025-10-01T23:55:30.265Z] x-ms-client-request-id:f27ef14f-60fe-4bc8-b032-4eb9d22f2f01
[2025-10-01T23:55:30.266Z] x-ms-return-client-request-id:true
[2025-10-01T23:55:30.266Z] User-Agent:azsdk-net-Storage.Blobs/12.21.2 (.NET 8.0.19; Microsoft Windows 10.0.22631)    
[2025-10-01T23:55:30.267Z] x-ms-date:Wed, 01 Oct 2025 23:55:30 GMT
[2025-10-01T23:55:30.268Z] Authorization:REDACTED
[2025-10-01T23:55:30.268Z] client assembly: Azure.Storage.Blobs
[2025-10-01T23:55:32.311Z] Request [f27ef14f-60fe-4bc8-b032-4eb9d22f2f01] exception Azure.RequestFailedException: No connection could be made because the target machine actively refused it. (127.0.0.1:10000)
[2025-10-01T23:55:32.312Z]  ---> System.Net.Http.HttpRequestException: No connection could be made because the target machine actively refused it. (127.0.0.1:10000)
[2025-10-01T23:55:32.313Z]  ---> System.Net.Sockets.SocketException (10061): No connection could be made because the target machine actively refused it.
[2025-10-01T23:55:32.314Z]    at System.Net.Sockets.Socket.AwaitableSocketAsyncEventArgs.ThrowException(SocketError error, CancellationToken cancellationToken)
[2025-10-01T23:55:32.314Z]    at System.Net.Sockets.Socket.AwaitableSocketAsyncEventArgs.System.Threading.Tasks.Sources.IValueTaskSource.GetResult(Int16 token)
[2025-10-01T23:55:32.315Z]    at System.Net.Sockets.Socket.<ConnectAsync>g__WaitForConnectWithCancellation|285_0(AwaitableSocketAsyncEventArgs saea, ValueTask connectTask, CancellationToken cancellationToken)
[2025-10-01T23:55:32.316Z]    at System.Net.Http.HttpConnectionPool.ConnectToTcpHostAsync(String host, Int32 port, HttpRequestMessage initialRequest, Boolean async, CancellationToken cancellationToken)
[2025-10-01T23:55:32.316Z]    --- End of inner exception stack trace ---
[2025-10-01T23:55:32.317Z]    at System.Net.Http.HttpConnectionPool.ConnectToTcpHostAsync(String host, Int32 port, HttpRequestMessage initialRequest, Boolean async, CancellationToken cancellationToken)
[2025-10-01T23:55:32.392Z]    at System.Net.Http.HttpConnectionPool.ConnectAsync(HttpRequestMessage request, Boolean async, CancellationToken cancellationToken)
[2025-10-01T23:55:32.394Z]    at System.Net.Http.HttpConnectionPool.CreateHttp11ConnectionAsync(HttpRequestMessage request, Boolean async, CancellationToken cancellationToken)
[2025-10-01T23:55:32.394Z]    at System.Net.Http.HttpConnectionPool.AddHttp11ConnectionAsync(QueueItem queueItem)    
[2025-10-01T23:55:32.395Z]    at System.Threading.Tasks.TaskCompletionSourceWithCancellation`1.WaitWithCancellationAsync(CancellationToken cancellationToken)
[2025-10-01T23:55:32.395Z]    at System.Net.Http.HttpConnectionPool.SendWithVersionDetectionAndRetryAsync(HttpRequestMessage request, Boolean async, Boolean doRequestAuth, CancellationToken cancellationToken)
[2025-10-01T23:55:32.397Z]    at System.Net.Http.HttpClient.<SendAsync>g__Core|83_0(HttpRequestMessage request, HttpCompletionOption completionOption, CancellationTokenSource cts, Boolean disposeCts, CancellationTokenSource pendingRequestsCts, CancellationToken originalCancellationToken)
[2025-10-01T23:55:32.398Z]    at Azure.Core.Pipeline.HttpClientTransport.ProcessSyncOrAsync(HttpMessage message, Boolean async)
[2025-10-01T23:55:32.398Z]    --- End of inner exception stack trace ---
[2025-10-01T23:55:32.399Z]    at Azure.Core.Pipeline.HttpClientTransport.ProcessSyncOrAsync(HttpMessage message, Boolean async)
[2025-10-01T23:55:32.400Z]    at Azure.Core.Pipeline.HttpPipelineTransportPolicy.ProcessAsync(HttpMessage message, ReadOnlyMemory`1 pipeline)
[2025-10-01T23:55:32.400Z]    at Azure.Core.Pipeline.ResponseBodyPolicy.ProcessAsync(HttpMessage message, ReadOnlyMemory`1 pipeline, Boolean async)
[2025-10-01T23:55:32.401Z]    at Azure.Core.Pipeline.LoggingPolicy.ProcessAsync(HttpMessage message, ReadOnlyMemory`1 pipeline, Boolean async)
[2025-10-01T23:55:40.107Z] Request [f27ef14f-60fe-4bc8-b032-4eb9d22f2f01] attempt number 4 took 02.2s
[2025-10-01T23:55:40.109Z] Request [f27ef14f-60fe-4bc8-b032-4eb9d22f2f01] HEAD http://127.0.0.1:10000/devstoreaccount1/azure-webjobs-hosts/locks/avd1371-2113432517/host
[2025-10-01T23:55:40.111Z] x-ms-version:2024-08-04
[2025-10-01T23:55:40.111Z] Accept:application/xml
[2025-10-01T23:55:40.112Z] x-ms-client-request-id:f27ef14f-60fe-4bc8-b032-4eb9d22f2f01
[2025-10-01T23:55:40.112Z] x-ms-return-client-request-id:true
[2025-10-01T23:55:40.113Z] User-Agent:azsdk-net-Storage.Blobs/12.21.2 (.NET 8.0.19; Microsoft Windows 10.0.22631)    
[2025-10-01T23:55:40.113Z] x-ms-date:Wed, 01 Oct 2025 23:55:40 GMT
[2025-10-01T23:55:40.245Z] Authorization:REDACTED
[2025-10-01T23:55:40.246Z] client assembly: Azure.Storage.Blobs
[2025-10-01T23:55:41.592Z] Stopping host...
[2025-10-01T23:55:41.599Z] Stopping JobHost
[2025-10-01T23:55:41.632Z] Stopping the listener 'Microsoft.Azure.WebJobs.ServiceBus.Listeners.ServiceBusListener' for function 'replication_fuction'