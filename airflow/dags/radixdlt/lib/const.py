RADIX_CHARTS_TOKENS = {
    "hug": {
        "resource_address": "resource_rdx1t5kmyj54jt85malva7fxdrnpvgfgs623yt7ywdaval25vrdlmnwe97",
        "symbol": "$HUG",
    },
    "radix": {
        "resource_address": "resource_rdx1tknxxxxxxxxxradxrdxxxxxxxxx009923554798xxxxxxxxxradxrd",
        "symbol": "XRD",
    },
    "floop": {
        "resource_address": "resource_rdx1t5pyvlaas0ljxy0wytm5gvyamyv896m69njqdmm2stukr3xexc2up9",
        "symbol": "$FLOOP",
    },
    "defiplaza": {
        "resource_address": "resource_rdx1t5ywq4c6nd2lxkemkv4uzt8v7x7smjcguzq5sgafwtasa6luq7fclq",
        "symbol": "$DFP2",
    },
}

LEDGER_USD_POOL = {
    "component": "component_rdx1cqelumvmmgwths34k9pp0htd2ykwq7d70m0r389etwh39ul3j5tyj5",
    "dex": "c9",
    "base": "XRD",
    "quote": "hUSDC",
}

LEDGER_TOKENS = {
    "XRD": {
        "resource_address": "resource_rdx1tknxxxxxxxxxradxrdxxxxxxxxx009923554798xxxxxxxxxradxrd",
        "pools": [],
        "base": "XRD",
        "quote": "XRD",
    },
    "FLOOP": {
        "resource_address": "resource_rdx1t5pyvlaas0ljxy0wytm5gvyamyv896m69njqdmm2stukr3xexc2up9",
        "pools": [
            {
                "component": "component_rdx1czgaazn4wqf40kav57t8tu6kwv2a5sfmnlzlar9ee6kdqk0ll2chsz",
                "dex": "c9",
            },
            {
                "component": "component_rdx1crmhyn4m3u3pxpx74lafpz5yyjtlyupx8duqcct9f8gx0tqqqjvc4q",
                "dex": "ociswap",
            },
        ],
        "base": "XRD",
        "quote": "FLOOP",
    },
    "hUSDC": {
        "resource_address": "resource_rdx1thxj9m87sn5cc9ehgp9qxp6vzeqxtce90xm5cp33373tclyp4et4gv",
        "pools": [
            {
                "component": "component_rdx1cqelumvmmgwths34k9pp0htd2ykwq7d70m0r389etwh39ul3j5tyj5",
                "dex": "c9",
            },
        ],
        "base": "XRD",
        "quote": "hUSDC",
    },
}
