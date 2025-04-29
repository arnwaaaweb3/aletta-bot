arnwaaaweb3/aletta-bot
A Discord Financial bot, strongly integrated with APIs from CoinGecko, CoinMarketCap, Messari, etc. Equipped with the ability of fundamental analysis, price-action graph, news integration auto-looping and much more!

[EN] - Feature List of Aletta V1 (April 2025 Version) Below are the features and advantages of Aletta V1, categorized based on the FPN theme (Fundamental, Price, News):

📊 F – Fundamental

!fa, !fund, !fundamental

Displays fundamental information from CoinGecko (market cap, volume, FDV, explorer, website).

Example: !fa sui, !fund xrp, !fundamental ena

!fscore

Provides a fundamental score based on CoinGecko and Tokenomics JSON (total of 15 points).

Example: !fscore eth

!update_tokenomics

Automatically scrapes the coin description from CoinGecko and generates a tokenomics.json file.

!metrics

Analyzes the project's ecosystem health using data from CMC (Market Cap, Volume, Volatility, Supply Ratio, etc.).

Example: !metrics btc

!compare , , [Max. 3]

Compares 2 to 3 different coins using various parameters and indicators.

!roadmap

Displays the development roadmap of a crypto project along with its progress status (completed, in_progress, delayed, or planned).

Example: !roadmap eth

💰 P – Price

!harga

Displays the current price and a 7-day price chart.

!checkcoin

Retrieves the CoinGecko ID of a coin based on its symbol (with caching).

3.a !bubble_4h

Displays a bubble chart showing the performance of the top 20 cryptos (top 10 gainers & top 10 losers) based on 4-hour price change (%) – (CMC API).

3.b !bubble

Displays a bubble chart showing the performance of the top 20 cryptos (top 10 gainers & top 10 losers) based on daily price change (24h) – (CMC API).

3.c !bubble_1w

Displays a bubble chart showing weekly price change performance (7d) of the top 20 cryptos – (CMC API).

3.d !bubble_1m

Displays a bubble chart showing monthly price change performance (30d) of the top 20 cryptos – (CMC API).

3.e !bubble_all

Displays a bubble chart summarizing price change (%) across 1d, 7d, and 30d in a single graph.

!mywatchlist

Shows the percentage price change performance of coins added to the watchlist.

!addcoin [coin]

Adds a coin to the watchlist, accessible via !mywatchlist.

!remove [coin]

Removes a coin from the watchlist, which can be viewed via !mywatchlist.

!clearwatchlist

Clears all coins in the watchlist.json via embedded message.

!fixjson

Deletes and automatically rewrites the watchlist.json file.

📰 N – News

!kb, !kategori, !kategori_berita

Displays an embedded message inviting users to search for news by pre-defined categories.

!sentimen

Searches, analyzes, and summarizes the latest news about a specific coin with sentiment analysis (bullish/bearish/neutral).

Example: !sentimen xrp

Background Task: The bot automatically posts news from 10+ sources every hour to the default channel.

🧠 Smart System

✅ Custom tokenomics.json, supports manual entry and semi-automatic updates via CoinGecko scraping. ✅ Internal COIN_MAPPING allowing commands to use popular symbols like btc, eth, sui, etc. ✅ Coin ID caching via CoinGecko to optimize API usage. ✅ Complete logging via the aletta.log file.

[ID] - Daftar Fitur Aletta V1 (Versi April 2025) Berikut adalah fitur dan keunggulan Aletta V1, kategori berdasarkan tema FPN (Fundamental, Price, News):

📊 F – Fundamental

!fa, !fund !fundamental ** - Menampilkan info fundamental dari CoinGecko (market cap, volume, FDV, explorer, website). - [ex: !fa sui, !fund xrp, !fundamental ena]

!fscore ** - Memberi skor fundamental berbasis CoinGecko + Tokenomics JSON (15 poin total). - [ex: !fscore eth]

!update_tokenomics - Scrape otomatis deskripsi coin dari CoinGecko dan generate tokenomics.json.

!metrics ** - Analisis kesehatan ekosistem proyek menggunakan data dari CMC (Market Cap, Volume, Volatility, Supply Ratio, dll). - [ex: !metrics btc]

!compare , , - [Maks.3] - Membandingkan 2-3 koin yang berbeda dengan berbagai macam parameter dan indikator.

!roadmap ** - Menampilkan roadmap pengembangan sebuah proyek kripto dengan status progressnya (completed, in_progress, delayed, atau planned). - [ex: !roadmap eth]

💰 P – Price

!harga - Menampilkan harga saat ini dan grafik harga 7 hari terakhir.

!checkcoin - Mendapatkan CoinGecko ID dari simbol coin (dengan caching).

3.a !bubble_4h - Menampilkan bubble chart performa top 20 crypto (top 10 gainers & top 10 losers) berdasarkan % perubahan harga per 4 jam (4h) - (CMC API).

3.b !bubble - Menampilkan bubble chart performa top 20 crypto (top 10 gainers & top 10 losers) berdasarkan % perubahan harian (24h/1d) - (CMC API).

3.c !bubble_1w - Menampilkan bubble chart performa top 20 crypto (top 10 gainers & top 10 losers) berdasarkan % perubahan mingguan (7d/1w) - (CMC API).

3.d !bubble_1m - Menampilkan bubble chart performa top 20 crypto (top 10 gainers & top 10 losers) berdasarkan % perubahan bulanan (30d/4w/1m) - (CMC API).

3.e !bubble_all - Menampilkan bubble chart performa (% perubahan harga) di 1d, 7d, dan 30d dalam satu grafik

!mywatchlist** - Menampilkan performa % perubahan harga dari daftar pantauan yang telah ditambahkan, dengan:

!addcoin [coin] - Menambahkan koin ke dalam daftar pantauan yang kemudian bisa diakses melalui !mywatchlist"

!remove [coin] - *Menghapus koin dari dalam daftar pantauan yang kemudian bisa diakses melalui "!mywatchlist"

!clearwatchlist - *Menghapus semua koin yang ada di dalam watchlist.json melalui embbed message

!fixjson - Menghapus dan mengetik ulang file watchlist.json secara otomatis

📰 N – News

!kb, !kategori, !kategori_berita - Menampilkan embbed message yang mempersilahkan pengguna untuk mencari berita sesuai kategori yang sudah disediakan

!sentimen ** - Mencari, menganalisis, dan merangkum berita terbaru tentang koin tertentu dengan analisis sentimen (bullish/bearish/netral). - [ex: !sentimen xrp]

Background Task Bot otomatis posting berita dari 10+ sumber setiap jam ke channel default.

🧠 Smart System

✅ tokenomics.json custom, mendukung pengisian manual dan update semi-otomatis via CoinGecko scraping.

✅ COIN_MAPPING internal agar command tetap bisa pakai simbol populer seperti btc, eth, sui, dll.

✅ Caching ID coin via CoinGecko untuk efisiensi API.

✅ Logging lengkap via file aletta.log.
