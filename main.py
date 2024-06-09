import base64
import functions_framework
import json
import os
import sendgrid
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content

# Project ID and topic details (replace placeholders)
project_id = "{yourprojectid}"
topic_name = "parts_status"

def send_email(recipient, faulty_parts):
    sendgrid_api_key = "{yourapikey}"

    message = Mail(
        from_email=Email("yoursenderemail"), 
        to_emails=[To(recipient)],                  
        subject="Faulty Parts Alert",
        html_content=Content("text/html", f"The following parts are faulty: <br> {', '.join(faulty_parts)}")
    )

    try:
        sg = SendGridAPIClient(sendgrid_api_key)
        response = sg.send(message)

        if 200 <= response.status_code < 300:
            print(f"Email sent to {recipient} successfully.")
        else:
            print(f"Email to {recipient} failed with status code: {response.status_code}")

    # Catch specific SendGrid exceptions
    except sendgrid.SendGridException as e:
        print(f"SendGrid Error: {e}") 


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

            # Send notification email with part ID
            send_email("{yourreceiveremail}", [part_id])
        else:
            print("Message is not 'faulty', skipping notification.")

    except (KeyError, json.JSONDecodeError):
        print("Error parsing message data or missing fields.")