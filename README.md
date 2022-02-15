# Creating and Consuming SparkPost Webhooks

SparkPost’s real-time [event webhooks](https://developers.sparkpost.com/api/webhooks/?_ga=2.154113720.1830737125.1636982825-1879043862.1633361783) are an incredibly valuable tool for senders to have data automatically pushed to their systems. This can drive downstream automation such as updating mailing lists, triggering automated email journeys, or populating internal dashboards.  While the same event data can be accessed via the SparkPost UI using [Event Search](https://app.sparkpost.com/reports/message-events), or programmatically by leveraging the SparkPost [Events API](https://developers.sparkpost.com/api/events/), limitations placed on the number of records returned in a single request or rate limits placed on the API endpoint can make both of these methods restrictive for large and sophisticated senders.  

Real-time event webhooks enable a sender to configure an endpoint where SparkPost transmits the data to, and the data can be consumed without having to schedule cron jobs that pull the data.  There are also logistical trade-offs when pulling the data as opposed to having the data pushed to you, such as having to identify what time period and parameters to use for each API request.  If the time periods are not lined up perfectly then you risk missing data, and if the time periods overlap then you need to handle duplicate data records.  With real-time webhooks, event data is simply pushed to your endpoint as it becomes available within SparkPost.

While the benefits of receiving event data in real-time to drive downstream automation processes may be immediately understood by many senders, the actual process for implementing and consuming webhooks may be intimidating.  This can be especially true if you are unfamiliar with the technical components of creating an endpoint and handling the data programmatically.

There are services available that will consume SparkPost webhook data and ETL into your database automatically - an example would be [StitchData](https://www.stitchdata.com/integrations/sparkpost/), which SparkPost has [blogged about in the past](https://www.sparkpost.com/blog/sparkpost-postgresql/).  However, if you would like more control over the process you can easily build the components yourself.  The following is a simple guide to help senders feel comfortable when creating a SparkPost Events Webhook and consuming the data using the infrastructure within AWS.

## Configuring Webhook Target Endpoint

When a SparkPost event is created, we want that event data to be streamed in real-time to an endpoint in AWS so that we can consume and use that data programmatically.  The data will be sent from SparkPost to a target endpoint, which will forward the payload to a Lambda function that will process and store the data in an S3 bucket.  A high-level diagram of the described data flow can be seen below:

![Flowchart](/img/webhook_flowchart.png)

### Steps

I've found the easiest way to implement the above workflow is to actually build them in the reverse order beginning with creating an S3 bucket where we will store our event data and then work backwards - adding each component that feeds into what we’ve built.


* Create S3 Bucket
* Create a Lambda Function to Consume the Data - sample function is included in this project where the webhook payload is stored in S3
* Create an Application Load Balancer
* Create a DNS Record for the Load Balancer
* Create a SparkPost Webhook


## Processing Webhook Event Data

Depending on the intended purpose for storing the SparkPost event data, your requirements may be satisfied by simply storing the JSON payload as a flat-file.  You may also have a downstream ETL process already established that is capable of consuming and loading data in a JSON format.  In both of these cases, you may be able to use the flat-file created by our processing lambda that we created above as-is.

Alternatively, you may need to transform the data - such as to convert from a JSON to a CSV format - or load the data directly into a database.  In this example we will create a simple lambda function that will convert the webhook data from the original JSON format into a CSV file that could be loaded into a database. 

### Steps

* Create a Lambda to Process the Data - sample function is included in this project where the data is converted into a csv
* Configure a Lambda to Execute When New Data is Stored on S3 - add trigger to lambda function for when a new file is created on the input S3 bucket

## Getting More Information

More information and detail can be found in the [associated blog post](https://www.sparkpost.com/blog/creating-and-consuming-sparkpost-webhooks/)


