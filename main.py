import requests
url = "https://api.cert.tastyworks.com"


def main():
    # Make an API request to start a session
    response = requests.post(
        f"{url}/sessions",
        json={
            "login": "login",
            "password": "password",
            "remember-me": True,
        }
    )
    print(response.content)


if __name__ == "__main__":
    main()
