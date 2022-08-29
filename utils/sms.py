import os
import vonage
from fastapi import HTTPException, status

client = vonage.Client(key=os.environ.get('VONAGE_KEY'), secret=os.environ.get('VONAGE_SECRET'))
sms = vonage.Sms(client)


async def send_sms(code: str, phone: str):
    """
    Sending a message to the user for confirmation

    :param code: str
    :param phone: str
    :return: bool -> success send sms; HTTPException -> An error occurred while sending
    """
    response_data = sms.send_message(
        {
            "from": "Bob Dylan",
            "to": phone,
            "text": f"Your verification code for the VA application: {code} ",
        }
    )

    if response_data["messages"][0]["status"] == "0":
        return True
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An error occurred while submitting the code"
        )
