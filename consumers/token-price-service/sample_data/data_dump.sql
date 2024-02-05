--
-- PostgreSQL database dump
--

-- Dumped from database version 15.5
-- Dumped by pg_dump version 16.0

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: radix_token_prices; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.radix_token_prices (
    id integer NOT NULL,
    resource_address character varying,
    usd_price double precision,
    usd_market_cap double precision,
    usd_vol_24h double precision,
    last_updated_at timestamp without time zone,
    token_id integer
);


ALTER TABLE public.radix_token_prices OWNER TO postgres;

--
-- Name: radix_token_prices_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.radix_token_prices_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.radix_token_prices_id_seq OWNER TO postgres;

--
-- Name: radix_token_prices_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.radix_token_prices_id_seq OWNED BY public.radix_token_prices.id;


--
-- Name: radix_tokens; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.radix_tokens (
    id integer NOT NULL,
    resource_address character varying,
    symbol character varying,
    name character varying
);


ALTER TABLE public.radix_tokens OWNER TO postgres;

--
-- Name: radix_tokens_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.radix_tokens_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.radix_tokens_id_seq OWNER TO postgres;

--
-- Name: radix_tokens_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.radix_tokens_id_seq OWNED BY public.radix_tokens.id;


--
-- Name: radix_token_prices id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.radix_token_prices ALTER COLUMN id SET DEFAULT nextval('public.radix_token_prices_id_seq'::regclass);


--
-- Name: radix_tokens id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.radix_tokens ALTER COLUMN id SET DEFAULT nextval('public.radix_tokens_id_seq'::regclass);


