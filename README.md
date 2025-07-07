# arnwaaaweb3/aletta-bot
_A Discord Financial bot, strongly integrated with APIs from CoinGecko, CoinMarketCap, Messari, etc. Equipped with the ability of fundamental analysis, price-action graph, news integration auto-looping and much more!_

---

## [EN] - Aletta V1 Feature List (April 2025 Version)
Below are the features and advantages of Aletta V1, categorized based on the FPN theme (Fundamental, Price, News):

---

### 📊 F – Fundamental

* **__!fa, !fund, !fundamental__**
    _Displays fundamental information from CoinGecko (market cap, volume, FDV, explorer, website)._
    * Example: `!fa sui`, `!fund xrp`, `!fundamental ena`

* **__!fscore__**
    _Provides a fundamental score based on CoinGecko and Tokenomics JSON (total of 15 points)._
    * Example: `!fscore eth`

* **__!update_tokenomics__**
    _Automatically scrapes the coin description from CoinGecko and generates a `tokenomics.json` file._

* **__!metrics__**
    _Analyzes the project's ecosystem health using data from CMC (Market Cap, Volume, Volatility, Supply Ratio, etc.)._
    * Example: `!metrics btc`

* **__!compare <coin1>, <coin2>, [coin3]__**
    _Compares 2 to 3 different coins using various parameters and indicators (Max. 3 coins)._

* **__!roadmap__**
    _Displays the development roadmap of a crypto project along with its progress status (completed, in_progress, delayed, or planned)._
    * Example: `!roadmap eth`

---

### 💰 P – Price

* **__!harga__**
    _Displays the current price and a 7-day price chart._

* **__!checkcoin__**
    _Retrieves the CoinGecko ID of a coin based on its symbol (with caching)._

* **Bubble Charts (CMC API)**
    * **__!bubble_4h__**
        _Displays a bubble chart showing the performance of the top 20 cryptos (top 10 gainers & top 10 losers) based on 4-hour price change (%)._
    * **__!bubble__**
        _Displays a bubble chart showing the performance of the top 20 cryptos (top 10 gainers & top 10 losers) based on daily price change (24h)._
    * **__!bubble_1w__**
        _Displays a bubble chart showing weekly price change performance (7d) of the top 20 cryptos._
    * **__!bubble_1m__**
        _Displays a bubble chart showing monthly price change performance (30d) of the top 20 cryptos._
    * **__!bubble_all__**
        _Displays a bubble chart summarizing price change (%) across 1d, 7d, and 30d in a single graph._

* **__!mywatchlist__**
    _Shows the percentage price change performance of coins added to the watchlist._

* **__!addcoin [coin]__**
    _Adds a coin to the watchlist, accessible via `!mywatchlist`._

* **__!remove [coin]__**
    _Removes a coin from the watchlist, which can be viewed via `!mywatchlist`._

* **__!clearwatchlist__**
    _Clears all coins in the `watchlist.json` via an embedded message._

* **__!fixjson__**
    _Deletes and automatically rewrites the `watchlist.json` file._

---

### 📰 N – News

* **__!kb, !kategori, !kategori_berita__**
    _Displays an embedded message inviting users to search for news by pre-defined categories._

* **__!sentimen__**
    _Searches, analyzes, and summarizes the latest news about a specific coin with sentiment analysis (bullish/bearish/neutral)._
    * Example: `!sentimen xrp`

* **__Background Task__**
    _The bot automatically posts news from 10+ sources every hour to the default channel._

---

### 🧠 Smart System

* ✅ **Custom `tokenomics.json`**: Supports manual entry and semi-automatic updates via CoinGecko scraping.
* ✅ **Internal `COIN_MAPPING`**: Allows commands to use popular symbols like `btc`, `eth`, `sui`, etc.
* ✅ **Coin ID caching**: Optimizes API usage via CoinGecko.
* ✅ **Complete logging**: All activities are logged via the `aletta.log` file.

---

## [ID] - Daftar Fitur Aletta V1 (Versi April 2025)
Berikut adalah fitur dan keunggulan Aletta V1, dikategorikan berdasarkan tema FPN (Fundamental, Price, News):

