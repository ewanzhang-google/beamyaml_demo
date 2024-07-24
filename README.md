# beamYAML/Visual Job Builder demo
## This demo is showing an end to end pipeline processing car part inspection events to report on manufactoring status realtime and report on faulty parts.

## Step 1 - Streaming Source Data Generation
Use [Streaming Data Generator Dataflow teamplate](https://cloud.google.com/dataflow/docs/guides/templates/provided/streaming-data-generator) to generate raw car part inspection events, by using the schema defiition specified in the [parts_schema.json](https://github.com/ewanzhang-google/beamyaml_demo/blob/main/parts_schema.json) file. Output the data stream to a PubSub topic called 'parts_raw'.

Detailed steps:
- Go to 'Dataflow'->'Jobs', click 'CREATE JOB FROM TEMPLATE'
- Choose 'Streaming Data Generator' at the 'Dataflow template' drop-down box
- Complete the required fields and leave the rest as default\
[Job name]: parts-generation\
[Required output rate]: 5\
Tick 'Enable Streaming Engine'\
[Location of Schema file to generate fake data]: point to your own storage location where you have uploaded the [parts_schema.json](https://github.com/ewanzhang-google/beamyaml_demo/blob/main/parts_schema.json) file file to\
[Output Pub/Sub topic]: create new topic parts_raw\
Click 'RUN JOB'

![s1](/screenshots/s1.png?raw=true)
![s2](/screenshots/s2.png?raw=true)


## Step 2 - beamYAML/Visual Job Builder Execution
**Option 1:** follow the steps outlined in the [beam.yaml](https://github.com/ewanzhang-google/beamyaml_demo/blob/main/beam.yaml) file to run through the job build, the detailed steps are:
- Go to 'Dataflow'->'Jobs', click 'CREATE JOB FROM TEMPLATE', toggle to 'Job builder'
- Complete the pipeline steps one by one\
[Job name]: quality-check\
[Job type]: choose 'Streaming', select 'Fixed' for windowing and 180 for size\
**Sources:**\
[Source name]: source\
[Source type]: Pub/Sub Topic\
[Pub/Sub topic]: choose the topic we created above parts_raw\
[Message schema]: fill out the field names and types are below:\
part_id: {type: string}\
point_of_time: {type: string}\
part_type: {type: string}\
length: {type: integer}\
thickness: {type: integer}\
weights: {type: integer}\
**Transforms:**\
Click 'ADD A TRANSFORM'for our first transform\
[Transform name]: Filter\
[Transform type]: Choose 'Filter(Python)'\
[Python filter expression]: part_type == 'piston' or part_type == 'connecting rod' or part_type == 'crankshaft'\
Click 'DONE' and 'ADD A TRANSFORM' for our second transform\
[Transform name]: Map\
[Transform type]: Choose 'Map Fields(SQL)'\
Choose 'Preserve existing fields'\
Click 'ADD A FIELD'\
[Field name]: status\
[SQL expression]: CASE WHEN length <= 20 AND length >= 40 THEN 'faulty'  WHEN thickness <= 5 AND thickness >= 10 THEN 'faulty'  WHEN weights <= 200 AND weights >= 600 THEN 'faulty'  ELSE 'not faulty' END\
Click 'DONE' and 'DONE'\
**Sinks:**\
Click 'ADD A SINK' for our first sink\
[Sink name]: BigQuery\
[Sink type]: BigQuery Table\
Click 'Create new table' and fill out the box for Dataset and Table information such as sink.check_result\
Click 'DONE' and 'ADD A SINK' for our second sink\
[Sink name]: PubSub\
[Sink type]: Pub/Sub topic\
[Pub/Sub topic]: create a new topic called parts_status\
Click 'DONE'\
Leave the rest as it and click 'RUN JOB'

![s3](/screenshots/s3.png?raw=true)
![s4](/screenshots/s4.png?raw=true)
![s5](/screenshots/s5.png?raw=true)
![s6](/screenshots/s6.png?raw=true)
![s7](/screenshots/s7.png?raw=true)
![s8](/screenshots/s8.png?raw=true)

**Option 2:** load the job directly from the [beam.yaml](https://github.com/ewanzhang-google/beamyaml_demo/blob/main/beam.yaml) file, the detailed steps are:
- Replace {yourprojectid} with your project id in the yaml file\
- Copy the code\
- Go to 'Dataflow'->'Jobs', click 'CREATE JOB FROM TEMPLATE', toggle to 'Job builder'\
- Find 'LOAD'->'Load from text' at the top right hand side of the UI\
- Paste the code in there and click 'LOAD'\
- Complete the build and click 'RUN JOB'


![s9](/screenshots/s9.png?raw=true)

**Option 3:** run the gcloud command to execute the local yaml file directly like this:\
```gcloud dataflow yaml run quality-check --yaml-pipeline-file=beam.yaml --region=us-central1```

## Step 3 - BigQuery Status Check
The following queries can be run to understand the latest statistics of the faulty status and faulty rate:
```
SELECT 
part_id, TIMESTAMP_MILLIS(CAST(`point_in_time` AS INT64)), part_type
FROM sinks.check_result
WHERE status = 'faulty'
ORDER BY point_in_time

SELECT 
    TIMESTAMP_BUCKET(TIMESTAMP_MILLIS(CAST(`point_in_time` AS INT64)), INTERVAL 10 MINUTE) AS timeunit,
    FORMAT("%.*f%%", 2, (COUNTIF(status = 'faulty')) / COUNT(*) * 100) AS faulty_percentage 
FROM sinks.check_result
GROUP BY timeunit
ORDER BY timeunit;
```


## (Optional) Step 4 - Cloud Function Notification Alert
This optional step will set up a Cloud Function service to subscribe to the 'parts_status' topic and log an error whenever it sees a faulty part. And we can be notified once we create an alerting policy on our custom log metric. The detailed steps are as follows:

- Create a Cloud Function service using the code snippet in [main.py](https://github.com/ewanzhang-google/beamyaml_demo/blob/main/main.py) and [requirements.txt](https://github.com/ewanzhang-google/beamyaml_demo/blob/main/requirements.txt) files, the Cloud Function will be triggered by events landing in the PubSub topic 'parts_status'
- Create a log-based metric in Cloud Logging on below filter\
```severity="ERROR" jsonPayload.message="Faulty Parts Alert"```

![s10](/screenshots/s10.png?raw=true)
- Create an alerting policy on the above metric to count the number of logs in a rolling window of 10 minutes and alert to an email everytime it goes over the threshold of 0
![s11](/screenshots/s11.png?raw=true)
![s12](/screenshots/s12.png?raw=true)
