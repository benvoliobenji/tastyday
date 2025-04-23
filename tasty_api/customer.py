import requests
from rich.console import Console
from rich.table import Table

from .account import Account
from .errors import translate_error_code
from .session import Session


class Customer:
    url = "https://api.cert.tastyworks.com"
    active_session: Session = None
    _auth_header: dict = {"Authorization": ""}
    _accounts: list[Account] = []

    def __init__(self, active_session: Session):
        if not active_session.is_logged_in():
            raise ValueError("Session is not logged in.")
        self._auth_header["Authorization"] = f"{active_session.session_id}"
        self.active_session = active_session

    def sync(self):
        """
        Sync the customer data with the Tastyworks API.
        """
        response = requests.get(f"{self.url}/customers/me", headers=self._auth_header)
        if response.status_code != 200:
            error_code = response.status_code
            error_message = response.json()["error"]["message"]
            raise translate_error_code(error_code, error_message)

        # If we can get our customer data, it's time we get our accounts
        response = requests.get(
            f"{self.url}/customers/me/accounts", headers=self._auth_header
        )
        if response.status_code == 200:
            accounts = response.json()["data"]["items"]
            for account in accounts:
                account_number = account["account"]["account-number"]
                # Check if the account already exists in the list
                if any(acc.account_number == account_number for acc in self._accounts):
                    continue

                # If not, create a new Account instnace, synchronize, and append it to the list
                new_account = Account(self.active_session, account_number)
                new_account.sync()
                self._accounts.append(new_account)
                print(f"Account {account_number} synchronized.")
            # Print out a table of accounts, balances, and positions
            console = Console()
            table = Table(title="Accounts")
            table.add_column("Account Number", justify="left", style="cyan")
            table.add_column("Cash Balance", justify="right", style="green")
            table.add_column("Positions", justify="right", style="yellow")
            for account in self._accounts:
                # Get the balance and positions for each account
                table.add_row(
                    account.account_number,
                    str(account.cash_balance),
                    str(account.positions),
                )
            console.print(table)

        else:
            error_code = response.status_code
            error_message = response.json()["error"]["message"]
            raise translate_error_code(error_code, error_message)