--
-- Data for Name: radix_token_prices; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.radix_token_prices (id, resource_address, usd_price, usd_market_cap, usd_vol_24h, last_updated_at, token_id) FROM stdin;
1	resource_rdx1t5n6agexw646tgu3lkr8n0nvt69z00384mhrlfuxz75wprtg9wwllq	0.0010302314055714269	103023.14	0	2024-01-29 12:14:46	\N
2	resource_rdx1t4k6qmpv7krl9gxc5v7ss6fl4j7uuelkaftfz4p49ejd0zj0xs2pwn	1877.9009642565948	18779009.64	0	2024-01-29 12:14:44	\N
3	resource_rdx1t4km4k306ul40s3zr8zwwrm25xfmx7w8ytjvdwqh0u3kkch0eph9rn	0.007109061571362276	7109061.57	968.68	2024-01-29 12:14:44	\N
4	resource_rdx1t4qfgjm35dkwdrpzl3d8pc053uw9v4pj5wfek0ffuzsp73evye6wu6	4.852292243857206e-05	388183.4	0.43	2024-01-29 12:14:44	\N
5	resource_rdx1t4r855ref2yk5jy6ypxyvtflm6hdmyp9lcwvtyksxktmlj3e5klv53	0.0010702912215319188	1761.63	0.04	2024-01-29 12:14:44	\N
6	resource_rdx1t4tjx4g3qzd98nayqxm7qdpj0a0u8ns6a0jrchq49dyfevgh6u0gj3	0.04220773316792373	1519478.41	223.26	2024-01-29 12:14:44	\N
7	resource_rdx1t4upr78guuapv5ept7d7ptekk9mqhy605zgms33mcszen8l9fac8vf	0.9923627509647657	69914.2	3338.76	2024-01-29 12:14:44	\N
8	resource_rdx1t4zrksrzh7ucny7r57ss99nsrxscqwh8crjn6k22m8e9qyxh8c05pl	0.0022686554496738646	113432.76	567.17	2024-01-29 12:14:44	\N
9	resource_rdx1t52pvtk5wfhltchwh3rkzls2x0r98fw9cjhpyrf3vsykhkuwrf7jg8	0.06246427175770811	6246427.18	3013.42	2024-01-29 12:14:44	\N
10	resource_rdx1t54h37ew56pvkv6ag6gw3cmjwspts6twsdtc65r23k2cs8q5qgu727	0.34084093253059783	3408.43	0	2024-01-29 12:14:44	\N
11	resource_rdx1t56e5z78yxa5shrhu352pk9uczkwj2zqe6fdhy9hgj9058a028knul	0.005432311570376813	5432.3	0	2024-01-29 12:14:44	\N
12	resource_rdx1t5fut5566uvkrgf6fltt7pxcdcjs42ydgc5tm3gj8qzaag7xkqn4lg	9.565634637818496e-05	67026.48	1244.53	2024-01-29 12:14:44	\N
13	resource_rdx1t5jnkwz3s6ezuun53s22duad7ezr3gfz3x3v9myuacg42g885q4m04	0.0015388742197902743	75404.82	0	2024-01-29 12:14:44	\N
14	resource_rdx1t5jt96k2ywxq36qt6sdsjfsrq8nchgruhtzq35p8haxte8xwmw2c4r	3.8450195037053945e-07	16149.09	0	2024-01-29 12:14:44	\N
15	resource_rdx1t5muwkqqthsv2w25syfmeef3yul6qc7vs0phulms2hyazf9p863zpq	0.005414711774887692	5414711.78	1021.56	2024-01-29 12:14:44	\N
16	resource_rdx1t5pyvlaas0ljxy0wytm5gvyamyv896m69njqdmm2stukr3xexc2up9	6192.581222495742	6192360.51	154.14	2024-01-29 12:14:44	\N
17	resource_rdx1t5w44wm96zsqjq4a2s2qxxarlay9hdwvcm68fudscx3262yas2xm0e	0.013233964633650026	6947831.43	42.72	2024-01-29 12:14:44	\N
18	resource_rdx1t5xg95m0mhnat0wv59ed4tzmevd7unaezzm04f337djkp8wghz2z7e	4.1328595754906014e-05	41328.6	0	2024-01-29 12:14:44	\N
19	resource_rdx1t5ywq4c6nd2lxkemkv4uzt8v7x7smjcguzq5sgafwtasa6luq7fclq	0.01987502968981212	1350347.56	2422.74	2024-01-29 12:14:44	\N
20	resource_rdx1th7jrjlpfz5dxtpa6v2thsxarqa5mgygcqm8qgm37ntyy6dj7l7dxs	0.001073361368923967	107336.15	0	2024-01-29 12:14:44	\N
21	resource_rdx1th8zw0meumt5t60hdaak8xmc5talrpmphjj2htjutsen02pty9zsd9	1.2095395439835028e-10	120953.97	17.22	2024-01-29 12:14:44	\N
22	resource_rdx1th98jhdzsw6cvzu9c24lzzdyj236szc297vwl8rvcp63jj2pxd57v7	0.02581095966275727	129054.81	0.3	2024-01-29 12:14:44	\N
23	resource_rdx1thdd4yz5jvs5kw73z5a3t4gj4aekzfusgah8mzdays5ywt7vv05yen	133.93776646374369	56346.28	168.04	2024-01-29 12:14:44	\N
24	resource_rdx1thn6xa5vjdh5zagqzvxkxpd70r6eadpzmzr83m20ayp3yhxrjavxz5	0.0026839621633684254	268396.21	0	2024-01-29 12:14:44	\N
25	resource_rdx1thrvr3xfs2tarm2dl9emvs26vjqxu6mqvfgvqjne940jv0lnrrg7rw	1.0264716092912605	10651.03	27.72	2024-01-29 12:14:44	\N
26	resource_rdx1tk3fxrz75ghllrqhyq8e574rkf4lsq2x5a0vegxwlh3defv225cth3	0.03933450275386904	3933450.26	11407.67	2024-01-29 12:14:44	\N
27	resource_rdx1tk7g72c0uv2g83g3dqtkg6jyjwkre6qnusgjhrtz0cj9u54djgnk3c	175.5305841247544	359486.63	0	2024-01-29 12:14:44	\N
28	resource_rdx1tkk83magp3gjyxrpskfsqwkg4g949rmcjee4tu2xmw93ltw2cz94sq	0.012634810840189949	12634810.82	2002.87	2024-01-29 12:14:44	\N
29	resource_rdx1t43srxdw79mlz6xa74sav09ke92jfyf8mnm3q9z64kdjh3tnhye9c0	7.968134219303957e-06	20318742.27	0	2024-01-29 12:14:44	\N
30	resource_rdx1tkmwanknxau3f62kvufsk7sn80gaqhtllz8dasuq2en7nzdfka4t2t	0.04902826824934923	11766784.39	2241.99	2024-01-29 12:14:44	\N
31	resource_rdx1tknxxxxxxxxxradxrdxxxxxxxxx009923554798xxxxxxxxxradxrd	0.0425102577904149	439675033	3425722	2024-01-29 12:15:07	\N
32	resource_rdx1t4nx97z9lcxlcctpug6h8ml4wkkrnpw45v7su4wywma7zlsd5g38v9	2.0047121773468373e-10	200.48	0	2024-01-29 12:14:47	\N
33	resource_rdx1t52m6psjwzmg9vt83d3tsalzwqxwzheftatsmvz7aflq7nj07rtrr3	7.498955341598078e-07	17997.48	0.26	2024-01-29 12:14:44	\N
34	resource_rdx1t59fuustx3gthwwm2s3r77afaddrwsms7hd86egm6rm38nwzv84393	0.0007428493619251506	111427.42	194.82	2024-01-29 12:14:44	\N
35	resource_rdx1t5kmyj54jt85malva7fxdrnpvgfgs623yt7ywdaval25vrdlmnwe97	2.0781604100351648e-05	2078160.42	33134.54	2024-01-29 12:14:44	\N
36	resource_rdx1tht8xmacjp30r9s8ymw2m200munnq78ja2dpaza8k9frpncaz94t88	42313.764972290424	10686.95	2.38	2024-01-29 12:14:44	\N
37	resource_rdx1tk2ekrvckgptrtls6zp0uautg8t34nzl3h93vagt66k49vh757w5px	0.02112021183304692	2112021.15	306.29	2024-01-29 12:14:44	\N
38	resource_rdx1tkcghk0v6ajyt38a67cj94x6rk2f7v7krertpc7p779h4sn5nzx3nj	1.2296765892463915e-06	12296.77	0	2024-01-29 12:14:44	\N
39	resource_rdx1tkkzy2zg4na22kskk00q50v0kghw89akeh84u60xczxsr0ynes80d5	0.0022643807466223233	22643.81	0.09	2024-01-29 12:14:44	\N
40	resource_rdx1tknu3dqlkysz9lt08s7spuvllz3kk2k2yccslfpdk73t4lnznl9jck	0.0013656416966672047	1365641.69	481.39	2024-01-29 12:14:44	\N
41	resource_rdx1t45js47zxtau85v0tlyayerzrgfpmguftlfwfr5fxzu42qtu72tnt0	2.8911465783958246	289114.64	281.04	2024-01-29 12:14:44	\N
42	resource_rdx1t4nxvalrqpqaxv9cvmghk5yyl5u47mgj33npthwfupszvm8ezgy5x0	0.00012010985017707116	60054.92	0	2024-01-29 12:14:44	\N
43	resource_rdx1thsg68perylkawv6w9vuf9ctrjl6pjhh2vrhp5v4q0vxul7a5ws8wz	19.35769594453397	96788.47	3.99	2024-01-26 08:57:51	\N
\.


