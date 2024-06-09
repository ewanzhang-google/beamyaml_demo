# beamYAML/Visual Job Builder demo
## This demo is showing an end to end pipeline processing car part inspection events to report on manufactoring status realtime and report on faulty parts.

## Step 1 - Streaming Source Data Generation
Use Streaming Data Generator Dataflow teamplate to generate raw car part inspection events, by using the schema defiition specified in the parts_schema.json file. Output the data stream to a PubSub topic called 'parts_raw'.

## Step 2 - beamYAML/Visual Job Builder Execution
Follow the steps outlined in the beam.yaml file to run through the job execution, which includes:
1. connect to the data source PubSub topic 'parts_raw'
2. filter on part_type for engine related parts
3. apply rule-based function on three different measurements of the part to determine if the part is faulty or not faulty, assign the value to a new column called 'status'
4. output the result to a new PubSub topic called 'parts_status' as well as a BigQuery table called 'check_result'

You can also called the gcloud command to execute the yaml file directly like this:\
```gcloud dataflow yaml run quality-check --yaml-pipeline-file=beam.yaml --region=us-central1```

## Step 3a - Cloud Function Notification Alert
First of all refer to the online guide to create SendGrid account and api keys (in my case sending email from my personal gmail account will remove the security restriction otherwise experienced with corporated emails). 

Once the configuration is complete on SendGrid proceed to creating a Cloud Function using the code snippet in main.py and requirements.txt files, the Cloud Function will be triggered by events landing in the PubSub topic 'parts_status'

The alert email will look like this:

Title: "Faulty Parts Alert"\
Body: "The following parts are faulty:33cb9ba7-1f0f-451f-ac4c-aafda52bfa9f"

## Step 3b - BigQuery Status Check
The following queries can be run to understand the latest statistics of the faulty status and faulty rate:
```
SELECT 
part_id, TIMESTAMP_MILLIS(CAST(`point_of_time` AS INT64)), part_type
FROM sinks.check_result
WHERE status = 'faulty'
ORDER BY point_of_time

SELECT 
    TIMESTAMP_BUCKET(TIMESTAMP_MILLIS(CAST(`point_of_time` AS INT64)), INTERVAL 10 MINUTE) AS timeunit,
    FORMAT("%.*f%%", 2, (COUNTIF(status = 'faulty')) / COUNT(*) * 100) AS faulty_percentage 
FROM sinks.check_result
GROUP BY timeunit
ORDER BY timeunit;```