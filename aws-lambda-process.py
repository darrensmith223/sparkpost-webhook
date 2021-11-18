import json, boto3, csv, os, botocore

def lambda_handler(event, context):
  
    r = event.get("Records")[0]
    event_name = r.get('eventName')
    if  event_name!= 'ObjectCreated:Put':
      print('Unexpected eventName', event_name)
      return

    info = r.get('s3')
    if info == None:
       print('Missing s3 information')
       return
     
    bucket_name = info.get('bucket').get('name')
    if bucket_name == None:
       print('Missing s3.bucket.name information')
       return
      
    obj = info.get('object')
    if obj == None:
      print('Missing s3.object information')
      return

    batch_id =  obj.get('key').split("/")[-1]
    if batch_id == None:
      return
            
    # Read New File
    s3_client = boto3.client('s3')
    obj = s3_client.get_object(Bucket=str(bucket_name), Key=str(obj.get('key')))
    try:
        events = json.load(obj.get('Body'))
        print(events)
        print(type(events))
    except botocore.exceptions.ClientError as err:
        print(err)
    
    file_name = str(batch_id) + ".csv"
    file_path = "/tmp/" + file_name
    
    # Create temp file
    with open(file_path, "w") as file:
        csv_writer = csv.writer(file)
        active_event_types = ['track_event', 'message_event', 'gen_event', 'unsubscribe_event']
        for iteration, i in enumerate(events):
            record = i.get('msys')
            
            # Search for included event types
            for t in active_event_types:
                if t in record:
                    event = record.get(t)
                    if iteration == 0:
                        # Writing headers of CSV file
                        header = event.keys()
                        csv_writer.writerow(header)
     
                    # Writing data of CSV file
                    csv_writer.writerow(event.values())
                    break
      
    body = open('/tmp/' + file_name, 'rb').read()
    
    # Delete temp file
    os.remove('/tmp/' + file_name)
    
    # Store in S3
    store_batch(s3_client, body, file_name)

    return {
        'statusCode': 200,
        'body': 'Done'
    }
 
def store_batch(s3_client, body, file_name):
    bucket_name = 'sparkpost-webhook-csv'
    path = 'SP Event Data/' + str(file_name)
    try:
        try:
            _ = s3_client.get_object(Bucket=bucket_name, Key=path)
            return

        except botocore.exceptions.ClientError as err:
            e = err.response['Error']['Code']
            if e in ['NoSuchKey', 'AccessDenied']:
                # Forward path. Object does not exist already, so try to create it
                s3_client.put_object(Body=body, Bucket=bucket_name, Key=path)
            else:
                print(err)

    except Exception as err:
        print(err)
        return
