import requests
from pprint import pprint
from tasty_api.session import Session
from pathlib import Path

url = "https://api.cert.tastyworks.com"
user_name = "your_username"  # Replace with your username


def main():
    # Pull the remember-me token from .tastyworks_token file

    with open(Path(".tastyworks_token"), "r") as f:
        remember_token = f.read().strip()

    try:
        trading_session = Session.from_remember_token(user_name, remember_token)
        trading_session.login()
        print(trading_session.session_id)
        trading_session.dump_remember_token(Path(".tastyworks_token"))
        # trading_session.logout() # Logging out will
    except Exception as e:
        print(f"Error: {e}")
        # Delete the remember-me token file if login fails
        Path(".tastyworks_token").unlink(missing_ok=True)
        print("Deleted .tastyworks_token file.")

    # Get me as a person
    # response = requests.get(
    #     f"{url}/customers/me",
    #     headers=header,
    # )
    # pprint(response.json())

    # # Get my accounts
    # response = requests.get(
    #     f"{url}/customers/me/accounts",
    #     headers=header,
    # )
    # pprint(response.json())

    # # Retrieve my account number and get the account details
    # account_number = response.json()["data"]["items"][0]["account"]["account-number"]
    # response = requests.get(
    #     f"{url}/customers/me/accounts/{account_number}",
    #     headers=header,
    # )
    # pprint(response.json())

    # # Print my balance
    # response = requests.get(
    #     f"{url}/accounts/{account_number}/balances",
    #     headers=header,
    # )
    # print(response.status_code)
    # pprint(response.json())

    # Destroy a session
    # response = requests.delete(
    #     f"{url}/sessions",
    #     json={"Authorization": "session_token"},
    # )


if __name__ == "__main__":
    main()
