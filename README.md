# Python-SwitchBot-API
 Simple Python Wrapper for SwitchBot API



this simple wrapper abstract the authentication, and allow simpler code. it use the auth function provided by [Switchbot](https://github.com/OpenWonderLabs/SwitchBotAPI?tab=readme-ov-file#python-3-example-code) and return the json as dict

it it as easy as

```python
from switchbot import SwitchBot

my_switchbot = SwitchBot(application_token='your_token',
                   application_secret='your_secret')

my_devices = my_switchbot.get('devices')
```

## identification

you can provide identification in environment variables 

| Variable    | Description                                         |
| ----------- | --------------------------------------------------- |
| ENDPOINT    | is the SwitchBot API Endpoint                       |
| API_VERSION | the SwitchBot API version you wanted to use         |
| TOKEN       | token provided by the developper Switchbot account  |
| SECRET      | secret provided by the developper Switchbot account |
| TIMEOUT     | the request timeout override                        |

or during the object creation

```python
my_switchbot = SwitchBot(
    endpoint='https://api.switch-bot.com',
    api_version='v1.1' 
    application_token='your_token',
    application_secret='your_secret',
    timeout=60
)
```

 ## use

after that, you can simply use the [SwitchBot API](https://github.com/OpenWonderLabs/SwitchBotAPI). 

For example, list all your devices :

```
my_devices = my_switchbot.get('devices')
```

get status of a device

```
my_device = 'MY_DEVICE_ID'
test = client.get(f'devices/{my_device}/status')
```

## errors

the wrapper will raise an APIError following the standard HTML errors https://github.com/OpenWonderLabs/SwitchBotAPI?tab=readme-ov-file#standard-http-error-codes

