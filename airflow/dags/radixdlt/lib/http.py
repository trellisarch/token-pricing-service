from radixdlt.config.config import Config


def get_headers():
    return {"accept": "application/json"}


def get_radix_charts_headers():
    return {
        "accept": "application/json",
        "authorization": f"bearer {Config.RADIX_CHARTS_AUTHORIZATION_TOKEN}",
    }
