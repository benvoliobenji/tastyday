from pathlib import Path

import requests
import typer
from rich import print, print_json
from rich.console import Console
from rich.table import Table
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

    # Print out a table of accounts, balances, and positions
    console = Console()
    table = Table(title="Accounts")
    table.add_column("Account Number", justify="left", style="cyan")
    table.add_column("Account Type", justify="left", style="magenta")
    table.add_column("Cash Balance", justify="right", style="green")
    table.add_column("Account Restrictions", justify="left", style="blue")
    table.add_column("Positions", justify="right", style="yellow")
    for account in customer.accounts:
        # Get the balance and positions for each account
        table.add_row(
            account.account_number,
            account.account_type,
            str(account.cash_balance),
            ""
            + ("Closed" if account.closed else "")
            + (",Frozen" if account.frozen else "")
            + (",Closing Only" if account.is_closing_only else ""),
            str(account.positions),
        )
    console.print(table)

    if logout:
        print("Logging out...")
        try:
            trading_session.logout()
            print("Successfully logged out.")
        except Exception as e:
            print(f"Error logging out: {e}")
        return

    # Fetch the SPY and TSLA equities
    auth_header = {"Authorization": trading_session.session_id}
    # response = requests.get(
    #     f"{url}/instruments/equities",
    #     params={"symbol[]": ["SPY", "TSLA"]},
    #     headers=auth_header,
    # )
    # if response.status_code != 200:
    #     error_code = response.status_code
    #     error_message = response.json()["error"]["message"]
    #     raise errors.translate_error_code(error_code, error_message)
    # print_json(data=response.json())

    # Print specifically the SPY equity and info
    response = requests.get(
        f"{url}/market-data/",
        params={"symbol": "SPY", "instrumentType": "Equity"},
        headers=auth_header,
    )
    if response.status_code != 200:
        error_code = response.status_code
        error_message = response.json()["error"]["message"]
        raise errors.translate_error_code(error_code, error_message)
    print_json(data=response.json())

    # Next, look for options equities

    # Get the market data for SPY and TSLA - Doesn't work yet
    # response = requests.get(
    #     f"{url}/market-data/by-type",
    #     params={"equity[]": ["SPY"]},
    #     headers=auth_header,
    # )
    # if response.status_code != 200:
    #     error_code = response.status_code
    #     error_message = response.json()["error"]["message"]
    #     raise errors.translate_error_code(error_code, error_message)
    # print_json(data=response.json())


if __name__ == "__main__":
    typer.run(main)
