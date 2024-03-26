from locust import task, FastHttpUser
import random

TOKENS = [
    "resource_rdx1t4tjx4g3qzd98nayqxm7qdpj0a0u8ns6a0jrchq49dyfevgh6u0gj3",
    "resource_rdx1t45js47zxtau85v0tlyayerzrgfpmguftlfwfr5fxzu42qtu72tnt0",
    "resource_rdx1tk7g72c0uv2g83g3dqtkg6jyjwkre6qnusgjhrtz0cj9u54djgnk3c",
    "resource_rdx1tkk83magp3gjyxrpskfsqwkg4g949rmcjee4tu2xmw93ltw2cz94sq",
    "resource_rdx1t52m6psjwzmg9vt83d3tsalzwqxwzheftatsmvz7aflq7nj07rtrr3",
    "resource_rdx1t54h37ew56pvkv6ag6gw3cmjwspts6twsdtc65r23k2cs8q5qgu727",
    "resource_rdx1tkcghk0v6ajyt38a67cj94x6rk2f7v7krertpc7p779h4sn5nzx3nj",
    "resource_rdx1t5xg95m0mhnat0wv59ed4tzmevd7unaezzm04f337djkp8wghz2z7e",
    "resource_rdx1t5ywq4c6nd2lxkemkv4uzt8v7x7smjcguzq5sgafwtasa6luq7fclq",
    "resource_rdx1t4qfgjm35dkwdrpzl3d8pc053uw9v4pj5wfek0ffuzsp73evye6wu6",
    "resource_rdx1t43srxdw79mlz6xa74sav09ke92jfyf8mnm3q9z64kdjh3tnhye9c0",
    "resource_rdx1tk2ekrvckgptrtls6zp0uautg8t34nzl3h93vagt66k49vh757w5px",
    "resource_rdx1t5jt96k2ywxq36qt6sdsjfsrq8nchgruhtzq35p8haxte8xwmw2c4r",
    "resource_rdx1t5pyvlaas0ljxy0wytm5gvyamyv896m69njqdmm2stukr3xexc2up9",
    "resource_rdx1t4km4k306ul40s3zr8zwwrm25xfmx7w8ytjvdwqh0u3kkch0eph9rn",
    "resource_rdx1tknu3dqlkysz9lt08s7spuvllz3kk2k2yccslfpdk73t4lnznl9jck",
    "resource_rdx1t5kmyj54jt85malva7fxdrnpvgfgs623yt7ywdaval25vrdlmnwe97",
    "resource_rdx1tkmwanknxau3f62kvufsk7sn80gaqhtllz8dasuq2en7nzdfka4t2t",
    "resource_rdx1th8zw0meumt5t60hdaak8xmc5talrpmphjj2htjutsen02pty9zsd9",
    "resource_rdx1th98jhdzsw6cvzu9c24lzzdyj236szc297vwl8rvcp63jj2pxd57v7",
    "resource_rdx1t5muwkqqthsv2w25syfmeef3yul6qc7vs0phulms2hyazf9p863zpq",
    "resource_rdx1t4r855ref2yk5jy6ypxyvtflm6hdmyp9lcwvtyksxktmlj3e5klv53",
    "resource_rdx1t5fut5566uvkrgf6fltt7pxcdcjs42ydgc5tm3gj8qzaag7xkqn4lg",
    "resource_rdx1t4nx97z9lcxlcctpug6h8ml4wkkrnpw45v7su4wywma7zlsd5g38v9",
    "resource_rdx1t52pvtk5wfhltchwh3rkzls2x0r98fw9cjhpyrf3vsykhkuwrf7jg8",
    "resource_rdx1thn6xa5vjdh5zagqzvxkxpd70r6eadpzmzr83m20ayp3yhxrjavxz5",
    "resource_rdx1th7jrjlpfz5dxtpa6v2thsxarqa5mgygcqm8qgm37ntyy6dj7l7dxs",
    "resource_rdx1tknxxxxxxxxxradxrdxxxxxxxxx009923554798xxxxxxxxxradxrd",
    "resource_rdx1t4zrksrzh7ucny7r57ss99nsrxscqwh8crjn6k22m8e9qyxh8c05pl",
    "resource_rdx1t4nxvalrqpqaxv9cvmghk5yyl5u47mgj33npthwfupszvm8ezgy5x0",
    "resource_rdx1t5n6agexw646tgu3lkr8n0nvt69z00384mhrlfuxz75wprtg9wwllq",
    "resource_rdx1thsg68perylkawv6w9vuf9ctrjl6pjhh2vrhp5v4q0vxul7a5ws8wz",
    "resource_rdx1t56e5z78yxa5shrhu352pk9uczkwj2zqe6fdhy9hgj9058a028knul",
]


class WalletUser(FastHttpUser):

    @task
    def send_post_request(self):
        num_tokens = random.randint(5, 10)
        tokens_list = random.sample(TOKENS, num_tokens)
        request_body = {"currency": "USD", "lsus": [], "tokens": tokens_list}
        self.client.post("/price/tokens/", json=request_body)