---

### 📊 F – Fundamental

* **__!fa, !fund, !fundamental__**
    _Menampilkan info fundamental dari CoinGecko (market cap, volume, FDV, explorer, website)._
    * Contoh: `!fa sui`, `!fund xrp`, `!fundamental ena`

* **__!fscore__**
    _Memberi skor fundamental berbasis CoinGecko + Tokenomics JSON (total 15 poin)._
    * Contoh: `!fscore eth`

* **__!update_tokenomics__**
    _Scrape otomatis deskripsi koin dari CoinGecko dan generate `tokenomics.json`._

* **__!metrics__**
    _Analisis kesehatan ekosistem proyek menggunakan data dari CMC (Market Cap, Volume, Volatility, Supply Ratio, dll)._
    * Contoh: `!metrics btc`

* **__!compare <koin1>, <koin2>, [koin3]__**
    _Membandingkan 2-3 koin yang berbeda dengan berbagai macam parameter dan indikator (Maks. 3 koin)._

* **__!roadmap__**
    _Menampilkan roadmap pengembangan sebuah proyek kripto dengan status progressnya (completed, in_progress, delayed, atau planned)._
    * Contoh: `!roadmap eth`

---

### 💰 P – Price

* **__!harga__**
    _Menampilkan harga saat ini dan grafik harga 7 hari terakhir._

* **__!checkcoin__**
    _Mendapatkan CoinGecko ID dari simbol koin (dengan caching)._

* **Bubble Charts (CMC API)**
    * **__!bubble_4h__**
        _Menampilkan bubble chart performa top 20 kripto (top 10 gainers & top 10 losers) berdasarkan % perubahan harga per 4 jam (4h)._
    * **__!bubble__**
        _Menampilkan bubble chart performa top 20 kripto (top 10 gainers & top 10 losers) berdasarkan % perubahan harian (24h/1d)._
    * **__!bubble_1w__**
        _Menampilkan bubble chart performa top 20 kripto (top 10 gainers & top 10 losers) berdasarkan % perubahan mingguan (7d/1w)._
    * **__!bubble_1m__**
        _Menampilkan bubble chart performa top 20 kripto (top 10 gainers & top 10 losers) berdasarkan % perubahan bulanan (30d/4w/1m)._
    * **__!bubble_all__**
        _Menampilkan bubble chart performa (% perubahan harga) di 1d, 7d, dan 30d dalam satu grafik._

* **__!mywatchlist__**
    _Menampilkan performa % perubahan harga dari daftar pantauan yang telah ditambahkan._

* **__!addcoin [koin]__**
    _Menambahkan koin ke dalam daftar pantauan yang kemudian bisa diakses melalui `!mywatchlist`._

* **__!remove [koin]__**
    _Menghapus koin dari dalam daftar pantauan yang kemudian bisa diakses melalui `!mywatchlist`._

* **__!clearwatchlist__**
    _Menghapus semua koin yang ada di dalam `watchlist.json` melalui embedded message._

* **__!fixjson__**
    _Menghapus dan menulis ulang file `watchlist.json` secara otomatis._

---

### 📰 N – News

* **__!kb, !kategori, !kategori_berita__**
    _Menampilkan embedded message yang mempersilakan pengguna untuk mencari berita sesuai kategori yang sudah disediakan._

* **__!sentimen__**
    _Mencari, menganalisis, dan merangkum berita terbaru tentang koin tertentu dengan analisis sentimen (bullish/bearish/netral)._
    * Contoh: `!sentimen xrp`

* **__Background Task__**
    _Bot otomatis posting berita dari 10+ sumber setiap jam ke channel default._

---

### 🧠 Smart System

* ✅ **Custom `tokenomics.json`**: Mendukung pengisian manual dan update semi-otomatis via CoinGecko scraping.
* ✅ **Internal `COIN_MAPPING`**: Agar command tetap bisa pakai simbol populer seperti `btc`, `eth`, `sui`, dll.
* ✅ **Caching ID koin**: Untuk efisiensi API via CoinGecko.
* ✅ **Logging lengkap**: Semua aktivitas dicatat via file `aletta.log`.
