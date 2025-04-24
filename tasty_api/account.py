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
        elif response.status_code == 200:
            self.all_account_data = response.json()["data"]
            self.account_type = response.json()["data"]["margin-or-cash"]

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
            self.all_balance_data = response.json()["data"]
            self.cash_balance = response.json()["data"]["cash-balance"]
            print(f"Account {self.account_number} balance: {self.cash_balance}")

        # Get our trading status
        response = requests.get(
            f"{self.url}/accounts/{self.account_number}/trading-status",
            headers=self._auth_header,
        )
        if response.status_code != 200:
            error_code = response.status_code
            error_message = response.json()["error"]["message"]
            raise translate_error_code(error_code, error_message)
        elif response.status_code == 200:
            # print_json(data=response.json())
            self.all_trading_status_data = response.json()["data"]
            self.is_closing_only = response.json()["data"]["is-closing-only"]
            self.closed = response.json()["data"]["is-closed"]
            self.frozen = response.json()["data"]["is-frozen"]
            self.blocked_from_trading = self.closed or self.frozen

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
            self.all_position_data = response.json()["data"]
            self.positions = response.json()["data"]["items"]
