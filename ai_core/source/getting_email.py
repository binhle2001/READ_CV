import logging
import os
import datetime
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from oauth2client.client import flow_from_clientsecrets
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
from api.helpers.s3_config import s3
from api.helpers.common import get_cv_file_s3_path, get_env_var
from api.schema import CVSender

# If modifying these scopes, delete the file token.pickle.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly", "https://www.googleapis.com/auth/gmail.modify"]

def get_credentials(tenant):
    """Gets valid user credentials from storage or runs the OAuth 2.0 authorization flow if no valid credentials are available."""
    creds = None
    if os.path.exists(f'ai_core/token/{tenant}.json'):
        creds = Credentials.from_authorized_user_file(f'ai_core/token/{tenant}.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
    return creds



def get_attachment(tenant_id):
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = get_credentials(tenant_id)
    if not creds:
        logging.error("Please check authorized user file exist!")
        return None
    service = build('gmail', 'v1', credentials=creds)
    if tenant_id not in CVSender.list_email_address_sender:
        return None
    try:
        # Call the Gmail API
        results = service.users().labels().list(userId="me").execute()
        labels = results.get("labels", [])

        follow_up_label_id = None
        for label in labels:
            if label["name"] in CVSender.list_email_address_sender[tenant_id]["label"]:
                follow_up_label_id = label["id"]
                break

        if follow_up_label_id:
            # Construct the query for filtering by sender, label, and unread status
            data_cv = []
            for i in range(len(CVSender.list_email_address_sender[tenant_id]["email_address"])):
                email = CVSender.list_email_address_sender[tenant_id]["email_address"][i]
                label = CVSender.list_email_address_sender[tenant_id]["label"][i]
                status = CVSender.list_email_address_sender[tenant_id]["status"][i]
                query = f'from:{email} label:{label}'

                # Retrieve emails matching the query
                messages = service.users().messages().list(userId="me", q=query).execute()

                for message in messages.get("messages", []):
                    msg = service.users().messages().get(userId="me", id=message["id"]).execute()
                    snippet = msg["snippet"]
                    
                    # Check for attachments
                    if "parts" in msg["payload"]:
                        for part in msg["payload"]["parts"]:

                            
                            if part["filename"]:
                                # Decode attachment data
                                attachment = (
                                    service.users()
                                    .messages()
                                    .attachments()
                                    .get(
                                        userId="me",
                                        messageId=message["id"],
                                        id=part["body"]["attachmentId"],
                                    ).execute()
                                )
                                data = base64.urlsafe_b64decode(attachment["data"].encode("UTF-8"))
                                # Save attachment to file
                                os.makedirs(f"ai_core/data_cv/{tenant_id}/", exist_ok= True)
                                with open(f"ai_core/data_cv/{tenant_id}/" + part["filename"], "wb") as f:
                                    f.write(data)
                                with open(f"ai_core/data_cv/{tenant_id}/" + part["filename"], "rb") as f:
                                    s3.upload_fileobj(f, get_env_var('s3', 'AWS_S3_BUCKET_NAME'), get_cv_file_s3_path(tenant_id) + part["filename"])
                                service.users().messages().modify(userId="me", id=message["id"], body={"removeLabelIds": ["UNREAD"]}).execute()
                                
                                data_cv.append({
                                    "snippet": snippet,
                                    "attachment":f"ai_core/data_cv/{tenant_id}/" + part["filename"],
                                    "link_cv": f"https://{get_env_var('s3', 'AWS_S3_BUCKET_NAME')}.s3.{get_env_var('s3', 'AWS_REGION_NAME')}.amazonaws.com/{get_cv_file_s3_path(tenant_id)}{part['filename']}"
                                })
                                
                                
                                
                    
                    # Mark the email as read
                    service.users().messages().modify(userId="me", id=message["id"], body={"removeLabelIds": ["UNREAD"]}).execute()
                    data_cv.append({
                                    "snippet": snippet,
                                    "attachment": None
                                })      
            return data_cv

                    

    except HttpError as error:
        # Handle errors from Gmail API
        print(f"An error occurred: {error}")

if __name__ == "__main__":
    get_attachment()
