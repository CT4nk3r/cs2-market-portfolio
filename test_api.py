def test_api():
    url = "http://steamcommunity.com/market/priceoverview/?appid=730&currency=3&market_hash_name=StatTrak%E2%84%A2%20USP-S%20%7C%20Torque%20(Field-Tested)"
    response = requests.get(url, timeout=10)
    data = response.json()
    print(response.status_code)
    print(data)