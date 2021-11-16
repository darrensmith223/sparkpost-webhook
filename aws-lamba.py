def lambda_handler(event, context):
    
    headers = event.get('headers')
    batch_id = headers.get('x-messagesystems-batch-id')
    body = event.get('body')
    
    # store file in S3
    s3_client = boto3.client('s3')
    store_batch(s3_client, body, batch_id)

    return {
        'statusCode': 200,
        'body': 'Done'
    }


def store_batch(s3_client, body, batch_id):
    bucket_name = 'sparkpost-webhooks'
    path = 'SP Event Data/' + str(batch_id)
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
