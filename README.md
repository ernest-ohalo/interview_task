# Interview Technical task

## Installation
### Unix

1. Create a virtual environment
```
$> python3 -m venv venv
```

2. Activate the virtual environment

```
$> source venv/bin/activate
```

When you do not need the server, you can deactivate it with `deactivate`.

3. Install updates and dependencies
```
$> pip install --upgrade pip
$> pip install -r requirements.txt
```

### Windows

1. Create a virtual environment
```
$> python -m venv venv
```

2. Activate the virtual environment
```
$> ".env\Scripts\activate.bat"
```

When you do not need the server, you can deactivate it with `".env\Scripts\deactivate.bat"`.

3. Install dependencies.
```
$> pip install -r requirements.txt
```

## Database

### Initialising the database
From the root directory of this project, run
```
python database.py
```
to initialise the database.

In the `database.py` script you can find a list of 36 ERC-20 tokens I found from the top 80 coins on coingecko. This list is found by matching with the list of ERC-20 tokens on Etherscan.

However, for 7 of these tokens, the contract address was not available on coingecko. Hence, these were omitted from the database and we have 29 tokens left.

The database fetches price, market cap and 24h total volume from the past 3 months and are obtained from the coingecko API at 1-hour intervals.

## Server
Once the database is initialised, the server can be launched by running
```
python server.py
```

Various functions can be used by accessing the following API endpoints. By default, the server is hosted at port 8082, so the default base URL is `http://localhost:8082`.

### GET /token/\<address>/volume

To access this endpoint, insert the contract address of the token as a path param.

Sample response:
```
{
    "estimated_weekly_volume": 63961714.60928121,
    "id": [
        "amp-token"
    ],
    "volume": {
        "22/05/2021 11:30:38": 10020215.46297049,
        "22/05/2021 12:32:34": 10280486.580150232,
        "22/05/2021 13:32:52": 10256832.702816963,
        "22/05/2021 14:13:44": 10199859.798721645,
        ...
        "29/05/2021 08:33:48": 5110367.010496828,
        "29/05/2021 09:32:22": 5023500.52247353
    }
}
```
The current time is `29/05/2021 10:20`, so the server retrieves volume data of this token from `22/05/2021 10:20` to `29/05/2021 10:20`. An optional query param can also be passed in. If `date=2021-05-25` is given, this endpoint will retrieve data from `18/05/2021 00:00` to `25/05/2021 00:00`.

The contract address given in this example is `0xff20817765cb7f73d4bde2e66e067e58d11095c2`, which is for the AMP token.

In the sample response shown above, the value next to each timestamp indicates the total trading volume for that token in the past 24 hours.

As coingecko does not provide data at fixed periods (only roughly 1 hour apart as shown above), it is impossible to calculate the total weekly volume from the data returned. Instead, an estimate is made by summing all total 24h volumes in the past week and dividing by 24.

### GET /token/\<symbol>/address
This endpoint answers the second question. Given the symbol of the token as a path param, the contract address is returned.

Sample request:
```
GET /token/USDT/address
```
Response:
```
{
    "token_address": [
        "0xdac17f958d2ee523a2206206994597c13d831ec7"
    ]
}
```

### GET /token/\<symbol>/price
This endpoint answers the third question. To access this endopint, insert the token symbol as a path param.

Sample response:
```
{
    "id": [
        "amp-token"
    ],
    "average_price": {
        "30/04/2021 15:23:27": 0.053153292942091854,
        "01/05/2021 15:23:27": 0.055279709210948734,
        "02/05/2021 15:23:27": 0.057702737599127016,
        ...
        "29/05/2021 15:23:27": 0.0370636203890507
    }
}
```
The current time is `29/05/2021 15:24`, so the server retrieves price data of this token from `22/05/2021 15:24` to `29/05/2021 15:24`. An optional query param can also be passed in. If `date=2021-05-25` is given, this endpoint will retrieve data from `18/05/2021 00:00` to `25/05/2021 00:00`.

The contract address given in this example is `0xff20817765cb7f73d4bde2e66e067e58d11095c2`, which is for the AMP token.

In the sample response shown above, the value next to each timestamp indicates the average price for that token in the past 24 hours.