import requests

from app.config.config import Config
from app.logger.log import get_logger
from app.models.token_price import LsuPrice
from app.utils.request import get_headers

logger = get_logger()


def get_lsu_redemption_values(addresses=[]):
    lsu_redemption_values = {}

    chunks = [addresses[i : i + 20] for i in range(0, len(addresses), 20)]
    for chunk in chunks:
        body = {
            "addresses": chunk,
            "aggregation_level": "Vault",
            "explicit_metadata": ["validator"],
        }
        try:
            data = requests.post(
                Config.ENTITY_DETAILS_URL, json=body, headers=get_headers()
            ).json()
            validators = []
            for lsu_resource in data["items"]:
                v = list(
                    filter(
                        lambda metadata_item: metadata_item["key"] == "validator",
                        lsu_resource["metadata"]["items"],
                    )
                )
                if v:
                    validator = v[0]
                    if validator["value"]["typed"][
                        "type"
                    ] == "GlobalAddress" and validator["value"]["typed"][
                        "value"
                    ].startswith(
                        "validator_"
                    ):
                        lsu_redemption_values[lsu_resource["address"]] = {
                            "totalSupplyOfStakeUnits": lsu_resource["details"][
                                "total_supply"
                            ]
                        }
                        validators.append(validator["value"]["typed"]["value"])
                    else:
                        logger.info(
                            f"Validator: {validator} is not valid or it might not exist"
                        )
                else:
                    logger.info(
                        f"Resource: {lsu_resource.address} doesn't seem to be an LSU resource"
                    )

            validators_details_body = {
                "addresses": validators,
                "aggregation_level": "Vault",
            }
            validators_data = requests.post(
                Config.ENTITY_DETAILS_URL,
                json=validators_details_body,
                headers=get_headers(),
            ).json()
            for validator in validators_data["items"]:
                stake_unit_resource_address = validator["details"]["state"][
                    "stake_unit_resource_address"
                ]
                stake_xrd_vault_address = validator["details"]["state"][
                    "stake_xrd_vault"
                ]["entity_address"]

                xrd_stake_resource = list(
                    filter(
                        lambda item: item["resource_address"]
                        == Config.XRD_RESOURCE_ADDRESS,
                        validator["fungible_resources"]["items"],
                    )
                )
                xrd_stake_vault = list(
                    filter(
                        lambda vault: vault["vault_address"] == stake_xrd_vault_address,
                        xrd_stake_resource[0]["vaults"]["items"],
                    )
                )
                xrd_stake_vault_balance = xrd_stake_vault[0]["amount"]

                total_supply_of_stake_units = lsu_redemption_values[
                    stake_unit_resource_address
                ]["totalSupplyOfStakeUnits"]
                xrd_redemption_value = float(xrd_stake_vault_balance) / float(
                    total_supply_of_stake_units
                )
                lsu_redemption_values[stake_unit_resource_address][
                    "xrdRedemptionValue"
                ] = xrd_redemption_value
        except Exception:
            logger.error(
                "There was an error getting the xrd redemption value. "
                "Check that all addresses used are LSU resource addresses"
            )
            return {}

    return [
        LsuPrice(key, float(value["xrdRedemptionValue"]))
        for key, value in lsu_redemption_values.items()
    ]
