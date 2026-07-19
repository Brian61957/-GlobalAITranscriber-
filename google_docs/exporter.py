from googleapiclient.discovery import build
from google_docs.auth import authenticate


def create_document(
        title,
        transcript,
        translation,
        confidence
):

    creds = authenticate()

    service = build(
        "docs",
        "v1",
        credentials=creds
    )

    document = service.documents().create(
        body={
            "title": title
        }
    ).execute()

    document_id = document["documentId"]

    text = f"""
Transcript

{transcript}


English Translation

{translation}


Confidence

{confidence}%
"""

    service.documents().batchUpdate(
        documentId=document_id,
        body={
            "requests": [
                {
                    "insertText": {
                        "location": {
                            "index": 1
                        },
                        "text": text
                    }
                }
            ]
        }
    ).execute()

    return document_id