from pathlib import Path

import typer
from rich import print
from typing_extensions import Annotated

from tasty_api import errors
from tasty_api.customer import Customer
from tasty_api.session import Session

url = "https://api.cert.tastyworks.com"


def main(
    username: Annotated[
        str,
        typer.Argument(help="The username of the client attempting to access the API."),
    ],
    password: Annotated[
        str,
        typer.Option(
            help="The password of the user. It will attempt to login with a remember-me token before using the password."
        ),
    ] = None,
    logout: Annotated[
        bool,
        typer.Option(
            "--logout",
            "-l",
            help="Logout from the Tastyworks API.",
        ),
    ] = False,
):
    """Logs into the Tastyworks API to perform various actions such as getting account information, making trades, watching the market, etc."""
    trading_session = None
    try:
        print("Attempting login in with remember-me token...")
        with open(Path(".tastyworks_token"), "r") as f:
            remember_token = f.read().strip()
        trading_session = Session.from_remember_token(username, remember_token)
        trading_session.login()
        trading_session.dump_remember_token(Path(".tastyworks_token"))
        print("Successfully logged in with remember-me token.")
    except (errors.AuthorizationExpiredError, FileNotFoundError) as e:
        if isinstance(e, errors.AuthorizationExpiredError):
            print("Authorization expired. Attempting login with remember-me token...")
        else:
            print(
                "Remember-me token file not found. Attempting login with username and password..."
            )
        Path(".tastyworks_token").unlink(missing_ok=True)
        print("Deleted .tastyworks_token file.")
        try:
            if username is None or password is None:
                raise ValueError("Username and password are required for login.")
            trading_session = Session(username, password)
            trading_session.login()
            trading_session.dump_remember_token(Path(".tastyworks_token"))
            print("Successfully logged in with username and password.")
            print(trading_session.session_id)
        except Exception as e:
            print(f"Error: {e}")
            return
    except Exception as e:
        print(f"Error: {e}")
        # Delete the remember-me token file if login fails
        Path(".tastyworks_token").unlink(missing_ok=True)
        print("Deleted .tastyworks_token file.")

    print("Session ID:", trading_session.session_id)

    customer = Customer(trading_session)
    customer.sync()

    if logout:
        print("Logging out...")
        try:
            trading_session.logout()
            print("Successfully logged out.")
        except Exception as e:
            print(f"Error logging out: {e}")
        return

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
    typer.run(main)
