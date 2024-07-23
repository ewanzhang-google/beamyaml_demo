import base64
import functions_framework
import json
from google.cloud import logging

# Project ID and topic details 
project_id = "ryanmadden"
topic_name = "parts_status"

# Logging client
logging_client = logging.Client()
logger = logging_client.logger("faulty_parts_alert")  # Create a logger with a specific name

@functions_framework.cloud_event
def faulty_alert(cloud_event):
    # Decode message data
    message_data = base64.b64decode(cloud_event.data["message"]["data"]).decode("utf-8")
    
    try:
        # Parse JSON message
        message_json = json.loads(message_data)

        # Check if the status is 'faulty'
        if message_json["status"] == "faulty":
            part_id = message_json["part_id"]

            # Log an error to trigger an alert in Cloud Monitoring
            logger.log_struct(
                {
                    "message": "Faulty Parts Alert", 
                    "faulty_parts": part_id
                }, 
                severity="ERROR"  # Set the severity to ERROR to trigger alerts
            )

        else:
            print("Message is not 'faulty', skipping notification.")

    except (KeyError, json.JSONDecodeError):
        print("Error parsing message data or missing fields.")