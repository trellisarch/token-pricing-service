from radix_engine_toolkit import derive_virtual_account_address_from_olympia_account_address, OlympiaAddress


def convert():
    addresses = [
        "rdx1qsp258zf47f288g4y47hm3plsp03370safcjg5x98e6j2h66p5we8ds8m7g33",
        "rdx1qspzufvdcal3sa6uztlh4tg4wh7q69e2vf58kez3gw9znk8qkl3v5zcgwkz8p",
        "rdx1qspldshtx0s2l2rcnaqtqpqz8vwps2y6d9se0wq25xrg92l66cmp6mcnc6pyu",
        "rdx1qspnsk6a8208jdxpr0y04jpjvqvg5fkkwcu4q3j7kr7p2te568zny0gcccwyv",
        "rdx1qspasedqcp5nt3ed38ej9tkmkfmnupty3jt0fryzxuf2vykq9k87aaqqctqmk"
    ]
    for address in addresses:
        olympia_address = OlympiaAddress(address)
        babylon_address = derive_virtual_account_address_from_olympia_account_address(
            network_id=1,
            olympia_account_address=olympia_address
        )
        print(babylon_address.as_str())


if __name__ == "__main__":
    convert()