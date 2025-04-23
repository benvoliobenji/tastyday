import requests

from .errors import translate_error_code
from .session import Session


class Account:
    url = "https://api.cert.tastyworks.com/"
    _auth_header: dict = {"Authorization": ""}

    def __init__(self, active_session: Session, account_number: str = None):
        if not active_session.is_logged_in():
            raise ValueError("Session is not logged in.")
        elif account_number is None:
            raise ValueError("Account number is required.")
        self._auth_header["Authorization"] = f"{active_session.session_id}"
        self.account_number = account_number

    def sync(self):
        """
        Sync the account data with the Tastyworks API.
        """
        response = requests.get(
            f"{self.url}/customers/me/accounts/{self.account_number}",
            headers=self._auth_header,
        )
        if response.status_code != 200:
            error_code = response.status_code
            error_message = response.json()["error"]["message"]
            raise translate_error_code(error_code, error_message)

        # Next, get the account balances (in USD for now)
        response = requests.get(
            f"{self.url}/accounts/{self.account_number}/balances/USD",
            headers=self._auth_header,
        )
        if response.status_code != 200:
            error_code = response.status_code
            error_message = response.json()["error"]["message"]
            raise translate_error_code(error_code, error_message)
        elif response.status_code == 200:
            # print_json(data=response.json())
            # For now, just grab the cash balance (may want to add more info later)
            self.cash_balance = response.json()["data"]["cash-balance"]
            print(f"Account {self.account_number} balance: {self.cash_balance}")

        # Lastly, get the account positions
        response = requests.get(
            f"{self.url}/accounts/{self.account_number}/positions",
            headers=self._auth_header,
        )
        if response.status_code != 200:
            error_code = response.status_code
            error_message = response.json()["error"]["message"]
            raise translate_error_code(error_code, error_message)
        elif response.status_code == 200:
            # print_json(data=response.json())
            # For now, just grab basic positions (may want to add more info later)
            self.positions = response.json()["data"]["items"]
