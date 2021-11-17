import json, boto3, csv, os

def lambda_handler(event, context):
  
    event_name = r.get('eventName')
    if  event_name!= 'ObjectCreated:Put':
      print('Unexpected eventName', event_name)
      continue

    info = r.get('s3')
    if info == None:
       print('Missing s3 information')
       continue
     
    bucket_name = info.get('bucket').get('name')
    if bucket_name == None:
       print('Missing s3.bucket.name information')
       continue
      
    obj = info.get('object')
    if obj == None:
      print('Missing s3.object information')
      continue

    batch_id =  obj.get('key')
    if batch_id == None:
      print('Missing s3.object.key information')
      continue
            
    file_name = str(batch_id) + ".csv"
    
    # Create temp file
    with open("/tmp/" + file_name, "w") as file:
      for iteration, record in enumerate(event.get("Records")):
        if iteration == 1:
          # Writing headers of CSV file
          header = record.keys()
          csv_writer.writerow(header)
 
        # Writing data of CSV file
        csv_writer.writerow(record.values())
      
    body = open('/tmp/' + file_name, 'rb').read()
    
    # Delete temp file
    os.remove('/tmp/' + file_name)
    
    # Store in S3
    s3_client = boto3.client('s3')
    store_batch(s3_client, body, file_name)

    return {
        'statusCode': 200,
        'body': 'Done'
    }
 
def store_batch(s3_client, body, file_name):
    bucket_name = 'sparkpost-webhooks'
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
