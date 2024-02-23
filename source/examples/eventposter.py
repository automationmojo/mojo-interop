
import requests


def poster_main():

    port = 56683

    url = f"http://127.0.0.1:{port}"

    headers = { "Content-Type": "application/json" }
    data = { "tasking-id": "abc", "event-name": "blah" }

    resp = requests.post(url, headers=headers, json=data)

    print (f"Return Status: {resp.status_code}")

if __name__ == "__main__":
    poster_main()