--
-- Data for Name: radix_tokens; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.radix_tokens (id, resource_address, symbol, name) FROM stdin;
1	resource_rdx1t4tjx4g3qzd98nayqxm7qdpj0a0u8ns6a0jrchq49dyfevgh6u0gj3	$ASTRL	astrl
2	resource_rdx1t45js47zxtau85v0tlyayerzrgfpmguftlfwfr5fxzu42qtu72tnt0	$bobby	bobby
3	resource_rdx1tk7g72c0uv2g83g3dqtkg6jyjwkre6qnusgjhrtz0cj9u54djgnk3c	$cassie	cassie
4	resource_rdx1tkk83magp3gjyxrpskfsqwkg4g949rmcjee4tu2xmw93ltw2cz94sq	$CAVIAR	caviar
5	resource_rdx1t52m6psjwzmg9vt83d3tsalzwqxwzheftatsmvz7aflq7nj07rtrr3	$cerb	cerb
6	resource_rdx1t54h37ew56pvkv6ag6gw3cmjwspts6twsdtc65r23k2cs8q5qgu727	$cmon	cmon
7	resource_rdx1tkcghk0v6ajyt38a67cj94x6rk2f7v7krertpc7p779h4sn5nzx3nj	$crew	crew
8	resource_rdx1t5xg95m0mhnat0wv59ed4tzmevd7unaezzm04f337djkp8wghz2z7e	$CRUMB	crumb1
9	resource_rdx1t5ywq4c6nd2lxkemkv4uzt8v7x7smjcguzq5sgafwtasa6luq7fclq	$DFP2	dfp2
10	resource_rdx1t4qfgjm35dkwdrpzl3d8pc053uw9v4pj5wfek0ffuzsp73evye6wu6	$dgc	dgc
11	resource_rdx1t43srxdw79mlz6xa74sav09ke92jfyf8mnm3q9z64kdjh3tnhye9c0	$dgulden	dgulden
12	resource_rdx1tk2ekrvckgptrtls6zp0uautg8t34nzl3h93vagt66k49vh757w5px	$DPH	dph
13	resource_rdx1t5jt96k2ywxq36qt6sdsjfsrq8nchgruhtzq35p8haxte8xwmw2c4r	$emoon	emoon
14	resource_rdx1t5pyvlaas0ljxy0wytm5gvyamyv896m69njqdmm2stukr3xexc2up9	$FLOOP	floop
15	resource_rdx1t4km4k306ul40s3zr8zwwrm25xfmx7w8ytjvdwqh0u3kkch0eph9rn	$foton	foton
16	resource_rdx1tknu3dqlkysz9lt08s7spuvllz3kk2k2yccslfpdk73t4lnznl9jck	$GAB	gab
17	resource_rdx1t5kmyj54jt85malva7fxdrnpvgfgs623yt7ywdaval25vrdlmnwe97	$HUG	hug
18	resource_rdx1tkmwanknxau3f62kvufsk7sn80gaqhtllz8dasuq2en7nzdfka4t2t	$ida	ida
19	resource_rdx1th8zw0meumt5t60hdaak8xmc5talrpmphjj2htjutsen02pty9zsd9	$inu	inu
20	resource_rdx1th98jhdzsw6cvzu9c24lzzdyj236szc297vwl8rvcp63jj2pxd57v7	$ipt	ipt
21	resource_rdx1t5muwkqqthsv2w25syfmeef3yul6qc7vs0phulms2hyazf9p863zpq	$ist	ist
22	resource_rdx1t4r855ref2yk5jy6ypxyvtflm6hdmyp9lcwvtyksxktmlj3e5klv53	$luck	luck
23	resource_rdx1t5fut5566uvkrgf6fltt7pxcdcjs42ydgc5tm3gj8qzaag7xkqn4lg	$MNI	mni
24	resource_rdx1t4nx97z9lcxlcctpug6h8ml4wkkrnpw45v7su4wywma7zlsd5g38v9	$MRK	mrk
25	resource_rdx1t52pvtk5wfhltchwh3rkzls2x0r98fw9cjhpyrf3vsykhkuwrf7jg8	$OCI	oci
26	resource_rdx1thn6xa5vjdh5zagqzvxkxpd70r6eadpzmzr83m20ayp3yhxrjavxz5	$PLANET	planet
27	resource_rdx1th7jrjlpfz5dxtpa6v2thsxarqa5mgygcqm8qgm37ntyy6dj7l7dxs	$radit	radit
28	resource_rdx1tknxxxxxxxxxradxrdxxxxxxxxx009923554798xxxxxxxxxradxrd	$XRD	radix
29	resource_rdx1t4zrksrzh7ucny7r57ss99nsrxscqwh8crjn6k22m8e9qyxh8c05pl	$rdk	rdk
30	resource_rdx1t4nxvalrqpqaxv9cvmghk5yyl5u47mgj33npthwfupszvm8ezgy5x0	$rds	rds
31	resource_rdx1t5n6agexw646tgu3lkr8n0nvt69z00384mhrlfuxz75wprtg9wwllq	$rdt	rdt
32	resource_rdx1thsg68perylkawv6w9vuf9ctrjl6pjhh2vrhp5v4q0vxul7a5ws8wz	$robo	robo
33	resource_rdx1t56e5z78yxa5shrhu352pk9uczkwj2zqe6fdhy9hgj9058a028knul	$rst	rst
34	resource_rdx1t4k6qmpv7krl9gxc5v7ss6fl4j7uuelkaftfz4p49ejd0zj0xs2pwn	$RWA	rwa
35	resource_rdx1t5w44wm96zsqjq4a2s2qxxarlay9hdwvcm68fudscx3262yas2xm0e	$rzr	rzr
36	resource_rdx1t5jnkwz3s6ezuun53s22duad7ezr3gfz3x3v9myuacg42g885q4m04	$sinx	sinx
37	resource_rdx1thdd4yz5jvs5kw73z5a3t4gj4aekzfusgah8mzdays5ywt7vv05yen	$thc	thc
38	resource_rdx1t59fuustx3gthwwm2s3r77afaddrwsms7hd86egm6rm38nwzv84393	$VKC	vkc
39	resource_rdx1tht8xmacjp30r9s8ymw2m200munnq78ja2dpaza8k9frpncaz94t88	$wbtc	wbtc
40	resource_rdx1tk3fxrz75ghllrqhyq8e574rkf4lsq2x5a0vegxwlh3defv225cth3	$WEFT	weft
41	resource_rdx1tkkzy2zg4na22kskk00q50v0kghw89akeh84u60xczxsr0ynes80d5	$xse	xse
42	resource_rdx1t4upr78guuapv5ept7d7ptekk9mqhy605zgms33mcszen8l9fac8vf	$xUSDC	xusdc
43	resource_rdx1thrvr3xfs2tarm2dl9emvs26vjqxu6mqvfgvqjne940jv0lnrrg7rw	$xUSDT	xusdt
\.


--
-- Name: radix_token_prices_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.radix_token_prices_id_seq', 43, true);


--
-- Name: radix_tokens_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.radix_tokens_id_seq', 43, true);


--
-- Name: radix_token_prices radix_token_prices_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.radix_token_prices
    ADD CONSTRAINT radix_token_prices_pkey PRIMARY KEY (id);


--
-- Name: radix_tokens radix_tokens_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.radix_tokens
    ADD CONSTRAINT radix_tokens_pkey PRIMARY KEY (id);


--
-- Name: radix_token_prices radix_token_prices_token_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.radix_token_prices
    ADD CONSTRAINT radix_token_prices_token_id_fkey FOREIGN KEY (token_id) REFERENCES public.radix_tokens(id);


--
-- PostgreSQL database dump complete
--

