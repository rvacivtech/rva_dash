import json, configparser, logging
import requests

logging.basicConfig(
    filename="slack_invite.log",
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(message)s"
)

# import config file to global object
config = configparser.ConfigParser()
config_file = 'config.ini'
config.read(config_file)

def generate_url(email):
    slack_token = config.get('slack', 'legacy_token')
    url = f'https://slack.com/api/users.admin.invite?token={slack_token}&email={email}'
    return url 

def send_slack_invite(email):
    url = generate_url(email)
    logging.info(f'Attempting to send request to {url}.')
    r = requests.get(url)
    data = r.json()
    if data['ok']:
        logging.info(f'Successfully sent slack invite to {email}.')
    else:
        error = data['error']
        logging.warning(f'Slack invite failed: {error}')
    return data


# https://slack.com/api/users.admin.invite?token=xoxp-471246971284-471377338051-532736427415-e01b1a80854aa669b4e24f209aad1d1d&email=yopide@4senditnow.com