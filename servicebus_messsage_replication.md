Service Bus message replication for Tier-1 solutions
Status: Draft
Date Last Updated: July 31, 2025
Date Approved: 
Summary
Custom message replication for Service Bus messages has been selected to implement the new Service Bus pattern. 
This pattern provides Tier-1 support where messages get replicated across Azure regions to meet resiliency requirements.
Context
We need the messages on the Azure bus service to be replicated to the secondary region to meet the Tier 1 requirements and overcome any message loss during the regional failures or any Service Bus outage.
This is a tactical solution until Microsoft releases the final solution for Message queue service 
For the above-mentioned reasons, Infosys Team needs to provide a solution that:
-	Replicates the messages from the primary region to the secondary region.
-	Ensures that the replication solution is resilient
-	Ensures that already processed in the primary region do not get sent to the secondary region topic
-	Easy to debug and maintain
-	Low cost for the solution
Decision/Solution
 

 

1.	Develop a new Function App that will pull messages from the primary region to the secondary region Service Bus.
2.	Create a new Subscription of the existing Service Bus Topic in the primary region.
3.	During the replication, Time to Live (TTL) message property will be set by the Function code to a duration (RTO+delta) on the message that reflects the expected time during which a failure of the primary will lead to a failover.
4.	The replication will be one way where the Function code will consume messages from primary and replicate to the secondary Service Bus.
5.	Post failover and after the old primary Service Bus has come online, replication would happen in reverse order – from secondary to the old primary region Service Bus.

Azure Monitor Based Alerts
1.	Monitor specific alerts for Service Bus metrics for conditions based on throttled requests, dead letter messaging, CPU/memory usage etc. will be provided.
2.	Service Health alerts for the regionwide Service Bus outage will be provided.

Consequences
1.	As mentioned above a TTL of the message that need to be replicated to the secondary region will be changed to a value – RTO + delta.
2.	If Recovery time actual does not meet recovery time objective and messages might be deleted without being consumed.
3.	This solution assumes that the consumer of the messages can consume the messages in a timely manner.
4.	There is a possibility that the secondary region’s subscription consumer gets already processed messages. This has the risk of generating a swarm of false notifications that can lead to chaos.
5.	The RTO will be tested as a part of the migration process. Once testing is complete, we will update the TTL to match RTO+10 minutes. This should give buffer time to ensure messages are not lost.
6.	A solution could be developed to manually increase the TTL of the messages after they have been placed in a intermediate Topic. However, this adds additional complexity and edge cases that need to be handled hence it will be looked into in future design updates.

Cost of the Consequences
The only additional cost that would incur in this solution is for the new Function App that would use App Service Plan based host instances and the Azure Monitor Metrics based Service Bus alerts that are minimal.
We will go with Premium tier P1V2, 1 vCPU, 3.5 GB RAM, 250 GB Storage. For this configuration a Linux based instance will cost about $80/month and $146 for a Windows. We will be charged extra if we scale beyond 1 instance.
To save cost further we can leverage the existing App Service Plan to host Function Apps. This would not incur any additional cost. 
 
