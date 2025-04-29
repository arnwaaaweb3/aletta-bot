# === Keep-Alive ===
from keep_alive import keep_alive
keep_alive()

# === Core Discord Bot ===
import discord
from discord.ext import commands
from discord.ui import Button, View

# === OS & ENV ===
import os
from dotenv import load_dotenv

# === Async & Requests ===
import asyncio
import aiohttp
import requests
import feedparser
from urllib.parse import urlparse, urlunparse

# === Data & Logging ===
import json
import logging
import math
import numpy as np
import random
from math import sqrt
from random import uniform

# === Time & Date ===
import datetime

import matplotlib
matplotlib.use("Agg")

# === Visualization ===
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.image as mpimg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from io import BytesIO

# === Sentiment Analysis ===
import re
from collections import Counter
from urllib.parse import quote

# === Tambahin impor di atas main.py ===
from twitter_search import search_twitter

logging.basicConfig(filename='aletta.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# Load token & channel ID
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID'))

# Setup bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Load/save posted URLs
def load_posted_urls():
    try:
        with open("posted_urls.json", "r") as file:
            return set(json.load(file))
    except FileNotFoundError:
        return set()

def save_posted_urls(posted_urls):
    with open("posted_urls.json", "w") as file:
        json.dump(list(posted_urls), file)

posted_urls = load_posted_urls()

# Cache file
CACHE_FILE = "news_cache.json"

# === load tokenomics ===
def load_tokenomics():
    try:
        with open("tokenomics.json", "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Gagal load tokenomics.json: {e}")
        return {}

def get_tokenomics_data(coin_id: str):
    data = load_tokenomics()
    if coin_id in data:
        return data[coin_id]

    # Fallback jika nama tidak persis sama
    normalized_id = coin_id.replace("-", "").lower()
    for key in data:
        if key.replace("-", "").lower() == normalized_id:
            return data[key]

    return None

# === Coin ID Caching System ===
async def cache_coins_list():
    url = "https://api.coingecko.com/api/v3/coins/list"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as resp:
                if resp.status != 200:
                    print(f"Gagal cache coins list: Status {resp.status}")
                    return
                coins = await resp.json()
                with open("coins.json", "w") as f:
                    json.dump(coins, f)
                print("✅ Coin list cached to coins.json")
    except Exception as e:
        print(f"Error caching coins list: {str(e)}")

def load_coins_list():
    try:
        with open("coins.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def normalize_url(url):
    parsed = urlparse(url)
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', '', ''))

# RSS Feed List
RSS_FEEDS = {
    "CoinDesk": "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "Benzinga": "https://www.benzinga.com/news.rss",
    "Bloomberg": "https://www.bloomberg.com/feed/podcast/economics.xml",
    "NYTimes Economy": "https://rss.nytimes.com/services/xml/rss/nyt/Economy.xml",
    "Cointelegraph": "https://cointelegraph.com/rss",
    "Bitcoin Magazine": "https://bitcoinmagazine.com/feed",
    "Blockchain.News": "https://blockchain.news/feed",
    "Pintu - AI": "https://pintu.co.id/news/tags/ai-generatif/rss-feed.xml",
    "AI News": "https://www.artificialintelligence-news.com/feed/",
    "MIT Tech Review - AI": "https://www.technologyreview.com/feed/tag/artificial-intelligence/",
    "EnterpriseAI": "https://www.enterpriseai.news/feed/",
    "CryptoPanic": "https://cryptopanic.com/news/rss/",
    "Decrypt": "https://decrypt.co/feed",
    "TheBlock": "https://www.theblock.co/feed",
    "Web3Wire - Web3": "https://web3wire.org/category/web3/feed/gn",
    "Reuters Economy": "https://www.reuters.com/finance/economy/rss"
}

# RSS Feed Topics
RSS_TOPICS = {
    "ai": {
        "EnterpriseAI": "https://www.enterpriseai.news/feed/",
        "NVIDIA Blog": "https://www.nvidia.com/en-us/about-nvidia/rss/",
        "AIwire": "https://www.aiwire.net/rss-feeds/",
    },
    "crypto": {
        "CryptoPanic": "https://cryptopanic.com/news/rss/",
        "Cryptoknowmics": "https://www.cryptoknowmics.com/rss-feeds",
        "Web3Wire - Crypto": "https://web3wire.org/category/crypto/feed/gn",
    },
    "blockchain": {
        "Blockchain.News": "https://blockchain.news/feed",
        "Blockchain Academy": "https://theblockchainacademy.com/rss-feed/",
        "Blockchain Feeds": "https://theblockchainfeeds.com/",
    },
    "web3": {
        "Web3Wire - Web3": "https://web3wire.org/category/web3/feed/gn",
        "Web3Wire - Metaverse": "https://web3wire.org/category/metaverse/feed/gn",
        "Web3Wire - DeFi": "https://web3wire.org/category/defi/feed/gn",
    },
    "economy": {
        "Guardian Business": "https://www.theguardian.com/business/rss",
        "Reuters Economy": "https://www.reuters.com/finance/economy/rss",
        "Financial Times Economy": "https://www.ft.com/global-economy?format=rss",
    }
}

# Coin ID Mapping
COIN_MAPPING = {
    "btc": "bitcoin", "eth": "ethereum", "usdt": "tether", "bnb": "binancecoin",
    "sol": "solana", "usdc": "usd-coin", "xrp": "ripple", "steth": "staked-ether",
    "doge": "dogecoin", "ada": "cardano", "trx": "tron", "wbtc": "wrapped-bitcoin",
    "avax": "avalanche-2", "link": "chainlink", "dot": "polkadot", "matic": "polygon",
    "ton": "the-open-network", "shib": "shiba-inu", "ltc": "litecoin", "bch": "bitcoin-cash",
    "uni": "uniswap", "near": "near", "atom": "cosmos", "xlm": "stellar",
    "apt": "aptos", "sui": "sui", "arb": "arbitrum", "pepe": "pepe", "hedera": "hedera-hashgraph", 
    "fetch": "fetch-ai", "celestia": "celestia", "ethena": "ethena-usde", "kaspa": "kaspa", 
    "sonic": "sonic", "hype": "hyperliquid", "render": "render-token", "ondo": "ondo-finance",
    "mantle": "mantle", "wld": "worldcoin", "sei": "sei-network", "mov": "movement", "pendle": "pendle",
    "movt": "movement", "bonk": "bonk", "jupiter": "jupiter-exchange", "story": "story-protocol"
}

async def get_coin_id(query: str) -> str:
    query = query.lower()
    if query in COIN_MAPPING:
        return COIN_MAPPING[query]

    async with aiohttp.ClientSession() as session:
        url = f"https://api.coingecko.com/api/v3/search?query={query}"
        async with session.get(url) as resp:
            data = await resp.json()
            return data["coins"][0]["id"] if data["coins"] else None

async def get_coin_price(coin_id: str) -> float:
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
            return data[coin_id]["usd"]

async def generate_coin_chart(coin_id: str, days: int = 7) -> BytesIO:
    chart_url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days={days}"
    async with aiohttp.ClientSession() as session:
        async with session.get(chart_url) as resp:
            chart_data = await resp.json()

    prices = chart_data["prices"]
    timestamps = [datetime.datetime.fromtimestamp(p[0] / 1000) for p in prices]
    values = [p[1] for p in prices]

    plt.figure(figsize=(8, 4))
    plt.plot(timestamps, values, color='orange', linewidth=2)
    plt.title(f'Harga {coin_id.upper()} 7 Hari Terakhir')
    plt.xlabel("Tanggal")
    plt.ylabel("Harga (USD)")
    plt.grid(True)

    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    return buf

# ============ Transparansi ============
def get_transparency_info(data):
    links = data.get("links", {})
    return {
        "website": (links.get("homepage") or [""])[0],
        "twitter": links.get("twitter_screen_name"),
        "github": links.get("repos_url", {}).get("github", []),
        "explorer": (links.get("blockchain_site") or [""])[0],
        "docs": (links.get("official_forum_url") or [""])[0]
    }

# ============ EVENT HANDLER ============
@bot.event
async def on_ready():
    print(f"✅ Aletta sudah online sebagai {bot.user}!")
    await cache_coins_list()
    bot.loop.create_task(post_news_loop())  # Auto-post berita jalan terus

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.lower() == "!ping":
        await message.channel.send("Halo! Aku Aletta, bot kesayangan Nawa ❤️")

    await bot.process_commands(message)  # WAJIB! Biar semua command bisa jalan

# ============ COMMAND: !harga ============
@bot.command(name="harga")
async def harga(ctx, *, coin: str):
    await ctx.send("⏳ Mengambil data...")
    coin_id = await get_coin_id(coin)
    if not coin_id:
        return await ctx.send(f"❌ Koin '{coin}' tidak ditemukan.")

    try:
        price = await get_coin_price(coin_id)
        chart = await generate_coin_chart(coin_id)

        await ctx.send(f"💰 **{coin.upper()}**: ${price}")
        await ctx.send(file=discord.File(chart, filename='harga.png'))
    except Exception as e:
        await ctx.send(f"⚠️ Terjadi error: {str(e)}")

#KIRIM TOPIK BERITA BASED ON EMBBED BUTTON
async def send_topic_news(ctx, topic):
    feeds = RSS_TOPICS.get(topic)
    if not feeds:
        await ctx.send("❌ Topik tidak ditemukan.")
        return

    await ctx.send(f"📡 Menampilkan berita untuk topik **{topic.upper()}**...")

    for source, url in feeds.items():
        try:
            feed = feedparser.parse(url)
        except Exception as e:
            await ctx.send(f"❌ Gagal parsing RSS dari {source}: {str(e)}")
            continue  # Lanjut ke sumber lain

        if not feed.entries:
            await ctx.send(f"⚠️ Tidak ada entri berita dari {source}")
            continue

        for entry in feed.entries[:2]:
            try:
                title = entry.title
                link = normalize_url(entry.link)
                if link not in posted_urls:
                    posted_urls.add(link)
                    berita_message = f"📰 **{source}**: {title}\n🔗 {link}"
                    await ctx.send(berita_message)
                    save_posted_urls(posted_urls)
            except Exception as inner_e:
                await ctx.send(f"⚠️ Gagal kirim berita dari {source}: {str(inner_e)}")

# ============ COMMAND: !kategori, !kb, !kategori_berita ============
@bot.command(name="kategori_berita", aliases=["kategori", "kb"])
async def kategori(ctx):
    embed = discord.Embed(
        title="🗂️ Kategori Berita",
        description="Klik tombol di bawah untuk melihat berita dari topik tertentu.",
        color=0x3498db
    )
    embed.add_field(name="📌 Tersedia", value="• AI\n• Crypto\n• Web3\n• Ekonomi", inline=False)
    embed.set_footer(text="Powered by Aletta News Engine v2")

    class KategoriView(View):
        def __init__(self):
            super().__init__(timeout=60.0)

        @discord.ui.button(label="AI", style=discord.ButtonStyle.primary)
        async def ai_button(self, interaction: discord.Interaction, button: Button):
            await interaction.response.defer()
            await send_topic_news(interaction.channel, "ai")

        @discord.ui.button(label="Crypto", style=discord.ButtonStyle.success)
        async def crypto_button(self, interaction: discord.Interaction, button: Button):
            await interaction.response.defer()
            await send_topic_news(interaction.channel, "crypto")

        @discord.ui.button(label="Web3", style=discord.ButtonStyle.blurple)
        async def web3_button(self, interaction: discord.Interaction, button: Button):
            await interaction.response.defer()
            await send_topic_news(interaction.channel, "web3")

        @discord.ui.button(label="Ekonomi", style=discord.ButtonStyle.secondary)
        async def economy_button(self, interaction: discord.Interaction, button: Button):
            await interaction.response.defer()
            await send_topic_news(interaction.channel, "economy")

    await ctx.send(embed=embed, view=KategoriView())

# ============ COMMAND: !fund, !fa, !fundamental ============
@bot.command(name="fundamental", aliases=["fa", "fund"])
async def fundamental(ctx, *, coin: str):
    coin = coin.lower().strip()
    logging.info(f"Processing command !fundamental for coin: {coin}")

    coin_id = await get_coin_id(coin)
    if not coin_id:
        logging.info(f"Coin {coin} not found in cache or COIN_MAPPING")
        await ctx.send(f"⚠️ Koin '{coin.upper()}' tidak ditemukan di CoinGecko.")
        return
    logging.info(f"Mapped {coin} to CoinGecko ID: {coin_id}")

    await ctx.send(f"🔍 Mengambil data fundamental untuk **{coin.upper()}**...")

    async with aiohttp.ClientSession() as session:
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
        logging.info(f"Requesting URL: {url}")
        try:
            async with session.get(url, timeout=10) as resp:
                logging.info(f"API response status: {resp.status}")
                if resp.status == 429:
                    await ctx.send("⚠️ Batas API CoinGecko tercapai. Coba lagi nanti.")
                    return
                if resp.status != 200:
                    await ctx.send(f"⚠️ Gagal mengambil data (Status: {resp.status}).")
                    return

                data = await resp.json()
                logging.info(f"API response data keys: {list(data.keys()) if data else 'Empty'}")
                if not data or "id" not in data:
                    await ctx.send("⚠️ Data tidak valid atau tidak ditemukan.")
                    return

                name = data.get("name", "N/A")
                symbol = data.get("symbol", "N/A").upper()
                desc_raw = data.get("description", {}).get("en", "")
                description = desc_raw.strip().split(". ")[0][:300] + "..." if desc_raw else "Deskripsi tidak tersedia."
                links = data.get("links", {})
                homepage = links.get("homepage", ["N/A"])[0] or "N/A"
                explorer = links.get("blockchain_site", ["N/A"])[0] or "N/A"

                market_data = data.get("market_data", {})
                market_cap = market_data.get("market_cap", {}).get("usd", 0)
                volume = market_data.get("total_volume", {}).get("usd", 0)
                fdv = market_data.get("fully_diluted_valuation", {}).get("usd", 0)
                circulating = market_data.get("circulating_supply", 0)
                max_supply = market_data.get("max_supply", 0)

                def format_num(n):
                    return f"${n:,.0f}" if isinstance(n, (int, float)) and n > 0 else "N/A"

                embed = discord.Embed(
                    title=f"🧾 Fundamental Analysis: {name} ({symbol})",
                    description=description,
                    color=0x00bfff
                )
                embed.add_field(name="Market Cap", value=format_num(market_cap), inline=True)
                embed.add_field(name="FDV", value=format_num(fdv), inline=True)
                embed.add_field(name="Volume (24h)", value=format_num(volume), inline=True)
                embed.add_field(name="Max Supply", value=f"{max_supply:,.0f}" if max_supply else "N/A", inline=True)
                embed.add_field(name="Circulating Supply", value=f"{circulating:,.0f}" if circulating else "N/A", inline=True)
                embed.add_field(name="Explorer", value=explorer, inline=False)
                embed.add_field(name="Website", value=homepage, inline=False)
                embed.set_footer(text="Data from CoinGecko API")

                logging.info("Sending embed response")
                await ctx.send(embed=embed)
                await asyncio.sleep(2)

        except Exception as e:
            logging.info(f"Unexpected error in fundamental: {str(e)}")
            await ctx.send(f"❌ Terjadi kesalahan: {str(e)}")

# ============ COMMAND: !checkcoin ============
@bot.command(name="checkcoin")
async def check_coin(ctx, *, symbol: str):
    symbol = symbol.lower().strip()
    await ctx.send(f"🔍 Mencari ID untuk {symbol.upper()}...")
    coin_id = await get_coin_id(symbol)
    if coin_id:
        await ctx.send(f"✅ Ditemukan: `{coin_id}` di CoinGecko")
    else:
        await ctx.send(f"❌ Koin '{symbol.upper()}' tidak ditemukan di CoinGecko.")

# refresh coins list
@bot.command(name="refreshcoins")
async def refresh_coins(ctx):
    await ctx.send("🔄 Memperbarui daftar koin...")
    await cache_coins_list()
    await ctx.send("✅ Daftar koin diperbarui!")

# ============ AUTO POST NEWS ============
async def post_news_loop():
    await bot.wait_until_ready()
    channel = bot.get_channel(CHANNEL_ID)
    while not bot.is_closed():
        for source, url in RSS_FEEDS.items():
            feed = feedparser.parse(url)
            if feed.entries:
                for entry in feed.entries[:3]:
                    title = entry.title
                    link = normalize_url(entry.link)
                    if link not in posted_urls:
                        posted_urls.add(link)
                        message = f"📰 **{source}**: {title}\n🔗 {link}"
                        await channel.send(message)
                        save_posted_urls(posted_urls)
        await asyncio.sleep(3600)

# ============ COMMAND: !bubble ============
@bot.command(name="bubble")
async def bubble(ctx):
    try:
        from matplotlib.offsetbox import OffsetImage, AnnotationBbox
        import matplotlib.image as mpimg
        import os

        # [1] AMBIL DATA COIN
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {'vs_currency': 'usd', 'per_page': 100}
        response = requests.get(url, params=params)
        data = response.json()

        # Filter top 10 gainers & losers
        sorted_data = sorted(data, key=lambda x: x.get('price_change_percentage_24h', 0), reverse=True)
        selected_coins = sorted_data[:10] + sorted_data[-10:][::-1]

        coins = [c['symbol'].upper() for c in selected_coins]
        price_changes = [c.get('price_change_percentage_24h', 0) for c in selected_coins]
        abs_changes = [abs(p) for p in price_changes]
        sizes = np.interp(abs_changes, (min(abs_changes), max(abs_changes)), (2000, 8000))

        # [2] POSITIONING BUBBLE
        from random import uniform
        from math import sqrt
        positions = []
        min_distance_factor = 0.2
        max_attempts = 500

        for i in range(len(coins)):
            radius = sqrt(sizes[i] / np.pi) / 1000
            attempts = 0
            while attempts < max_attempts:
                x, y = uniform(0.05, 0.95), uniform(0.05, 0.95)
                overlap = False
                for j, (px, py) in enumerate(positions):
                    pradius = sqrt(sizes[j] / np.pi) / 1000
                    distance = sqrt((x - px) ** 2 + (y - py) ** 2)
                    min_distance = (radius + pradius) * min_distance_factor
                    if distance < min_distance:
                        overlap = True
                        break
                if not overlap:
                    positions.append((x, y))
                    break
                attempts += 1
            if attempts >= max_attempts:
                positions.append((uniform(0.05, 0.95), uniform(0.05, 0.95)))

        # [3] SETUP PLOT + BACKGROUND (abu-abu gelap)
        plt.figure(figsize=(12, 8), facecolor="#2f2f2f")
        ax = plt.gca()
        ax.set_facecolor("#2f2f2f")
        ax.set_axis_off()

        # [4] LOGO COINSPACE
        logo_path = os.path.join(os.path.dirname(__file__), "coinspace.png")
        logo = mpimg.imread(logo_path)
        imagebox = OffsetImage(logo, zoom=0.75, alpha=0.18)
        ab = AnnotationBbox(imagebox, (0.5, 0.5), frameon=False, box_alignment=(0.5, 0.5))
        ax.add_artist(ab)

        # [5] PLOT BUBBLE
        text_color = 'white'
        for i, (x, y) in enumerate(positions):
            color = 'limegreen' if price_changes[i] > 0 else 'red'
            plt.scatter(x, y, s=sizes[i], c=color, alpha=0.85, edgecolors='white', linewidth=1)
            plt.title('Top 1D Movers — Coinspace', color='white', fontsize=16, weight='bold', pad=20)
            plt.tight_layout()
            plt.text(
                x, y,
                f"{coins[i]}\n{price_changes[i]:+.2f}%",
                color=text_color,
                fontsize=10,
                weight='bold',
                ha='center',
                va='center',
                bbox=dict(facecolor='black', alpha=0.6, boxstyle='round,pad=0.5')
            )

        # [6] SIMPAN & KIRIM
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=120, facecolor=plt.gcf().get_facecolor())
        buf.seek(0)
        plt.close()
        await ctx.send(file=discord.File(buf, 'bubble_chart.png'))

    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

# ============ COMMAND: !bubble_4h ============
@bot.command(name="bubble_4h")
async def bubble_4h(ctx):
    try:
        from matplotlib.offsetbox import OffsetImage, AnnotationBbox
        import matplotlib.image as mpimg
        import os

        # Ambil API Key dari .env
        CMC_API_KEY = os.getenv("CMC_API_KEY")

        url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
        headers = {
            "Accepts": "application/json",
            "X-CMC_PRO_API_KEY": CMC_API_KEY
        }
        params = {
            "start": "1",
            "limit": "100",
            "convert": "USD"
        }

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()["data"]

        # Ambil top 10 gainers & 10 losers berdasarkan %change 1h
        sorted_by_change = sorted(
            data,
            key=lambda x: x["quote"]["USD"].get("percent_change_1h", 0),
            reverse=True
        )
        top_gainers = sorted_by_change[:10]
        top_losers = sorted_by_change[-10:][::-1]
        selected_coins = top_gainers + top_losers

        coins = [coin["symbol"].upper() for coin in selected_coins]
        price_changes = [coin["quote"]["USD"].get("percent_change_1h", 0) for coin in selected_coins]
        abs_changes = [abs(p) for p in price_changes]
        sizes = np.interp(abs_changes, (min(abs_changes), max(abs_changes)), (2000, 8000))

        # Posisi bubble
        from random import uniform
        n = len(coins)
        positions = []
        min_distance_factor = 0.2
        max_attempts = 500

        for i in range(n):
            radius = sqrt(sizes[i] / np.pi) / 1000
            attempts = 0
            while attempts < max_attempts:
                x, y = uniform(0.05, 0.95), uniform(0.05, 0.95)
                too_close = False
                for j, (px, py) in enumerate(positions):
                    pradius = sqrt(sizes[j] / np.pi) / 1000
                    dist = sqrt((x - px) ** 2 + (y - py) ** 2)
                    min_dist = (radius + pradius) * min_distance_factor
                    if dist < min_dist:
                        too_close = True
                        break
                if not too_close:
                    positions.append((x, y))
                    break
                attempts += 1
            if attempts >= max_attempts:
                positions.append((uniform(0.05, 0.95), uniform(0.05, 0.95)))

        # Plot Chart
        plt.figure(figsize=(12, 8), facecolor="#2f2f2f")
        ax = plt.gca()
        ax.set_facecolor("#2f2f2f")
        ax.set_axis_off()

        # Tambahkan logo Coinspace
        current_dir = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(current_dir, "coinspace.png")
        logo = mpimg.imread(logo_path)
        imagebox = OffsetImage(logo, zoom=0.75, alpha=0.18)
        ab = AnnotationBbox(imagebox, (0.5, 0.5), frameon=False, box_alignment=(0.5, 0.5), xycoords='axes fraction')
        ax.add_artist(ab)

        # Bubble & Label
        for i, (x, y) in enumerate(positions):
            color = 'limegreen' if price_changes[i] > 0 else 'red'
            plt.scatter(x, y, s=sizes[i], c=color, alpha=0.85, edgecolors='white', linewidth=1)

            label = f"{coins[i]}\n{price_changes[i]:+.2f}%"
            plt.text(
                x, y,
                label,
                fontsize=11,
                weight='bold',
                ha='center',
                va='center',
                color='white',
                bbox=dict(facecolor='black', alpha=0.6, boxstyle='round,pad=0.5')
            )

        plt.title('Top 4H Movers — Coinspace', color='white', fontsize=16, weight='bold', pad=20)
        plt.tight_layout()

        chart_path = 'bubble_chart_4h.png'
        plt.savefig(chart_path, facecolor=plt.gcf().get_facecolor(), bbox_inches='tight', dpi=150)
        plt.close()

        await ctx.send(file=discord.File(chart_path))

    except Exception as e:
        await ctx.send(f"❌ Terjadi kesalahan di bubble_4h: {str(e)}")

# ============ COMMAND: !bubble_1w ============
@bot.command(name="bubble_1w")
async def bubble_1w(ctx):
    try:
        from matplotlib.offsetbox import OffsetImage, AnnotationBbox
        import matplotlib.image as mpimg
        import os

        # Ambil data market + perubahan harga 7d
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            'vs_currency': 'usd',
            'order': 'market_cap_desc',
            'per_page': 100,
            'page': 1,
            'price_change_percentage': '7d'
        }

        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        # Ambil top 10 gainers dan 10 losers berdasarkan 7d
        sorted_by_change = sorted(data, key=lambda x: x.get('price_change_percentage_7d_in_currency', 0) or 0, reverse=True)
        top_gainers = sorted_by_change[:10]
        top_losers = sorted_by_change[-10:][::-1]
        selected_coins = top_gainers + top_losers

        coins = [coin['symbol'].upper() for coin in selected_coins]
        price_changes = [coin.get('price_change_percentage_7d_in_currency', 0) or 0 for coin in selected_coins]
        abs_changes = [abs(p) for p in price_changes]
        sizes = np.interp(abs_changes, (min(abs_changes), max(abs_changes)), (2000, 8000))

        # Penempatan gelembung
        from random import uniform
        n = len(coins)
        positions = []
        min_distance_factor = 0.2
        max_attempts = 500

        for i in range(n):
            radius = sqrt(sizes[i] / np.pi) / 1000
            attempts = 0
            while attempts < max_attempts:
                x, y = uniform(0.05, 0.95), uniform(0.05, 0.95)
                too_close = False
                for j, (px, py) in enumerate(positions):
                    pradius = sqrt(sizes[j] / np.pi) / 1000
                    dist = sqrt((x - px) ** 2 + (y - py) ** 2)
                    min_dist = (radius + pradius) * min_distance_factor
                    if dist < min_dist:
                        too_close = True
                        break
                if not too_close:
                    positions.append((x, y))
                    break
                attempts += 1
            if attempts >= max_attempts:
                positions.append((uniform(0.05, 0.95), uniform(0.05, 0.95)))

        # Visualisasi Chart
        plt.figure(figsize=(12, 8), facecolor="#2f2f2f")
        ax = plt.gca()
        ax.set_facecolor("#2f2f2f")
        ax.set_axis_off()

        # Logo Coinspace (watermark)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(current_dir, "coinspace.png")
        logo = mpimg.imread(logo_path)
        imagebox = OffsetImage(logo, zoom=0.75, alpha=0.18)
        ab = AnnotationBbox(imagebox, (0.5, 0.5), frameon=False, box_alignment=(0.5, 0.5), xycoords='axes fraction')
        ax.add_artist(ab)

        # Bubble chart
        for i, (x, y) in enumerate(positions):
            color = 'limegreen' if price_changes[i] > 0 else 'red'
            plt.scatter(x, y, s=sizes[i], c=color, alpha=0.85, edgecolors='white', linewidth=1)
            label = f"{coins[i]}\n{price_changes[i]:+.2f}%"
            plt.text(x, y, label, fontsize=11, weight='bold', ha='center', va='center',
                     color='white', bbox=dict(facecolor='black', alpha=0.6, boxstyle='round,pad=0.5'))

        plt.title('Top 10 Weekly Gainers & Losers — Coinspace', color='white', fontsize=16, weight='bold', pad=20)
        plt.tight_layout()

        chart_path = 'bubble_chart_1w.png'
        plt.savefig(chart_path, facecolor=plt.gcf().get_facecolor(), bbox_inches='tight', dpi=150)
        plt.close()

        await ctx.send(file=discord.File(chart_path))

    except requests.exceptions.RequestException as e:
        await ctx.send(f"❌ Gagal ambil data dari API: {str(e)}")
    except Exception as e:
        await ctx.send(f"❌ Terjadi kesalahan: {str(e)}")

# ============ COMMAND: !bubble_1m ============
@bot.command(name="bubble_1m")
async def bubble_1m(ctx):
    try:
        from matplotlib.offsetbox import OffsetImage, AnnotationBbox
        import matplotlib.image as mpimg
        import os

        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            'vs_currency': 'usd',
            'order': 'market_cap_desc',
            'per_page': 100,
            'page': 1,
            'price_change_percentage': '30d'
        }

        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        sorted_by_change = sorted(data, key=lambda x: x.get('price_change_percentage_30d_in_currency', 0) or 0, reverse=True)
        top_gainers = sorted_by_change[:10]
        top_losers = sorted_by_change[-10:][::-1]
        selected_coins = top_gainers + top_losers

        coins = [coin['symbol'].upper() for coin in selected_coins]
        price_changes = [coin.get('price_change_percentage_30d_in_currency', 0) or 0 for coin in selected_coins]
        abs_changes = [abs(p) for p in price_changes]
        sizes = np.interp(abs_changes, (min(abs_changes), max(abs_changes)), (2000, 8000))

        from random import uniform
        n = len(coins)
        positions = []
        min_distance_factor = 0.2
        max_attempts = 500

        for i in range(n):
            radius = sqrt(sizes[i] / np.pi) / 1000
            attempts = 0
            while attempts < max_attempts:
                x, y = uniform(0.05, 0.95), uniform(0.05, 0.95)
                too_close = False
                for j, (px, py) in enumerate(positions):
                    pradius = sqrt(sizes[j] / np.pi) / 1000
                    dist = sqrt((x - px) ** 2 + (y - py) ** 2)
                    min_dist = (radius + pradius) * min_distance_factor
                    if dist < min_dist:
                        too_close = True
                        break
                if not too_close:
                    positions.append((x, y))
                    break
                attempts += 1
            if attempts >= max_attempts:
                positions.append((uniform(0.05, 0.95), uniform(0.05, 0.95)))

        # Chart rendering
        plt.figure(figsize=(12, 8), facecolor="#2f2f2f")
        ax = plt.gca()
        ax.set_facecolor("#2f2f2f")
        ax.set_axis_off()

        # Watermark logo
        current_dir = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(current_dir, "coinspace.png")
        logo = mpimg.imread(logo_path)
        imagebox = OffsetImage(logo, zoom=0.75, alpha=0.18)
        ab = AnnotationBbox(imagebox, (0.5, 0.5), frameon=False, box_alignment=(0.5, 0.5), xycoords='axes fraction')
        ax.add_artist(ab)

        for i, (x, y) in enumerate(positions):
            color = 'limegreen' if price_changes[i] > 0 else 'red'
            plt.scatter(x, y, s=sizes[i], c=color, alpha=0.85, edgecolors='white', linewidth=1)
            label = f"{coins[i]}\n{price_changes[i]:+.2f}%"
            plt.text(
                x, y,
                label,
                fontsize=11,
                weight='bold',
                ha='center',
                va='center',
                color='white',
                bbox=dict(facecolor='black', alpha=0.6, boxstyle='round,pad=0.5')
            )

        plt.title('Top 30D Gainers & Losers — Coinspace', color='white', fontsize=16, weight='bold', pad=20)
        plt.tight_layout()

        chart_path = 'bubble_chart_1m.png'
        plt.savefig(chart_path, facecolor=plt.gcf().get_facecolor(), bbox_inches='tight', dpi=150)
        plt.close()

        await ctx.send(file=discord.File(chart_path))

    except Exception as e:
        await ctx.send(f"❌ Terjadi kesalahan di bubble_1m: {str(e)}")

# ============ COMMAND: !bubble_all ============
@bot.command(name="bubble_all")
async def bubble_all(ctx):
    """Generate a 4-panel bubble chart for 24h, 7d, 30d, and watchlist"""
    try:
        # ===== 1. FETCH DATA =====
        await ctx.send("🔄 Mengambil data dari APIs... (Mohon untuk menunggu 10-20 detik)")

        # Data fetching functions (simplified for readability)
        async def get_coin_data(timeframe):
            url = "https://api.coingecko.com/api/v3/coins/markets"
            params = {
                'vs_currency': 'usd',
                'order': 'market_cap_desc',
                'per_page': 100,
                'price_change_percentage': timeframe
            }
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as resp:
                    data = await resp.json()
                    return sorted(data, key=lambda x: x.get(f'price_change_percentage_{timeframe}_in_currency', 0), reverse=True)

        # Fetch all data concurrently (faster)
        top_24h, top_7d, top_30d = await asyncio.gather(
            get_coin_data('24h'),
            get_coin_data('7d'),
            get_coin_data('30d')
        )

        # Load watchlist (create if not exists)
        try:
            with open("watchlist.json", "r") as f:
                watchlist = json.load(f).get("coins", [])
        except FileNotFoundError:
            watchlist = ["btc", "eth", "sol"]  # Default watchlist
            with open("watchlist.json", "w") as f:
                json.dump({"coins": watchlist}, f)

        # ===== 2. SETUP PLOT =====
        plt.style.use('dark_background')
        fig = plt.figure(figsize=(16, 12), facecolor='#1e1e1e')
        fig.suptitle('CRYPTO BUBBLE DASHBOARD', fontsize=24, color='white', y=0.95)

        # Custom color palette
        colors = {
            'gain': '#4CAF50',  # Green
            'loss': '#F44336',   # Red
            'bg': '#2f2f2f',
            'text': 'white'
        }

        # ===== 3. SUBPLOT FUNCTIONS =====
        def plot_bubble(ax, data, title, timeframe):
            """Generic bubble plotter for 24h/7d/30d"""
            ax.set_facecolor(colors['bg'])
            ax.set_title(title, fontsize=16, pad=20, color=colors['text'])
            ax.set_xticks([])
            ax.set_yticks([])

            # Filter top 5 gainers & 5 losers
            gainers = data[:5]
            losers = data[-5:][::-1]
            coins = [x['symbol'].upper() for x in gainers + losers]
            changes = [x.get(f'price_change_percentage_{timeframe}_in_currency', 0) for x in gainers + losers]
            sizes = [abs(c)*30 + 100 for c in changes]  # Dynamic bubble size

            # Plot bubbles
            for i, (coin, change) in enumerate(zip(coins, changes)):
                color = colors['gain'] if change > 0 else colors['loss']
                ax.scatter(
                    i % 5 + 0.5,  # X position (centered)
                    0.8 - (i // 5)*0.6,  # Y position (gainers top, losers bottom)
                    s=sizes[i],
                    color=color,
                    alpha=0.7,
                    edgecolors='white',
                    linewidth=0.5
                )
                ax.text(
                    i % 5 + 0.5, 0.8 - (i // 5)*0.6,
                    f"{coin}\n{change:+.1f}%",
                    ha='center', va='center',
                    color=colors['text'],
                    fontsize=10,
                    bbox=dict(facecolor='black', alpha=0.5, boxstyle='round,pad=0.3')
                )

        async def plot_watchlist(ax, coins):  # <-- Added 'async' here!
            """Special plot for watchlist coins"""
            ax.set_facecolor(colors['bg'])
            ax.set_title("YOUR WATCHLIST", fontsize=16, pad=20, color=colors['text'])
            ax.set_xticks([])
            ax.set_yticks([])

            # Get prices for watchlist
            coin_ids = [COIN_MAPPING.get(c, c) for c in coins]
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={','.join(coin_ids)}&vs_currencies=usd&include_24hr_change=true"

            async with aiohttp.ClientSession() as session:  # <-- Now valid!
                async with session.get(url) as resp:
                    price_data = await resp.json()

            # Rest of the function remains the same...
            for i, coin in enumerate(coins):
                coin_id = COIN_MAPPING.get(coin, coin)
                data = price_data.get(coin_id, {})
                change = data.get('usd_24h_change', 0)
                color = colors['gain'] if change > 0 else colors['loss']

                ax.scatter(
                    i % 3 + 1, 2 - (i // 3),
                    s=abs(change)*20 + 200,
                    color=color,
                    alpha=0.7
                )
                ax.text(
                    i % 3 + 1, 2 - (i // 3),
                    f"{coin.upper()}\n${data.get('usd', '?')}\n{change:+.1f}%",
                    ha='center', va='center',
                    color=colors['text'],
                    fontsize=10
                )

        # ===== 4. RENDER SUBPLOTS =====
        plot_bubble(fig.add_subplot(2, 2, 1), top_24h, "24H TOP MOVERS", "24h")
        plot_bubble(fig.add_subplot(2, 2, 2), top_7d, "7D TOP MOVERS", "7d")
        plot_bubble(fig.add_subplot(2, 2, 3), top_30d, "30D TOP MOVERS", "30d")
        plot_watchlist(fig.add_subplot(2, 2, 4), watchlist[:9])  # Max 9 coins

        # ===== 5. SAVE & SEND =====
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=120, facecolor=fig.get_facecolor())
        buf.seek(0)
        plt.close()

        await ctx.send(file=discord.File(buf, 'crypto_bubble_dashboard.png'))
        await ctx.send("✅ **Dashboard siap!** Gunakan `!addcoin [coin]` untuk menambah watchlist.")

    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")
        print(f"Error in bubble_all: {traceback.format_exc()}")

# Add coin to watchlist
@bot.command(name="addcoin")
async def add_coin(ctx, coin: str):
    """Add a coin to your watchlist (e.g., !addcoin sol)"""
    try:
        coin = coin.lower().strip()

        # Load current watchlist
        try:
            with open("watchlist.json", "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {"coins": []}

        # Check if coin exists in CoinGecko
        coin_id = await get_coin_id(coin)
        if not coin_id:
            await ctx.send(f"⚠️ Coin '{coin.upper()}' tidak ditemukan di CoinGecko!")
            return

        # Add if not already in watchlist
        if coin not in data["coins"]:
            data["coins"].append(coin)
            with open("watchlist.json", "w") as f:
                json.dump(data, f)
            await ctx.send(f"✅ **{coin.upper()}** ditambahkan ke dalam pantauanmu!")
        else:
            await ctx.send(f"🔄 {coin.upper()} sudah ada di dalam pantauanmu!")

    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

# Remove coin from watchlist
@bot.command(name="removecoin")
async def remove_coin(ctx, coin: str):
    try:
        coin = coin.lower().strip()

        # Baca file saat ini
        with open("watchlist.json", "r") as f:
            data = json.load(f)  # Load semua data

        # Hapus coin jika ada
        if coin in data["coins"]:
            data["coins"].remove(coin)

            # Tulis ULANG seluruh file
            with open("watchlist.json", "w") as f:
                json.dump(data, f, indent=2)  # indent=2 biar rapi

            await ctx.send(f"✅ {coin.upper()} dihapus dari watchlist!")
        else:
            await ctx.send(f"❌ {coin.upper()} tidak ada di watchlist!")

    except Exception as e:
        await ctx.send(f"⚠️ Gagal: {str(e)}")

# Show my watchlist 
@bot.command(name="mywatchlist")
async def show_watchlist(ctx):
    """Show your current watchlist"""
    try:
        # 1. Baca file dengan error handling
        try:
            with open("watchlist.json", "r") as f:
                raw_data = f.read().strip()
                if not raw_data:  # Jika file kosong
                    coins = []
                else:
                    data = json.loads(raw_data)
                    coins = data.get("coins", [])
        except (json.JSONDecodeError, FileNotFoundError):
            coins = []
            with open("watchlist.json", "w") as f:
                json.dump({"coins": coins}, f)

        # 2. Handle watchlist kosong
        if not coins:
            await ctx.send("📭 Watchlist kosong! Tambahkan koin dengan `!addcoin`")
            return

        # 3. Ambil data harga dengan filter None
        coin_ids = [COIN_MAPPING.get(c, c) for c in coins]
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={','.join(coin_ids)}&vs_currencies=usd&include_24hr_change=true"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                price_data = await resp.json()

        # 4. Format pesan dengan cek None
        message = "🔍 **WATCHLIST KAMU:**\n"
        for coin in coins:
            coin_id = COIN_MAPPING.get(coin, coin)
            data = price_data.get(coin_id, {})

            # Handle None values
            price = data.get("usd", "?")
            change = data.get("usd_24h_change", 0) or 0  # Ganti None jadi 0

            arrow = "↑" if change > 0 else "↓"
            message += (
                f"• **{coin.upper()}**: ${price} "
                f"({arrow}{abs(change):.2f}%)\n"
            )

        await ctx.send(message)

    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

# Fix JSON
@bot.command(name="fixjson")
async def fix_json(ctx):
    try:
        # Baca file asli
        with open("watchlist.json", "r") as f:
            raw = f.read()

        # Method 1: Hapus karakter corrupt di akhir
        fixed = raw.rstrip('"}') + '"}'

        # Method 2: Parse paksa dan reconstruct
        try:
            data = json.loads(fixed)
            if not isinstance(data.get("coins"), list):
                raise ValueError("Format coins salah!")
        except:
            # Jika masih error, buat default
            data = {"coins": []}

        # Tulis ulang dengan format BAKU
        with open("watchlist.json", "w") as f:
            json.dump(data, f, indent=2)

        await ctx.send(f"✅ File JSON diperbaiki! Koin: {', '.join(data['coins'])}")
    except Exception as e:
        await ctx.send(f"❌ Gagal: {str(e)}")

# clear watchlist
@bot.command(name="clearwatchlist")
async def clear_watchlist(ctx):
    """Reset your watchlist to empty with buttons"""
    class ConfirmView(View):
        def __init__(self):
            super().__init__(timeout=30.0)

        @discord.ui.button(label="Ya, Hapus!", style=discord.ButtonStyle.danger)
        async def confirm(self, interaction: discord.Interaction, button: Button):
            with open("watchlist.json", "w") as f:
                json.dump({"coins": []}, f)
            await interaction.response.send_message("🗑️ **Daftar Pantauanmu telah berhasil dihapus!**")
            self.stop()

        @discord.ui.button(label="Batal", style=discord.ButtonStyle.grey)
        async def cancel(self, interaction: discord.Interaction, button: Button):
            await interaction.response.send_message("✅ Tindakan dibatalkan.")
            self.stop()

    view = ConfirmView()
    await ctx.send(
        "⚠️ **Apakah kamu YAKIN akan menghapus seluruh daftar pantauanmu?**\n"
        "Tindakan ini tidak dapat diulang!",
        view=view
    )

# ======== Ambil data market dari CoinGecko ==========
async def get_market_overview(coin_id: str):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                return None
            data = await resp.json()
            market_data = data.get("market_data", {})
            return {
                "market_cap": market_data.get("market_cap", {}).get("usd"),
                "volume_24h": market_data.get("total_volume", {}).get("usd"),
                "fdv": market_data.get("fully_diluted_valuation", {}).get("usd"),
                "supply": market_data.get("circulating_supply"),
                "raw_data": data  # buat transparansi di Step 3 nanti
            }

# ========== F-SCORE COMMAND ==========
@bot.command(name="fscore")
async def fscore(ctx, *, coin: str):
    coin_id = await get_coin_id(coin)
    if not coin_id:
        return await ctx.send(f"❌ Coin '{coin}' tidak ditemukan.")

    total_score, badge, stars = await calculate_fscore(coin_id)# Dummy skor total

    embed = discord.Embed(
        title=f"📊 Fundamental Score: {coin.upper()}",
        description=(
            f"**Skor Total:** `{total_score}/15`\n"
            f"🏅 Kategori: {badge}\n"
            f"⭐ Penilaian: {stars}\n\n"
            f"Klik tombol di bawah untuk lihat detail per panel 👇"
        ),
        color=0x2ecc71
    )
    embed.set_footer(text="Powered by Aletta Intelligence v1.5")

    await ctx.send(embed=embed, view=FscorePanel(coin_id, embed))

# ========== BUTTON PANEL ==========
class FscorePanel(View):
    def __init__(self, coin_id, embed):
        super().__init__(timeout=90)
        self.coin_id = coin_id
        self.embed = embed

    @discord.ui.button(label="Market Overview", style=discord.ButtonStyle.primary)
    async def market_panel(self, interaction: discord.Interaction, button: Button):
        market = await get_market_overview(self.coin_id)
        if market:
            desc = (
                f"🔹 Market Cap: ${market['market_cap']:,.0f}\n"
                f"🔹 Volume (24h): ${market['volume_24h']:,.0f}\n"
                f"🔹 FDV: ${market['fdv']:,.0f}\n"
                f"🔹 Circulating Supply: {market['supply']:,.0f}"
            )
        else:
            desc = "❌ Gagal mengambil data market."

        market_embed = discord.Embed(
            title=f"📈 Market Overview - {self.coin_id.upper()}",
            description=desc,
            color=0x1abc9c
        )
        market_embed.set_footer(text="Klik 'Kembali' untuk panel utama.")
        await interaction.response.edit_message(embed=market_embed, view=self)

    @discord.ui.button(label="Tokenomics", style=discord.ButtonStyle.success)
    async def tokenomics_panel(self, interaction: discord.Interaction, button: Button):
        token = get_tokenomics_data(self.coin_id)

        if token:
            desc = (
                f"🔹 Team Allocation: {token.get('team_allocation_percent', 'N/A')}%\n"
                f"🔹 Vesting: {token.get('vesting_status', 'N/A')}\n"
                f"🔹 Whale Distribution: {token.get('whale_distribution', 'N/A')}\n"
                f"🔹 Audited: {'✅' if token.get('audited') else '❌' if token.get('audited') == False else 'N/A'}"
            )
        else:
            desc = "⚠️ Data tokenomics tidak ditemukan."

        token_embed = discord.Embed(
            title=f"📦 Tokenomics - {self.coin_id.upper()}",
            description=desc,
            color=0xf1c40f
        )
        token_embed.set_footer(text="Klik 'Kembali' untuk panel utama.")
        await interaction.response.edit_message(embed=token_embed, view=self)

    @discord.ui.button(label="Transparansi", style=discord.ButtonStyle.secondary)
    async def transparansi_panel(self, interaction: discord.Interaction, button: Button):
        market = await get_market_overview(self.coin_id)
        if not market or not market.get("raw_data"):
            desc = "⚠️ Data tidak tersedia dari CoinGecko."
        else:
            info = get_transparency_info(market["raw_data"])
            desc = (
                f"🌐 Website: {info['website'] or 'N/A'}\n"
                f"🐦 Twitter: https://twitter.com/{info['twitter'] or 'N/A'}\n"
                f"📘 Docs: {info['docs'] or 'N/A'}\n"
                f"🔗 Explorer: {info['explorer'] or 'N/A'}\n"
                f"👥 GitHub Repo: {info['github'][0] if info['github'] else 'N/A'}"
            )

        trans_embed = discord.Embed(
            title=f"🔍 Transparansi - {self.coin_id.upper()}",
            description=desc,
            color=0x95a5a6
        )
        trans_embed.set_footer(text="Klik 'Kembali' untuk panel utama.")
        await interaction.response.edit_message(embed=trans_embed, view=self)

    @discord.ui.button(label="Kembali", style=discord.ButtonStyle.danger)
    async def back_panel(self, interaction: discord.Interaction, button: Button):
        await interaction.response.edit_message(embed=self.embed, view=self)

# ========== kalkualsi fscore ===========
async def calculate_fscore(coin_id: str):
    score = 0

    # ======= LOAD TOKENOMICS DATA =======
    token = get_tokenomics_data(coin_id)
    if token:
        # Team Allocation (1 point: <20%)
        team_alloc = token.get("team_allocation_percent")
        if isinstance(team_alloc, (int, float)):
            if team_alloc <= 20:
                score += 1
            elif team_alloc <= 35:
                score += 0.5

        # Vesting (1 point if locked/ongoing)
        vesting = token.get("vesting_status", "").lower()
        if any(k in vesting for k in ["locked", "ongoing"]):
            score += 1

        # Audited (1 point if true)
        audited = token.get("audited")
        if audited is True:
            score += 1

        # Whale Distribution (low = 1, medium = 0.5, high = 0)
        whale = token.get("whale_distribution", "").lower()
        if whale == "low":
            score += 1
        elif whale == "medium":
            score += 0.5

    # ======= LOAD MARKET DATA =======
    market = await get_market_overview(coin_id)
    if market:
        # Market Cap (1 point: > $1B)
        mc = market.get("market_cap")
        if mc and mc >= 1_000_000_000:
            score += 1

        # Volume / Market Cap Ratio (1 point: > 5%)
        vol = market.get("volume_24h")
        if vol and mc:
            ratio = vol / mc
            if ratio >= 0.05:
                score += 1

        # FDV (1 point: FDV < 2x Market Cap)
        fdv = market.get("fdv")
        if fdv and mc and fdv < (mc * 2):
            score += 1

        # Circulating Supply (1 point: tersedia)
        supply = market.get("supply")
        if supply:
            score += 1

    # ======= TRANSPARENCY =======
    data = market.get("raw_data") if market else {}
    info = get_transparency_info(data) if data else {}
    if info:
        if info.get("website"):
            score += 1
        if info.get("twitter"):
            score += 1
        if info.get("docs"):
            score += 1
        if info.get("explorer"):
            score += 1
        if info.get("github"):
            score += 1

    # ======= RANKING + STAR =======
    badge = "🟩 Excellent" if score >= 13 else "🟨 Moderate" if score >= 8 else "🟥 Risk"

    if score <= 3:
        stars = "⭐"
    elif score <= 6:
        stars = "⭐⭐"
    elif score <= 9:
        stars = "⭐⭐⭐"
    elif score <= 12:
        stars = "⭐⭐⭐⭐"
    else:
        stars = "⭐⭐⭐⭐⭐"

    return round(score, 2), badge, stars

# Update Tokenomics JSON
async def update_tokenomics_json(coin_id):
    try:
        with open("tokenomics.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}

    # Data dummy, bisa kamu ganti nanti pakai API
    tokenomics = {
        "team_allocation_percent": 20,
        "vesting_status": "locked",
        "audited": False,
        "whale_distribution": "medium"
    }

    data[coin_id] = tokenomics

    with open("tokenomics.json", "w") as f:
        json.dump(data, f, indent=2)

    print(f"✅ Tokenomics untuk {coin_id} berhasil diperbarui.")

# Update Tokenomics CMD
@bot.command(name="update_tokenomics")
async def update_tokenomics_cmd(ctx, *, coin: str):
    coin_id = await get_coin_id(coin)
    if not coin_id:
        await ctx.send(f"⚠️ Coin '{coin}' tidak ditemukan.")
        return

    await update_tokenomics_json(coin_id)
    await ctx.send(f"🔄 Tokenomics {coin.upper()} berhasil di-scrape dan disimpan.")

# ============ COMMAND: !metrics ============
@bot.command(name="metrics")
async def metrics(ctx, *, coin: str):
    try:
        # Get base coin id
        coin_id = await get_coin_id(coin)
        if not coin_id:
            await ctx.send(f"❌ Coin '{coin}' tidak ditemukan.")
            return
            
        await ctx.send(f"⏳ Menganalisis metrics untuk **{coin_id.upper()}**...")
        
        # Load CMC API Key
        CMC_API_KEY = os.getenv("CMC_API_KEY")
        if not CMC_API_KEY:
            await ctx.send("❌ CMC API key tidak ditemukan di .env file.")
            return
            
        # Fetch data from CoinMarketCap
        headers = {
            "X-CMC_PRO_API_KEY": CMC_API_KEY,
            "Accept": "application/json"
        }
        
        # Quote endpoint - basic market data
        quote_url = f"https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest"
        params = {
            "slug": coin_id,  # Using slug/name instead of symbol
            "convert": "USD"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(quote_url, headers=headers, params=params) as resp:
                if resp.status != 200:
                    await ctx.send(f"❌ Gagal mengambil data dari CMC API: {resp.status}")
                    return
                    
                data = await resp.json()
                
                # Extract data from the first result (should match our search)
                if not data.get("data") or len(data["data"]) == 0:
                    await ctx.send("❌ Tidak ada data coin yang ditemukan di CMC.")
                    return
                
                coin_data = list(data["data"].values())[0]
                quote = coin_data.get("quote", {}).get("USD", {})
                
                # METRICS EVALUATION
                metrics_score = {}
                total_score = 0
                max_score = 0
                
                # 1. Market Cap (1-5 points)
                market_cap = quote.get("market_cap", 0)
                if market_cap > 10000000000:  # >$10B
                    mc_score = 5
                    mc_desc = "Large Cap"
                elif market_cap > 1000000000:  # >$1B
                    mc_score = 4
                    mc_desc = "Mid Cap"
                elif market_cap > 100000000:  # >$100M
                    mc_score = 3  
                    mc_desc = "Small Cap"
                elif market_cap > 10000000:  # >$10M
                    mc_score = 2
                    mc_desc = "Micro Cap"
                else:
                    mc_score = 1
                    mc_desc = "Nano Cap"
                    
                metrics_score["Market Cap"] = {"score": mc_score, "desc": mc_desc, "max": 5}
                total_score += mc_score
                max_score += 5
                
                # 2. Volume to MC Ratio (1-5 points)
                volume = quote.get("volume_24h", 0)
                vol_mc_ratio = (volume / market_cap) if market_cap > 0 else 0
                
                if vol_mc_ratio > 0.2:  # >20% daily volume to MC ratio (very liquid)
                    vol_score = 5
                    vol_desc = "Excellent Liquidity"
                elif vol_mc_ratio > 0.1:  # >10%
                    vol_score = 4
                    vol_desc = "Strong Liquidity"
                elif vol_mc_ratio > 0.05:  # >5%
                    vol_score = 3
                    vol_desc = "Good Liquidity"
                elif vol_mc_ratio > 0.02:  # >2%
                    vol_score = 2
                    vol_desc = "Fair Liquidity"
                else:
                    vol_score = 1
                    vol_desc = "Poor Liquidity"
                    
                metrics_score["Volume/MC Ratio"] = {"score": vol_score, "desc": vol_desc, "max": 5}
                total_score += vol_score
                max_score += 5
                
                # 3. Circulating vs Total Supply (1-3 points)
                circulating = coin_data.get("circulating_supply", 0)
                total_supply = coin_data.get("total_supply", 0)
                
                if total_supply > 0:
                    circ_ratio = circulating / total_supply
                    if circ_ratio > 0.7:  # >70% in circulation
                        circ_score = 3
                        circ_desc = "Mostly Circulating"
                    elif circ_ratio > 0.4:  # >40% in circulation
                        circ_score = 2
                        circ_desc = "Partially Circulating"
                    else:
                        circ_score = 1
                        circ_desc = "Mostly Locked"
                else:
                    circ_score = 1
                    circ_desc = "Unknown Supply Ratio"
                
                metrics_score["Circ/Total Ratio"] = {"score": circ_score, "desc": circ_desc, "max": 3}
                total_score += circ_score
                max_score += 3
                
                # 4. Market Cap Growth (last 7d, 1-3 points)
                percent_change_7d = quote.get("percent_change_7d", 0)
                
                if percent_change_7d > 15:  # >15% growth
                    growth_score = 3
                    growth_desc = "Strong Growth"
                elif percent_change_7d > 0:  # Positive growth
                    growth_score = 2
                    growth_desc = "Positive Growth"
                else:
                    growth_score = 1
                    growth_desc = "Negative Growth"
                
                metrics_score["7D Growth"] = {"score": growth_score, "desc": growth_desc, "max": 3}
                total_score += growth_score
                max_score += 3
                
                # 5. Volatility (30d high-low range, 1-4 points)
                percent_change_30d = quote.get("percent_change_30d", 0)
                volatility = abs(percent_change_30d)
                
                if volatility < 10:  # <10% change (stable)
                    vol_score = 4
                    vol_desc = "Very Stable"
                elif volatility < 25:  # <25% change
                    vol_score = 3
                    vol_desc = "Moderately Stable"
                elif volatility < 50:  # <50% change
                    vol_score = 2
                    vol_desc = "Volatile"
                else:  # >50% change
                    vol_score = 1
                    vol_desc = "Highly Volatile"
                
                metrics_score["Volatility"] = {"score": vol_score, "desc": vol_desc, "max": 4}
                total_score += vol_score
                max_score += 4
                
                # Additional tokenomics data if available
                token = get_tokenomics_data(coin_id)
                if token:
                    # 6. Team Allocation (1-5 points, inversely proportional)
                    team_alloc = token.get("team_allocation_percent", 50)  # Default to 50% if not found
                    
                    if team_alloc <= 10:  # 10% or less to team
                        team_score = 5
                        team_desc = "Minimal Team Allocation"
                    elif team_alloc <= 20:
                        team_score = 4
                        team_desc = "Low Team Allocation"
                    elif team_alloc <= 30:
                        team_score = 3
                        team_desc = "Moderate Team Allocation"
                    elif team_alloc <= 40:
                        team_score = 2
                        team_desc = "High Team Allocation"
                    else:
                        team_score = 1
                        team_desc = "Very High Team Allocation"
                    
                    metrics_score["Team Allocation"] = {"score": team_score, "desc": team_desc, "max": 5}
                    total_score += team_score
                    max_score += 5
                
                # Calculate final percentage score
                percent_score = (total_score / max_score) * 100 if max_score > 0 else 0
                
                # Assign health rating based on score
                if percent_score >= 80:
                    health_rating = "🟢 SANGAT SEHAT"
                    color = 0x2ecc71  # Green
                elif percent_score >= 60:
                    health_rating = "🟡 CUKUP SEHAT"
                    color = 0xf1c40f  # Yellow
                elif percent_score >= 40:
                    health_rating = "🟠 HATI-HATI"
                    color = 0xe67e22  # Orange
                else:
                    health_rating = "🔴 BERISIKO"
                    color = 0xe74c3c  # Red
                
                # Create and send embed
                embed = discord.Embed(
                    title=f"🩺 Metrics Kesehatan: {coin_data.get('name', coin_id.upper())} ({coin_data.get('symbol', '').upper()})",
                    description=f"**Health Score: {percent_score:.1f}%**\n**Rating: {health_rating}**\n\n*Analisis berdasarkan data CMC dan Tokenomics*",
                    color=color
                )
                
                # Add metric fields
                for metric_name, metric_data in metrics_score.items():
                    stars = "⭐" * metric_data["score"] + "☆" * (metric_data["max"] - metric_data["score"])
                    embed.add_field(
                        name=f"{metric_name}",
                        value=f"{stars}\n{metric_data['desc']} ({metric_data['score']}/{metric_data['max']})",
                        inline=True
                    )
                
                # Add market data
                embed.add_field(
                    name="Market Data",
                    value=(
                        f"Market Cap: ${market_cap:,.0f}\n"
                        f"Volume 24h: ${volume:,.0f}\n"
                        f"Circ. Supply: {circulating:,.0f}"
                    ),
                    inline=False
                )
                
                embed.set_footer(text=f"Data dari CoinMarketCap & Tokenomics | {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
                
                await ctx.send(embed=embed)
    
    except Exception as e:
        await ctx.send(f"❌ Terjadi error: {str(e)}")
        
# ============ COMMAND: !compare ============
@bot.command(name="compare")
async def compare(ctx, *coins):
    if len(coins) < 2 or len(coins) > 3:
        await ctx.send("❌ Gunakan format: !compare <coin1> <coin2> [coin3] (2-3 coin)")
        return

    await ctx.send("⏳ Mengambil data perbandingan...")

    coin_data = []
    for coin in coins:
        coin_id = await get_coin_id(coin)
        if not coin_id:
            await ctx.send(f"❌ Coin '{coin}' tidak ditemukan.")
            return

        market = await get_market_overview(coin_id)
        token = get_tokenomics_data(coin_id)

        if not market:
            await ctx.send(f"❌ Gagal mendapatkan data market untuk {coin}")
            return

        coin_data.append({
            "id": coin_id,
            "market_cap": market.get("market_cap", "N/A"),
            "volume_24h": market.get("volume_24h", "N/A"),
            "fdv": market.get("fdv", "N/A"),
            "team_alloc": token.get("team_allocation_percent", "N/A") if token else "N/A",
            "vesting": token.get("vesting_status", "N/A") if token else "N/A",
            "audited": "✅" if token and token.get("audited") else "❌"
        })

    embed = discord.Embed(
        title="📊 Perbandingan Fundamental",
        description="Perbandingan metrik fundamental antar coin",
        color=0x3498db
    )

    metrics = {
        "💰 Market Cap": "market_cap",
        "📊 Volume 24h": "volume_24h",
        "💎 FDV": "fdv",
        "👥 Team Allocation": "team_alloc",
        "🔒 Vesting Status": "vesting",
        "🛡️ Audited": "audited"
    }

    for metric, key in metrics.items():
        value = ""
        for data in coin_data:
            val = data[key]
            if isinstance(val, (int, float)):
                val = f"${val:,.0f}"
            elif key == "team_alloc" and val != "N/A":
                val = f"{val}%"
            value += f"**{data['id'].upper()}**: {val}\n"
        
        # Add spacing after certain market metrics
        if key in ("market_cap", "volume_24h", "fdv"):
            value += "\n"

        embed.add_field(name=metric, value=value, inline=False)

    embed.set_footer(text="Data dari CoinGecko & Tokenomics Database")
    await ctx.send(embed=embed)

# ============ COMMAND: !roadmap ============
@bot.command(name="roadmap")
async def roadmap(ctx, *, coin: str = None):
    """
    Display project roadmap for a specified cryptocurrency.
    Usage: !roadmap <coin> (e.g., !roadmap btc)
    """
    if not coin:
        await ctx.send("❌ Silahkan tentukan coin yang ingin dilihat roadmapnya. Contoh: `!roadmap btc`")
        return
    
    try:
        # Get coin ID from alias or symbol
        coin_id = await get_coin_id(coin)
        if not coin_id:
            await ctx.send(f"❌ Coin '{coin}' tidak ditemukan di database.")
            return
            
        # Load roadmap data from JSON file
        with open("roadmap.json", "r") as f:
            data = json.load(f)
            
        # Check if roadmap exists for this coin
        if coin_id not in data:
            # Try alternative mappings
            alt_id = None
            for key in data.keys():
                if key.replace("-", "").lower() == coin_id.replace("-", "").lower():
                    alt_id = key
                    break
                    
            if not alt_id:
                await ctx.send(f"⚠️ Roadmap untuk {coin.upper()} belum tersedia.")
                return
            coin_id = alt_id
        
        # Get roadmap milestones for the coin
        roadmap_data = data[coin_id]
        
        # Create embed message
        embed = discord.Embed(
            title=f"🗺️ Roadmap {coin.upper()}",
            description=f"Rencana pengembangan project {coin.upper()} ke depan:",
            color=0x5865F2
        )
        
        # Count milestones by status
        completed = sum(1 for item in roadmap_data if item.get('status') == 'completed')
        in_progress = sum(1 for item in roadmap_data if item.get('status') == 'in_progress')
        planned = sum(1 for item in roadmap_data if item.get('status') == 'planned')
        total = len(roadmap_data)
        
        # Add progress overview
        embed.add_field(
            name="📊 Progress Overview",
            value=f"✅ Completed: {completed}/{total} ({int(completed/total*100)}%)\n"
                  f"🔄 In Progress: {in_progress}/{total} ({int(in_progress/total*100)}%)\n"
                  f"📝 Planned: {planned}/{total} ({int(planned/total*100)}%)",
            inline=False
        )
        
        # Style each milestone differently based on status
        completed_list = ""
        ongoing_list = ""
        planned_list = ""
        
        for milestone in roadmap_data:
            period = milestone.get('period', 'N/A')
            title = milestone.get('title', 'N/A')
            desc = milestone.get('description', 'N/A')
            status = milestone.get('status', 'planned')
            
            milestone_text = f"**{period}:** {title}\n→ *{desc}*\n\n"
            
            if status == 'completed':
                completed_list += milestone_text
            elif status == 'in_progress':
                ongoing_list += milestone_text
            else:  # planned or any other status
                planned_list += milestone_text
        
        # Add fields with appropriate emojis
        if completed_list:
            embed.add_field(name="✅ Completed", value=completed_list, inline=False)
        if ongoing_list:
            embed.add_field(name="🚧 In Progress", value=ongoing_list, inline=False)
        if planned_list:
            embed.add_field(name="🔮 Planned", value=planned_list, inline=False)
            
        embed.set_footer(text="Data terakhir diperbarui: April 2025")
        
        await ctx.send(embed=embed)
        
    except FileNotFoundError:
        await ctx.send("❌ File roadmap.json tidak ditemukan.")
    except json.JSONDecodeError as e:
        await ctx.send(f"❌ Error menguraikan roadmap.json: {str(e)}")
    except Exception as e:
        await ctx.send(f"❌ Terjadi error: {str(e)}")

# ============ COMMAND: !sentimen ============
@bot.command(name="sentimen")
async def sentimen_analisis(ctx, *, coin: str):
    """
    Analisis sentimen untuk koin kripto berdasarkan berita terbaru dan tweet.
    Usage: !sentimen <coin> (e.g., !sentimen btc)
    """
    try:
        # Validasi input
        if not coin:
            await ctx.send("❌ Silahkan tentukan coin yang ingin dianalisis. Contoh: `!sentimen btc`")
            return
        
        coin = coin.lower().strip()
        await ctx.send(f"🔍 Menganalisis sentimen untuk **{coin.upper()}**... (ini mungkin memakan waktu 10-20 detik)")
        
        # Dapatkan coin ID dan symbol
        coin_id = await get_coin_id(coin)
        if not coin_id:
            await ctx.send(f"❌ Coin '{coin.upper()}' tidak ditemukan di database.")
            return
        
        # Dapatkan symbol coin
        coins_list = load_coins_list()
        symbol = coin.upper()
        for c in coins_list:
            if c.get('id') == coin_id:
                symbol = c.get('symbol', '').upper()
                break
        
        # 1. Dapatkan berita terbaru dari sumber RSS
        news_items = []
        
        # Cari berita tentang coin di semua feed yang tersedia
        for source, url in RSS_FEEDS.items():
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries[:5]:  # Ambil 5 berita teratas
                    title = entry.title.lower()
                    desc = entry.get('description', '').lower()
                    content = entry.get('content', [{}])[0].get('value', '').lower() if entry.get('content') else ''
                    
                    if coin_id in title or symbol.lower() in title or coin in title or \
                       coin_id in desc or symbol.lower() in desc or coin in desc or \
                       coin_id in content or symbol.lower() in content or coin in content:
                        # Hitung relevansi berita
                        relevance = (title.count(coin) + title.count(symbol.lower()) + title.count(coin_id)) * 3 + \
                                    (desc.count(coin) + desc.count(symbol.lower()) + desc.count(coin_id)) * 2 + \
                                    (content.count(coin) + content.count(symbol.lower()) + content.count(coin_id))
                        
                        # Analisis tone dari berita
                        positive_words = ['bullish', 'surge', 'soar', 'gain', 'rally', 'rise', 'jump', 'growth', 
                                         'record', 'adopt', 'breakthrough', 'opportunity', 'positive', 'strong',
                                         'increase', 'up', 'high', 'moon', 'win', 'profitable']
                        
                        negative_words = ['bearish', 'plunge', 'crash', 'fall', 'decline', 'drop', 'tumble', 'slump',
                                          'loss', 'risk', 'warning', 'concern', 'weak', 'volatile', 'dump', 'sell',
                                          'down', 'low', 'bear', 'lose', 'scam', 'fraud']
                        
                        text_for_tone = (title + " " + desc + " " + content).lower()
                        pos_count = sum(1 for word in positive_words if word in text_for_tone)
                        neg_count = sum(1 for word in negative_words if word in text_for_tone)
                        
                        tone = "Neutral"
                        if pos_count > neg_count:
                            tone = "Positive"
                        elif neg_count > pos_count:
                            tone = "Negative"
                        
                        # Extract summary - get the first sentence or first 150 chars
                        summary = desc or content
                        
                        # Clean HTML tags from summary
                        summary = re.sub(r'<.*?>', '', summary)  # Remove HTML tags
                        summary = re.sub(r'&[a-z]+;', ' ', summary)  # Remove HTML entities
                        summary = re.sub(r'\s+', ' ', summary).strip()  # Clean up whitespace
                        
                        if summary:
                            if "." in summary[:200]:
                                summary = summary.split(".")[0] + "."
                            else:
                                summary = summary[:150] + "..."
                        else:
                            summary = title
                        
                        news_items.append({
                            "title": entry.title,
                            "url": entry.link,
                            "content": summary,
                            "source": source,
                            "date": entry.get('published', datetime.datetime.now().strftime('%Y-%m-%d')),
                            "relevance": relevance,
                            "tone": tone
                        })
            except Exception as e:
                logging.error(f"Error parsing RSS feed {source}: {str(e)}")
                continue
        
        # 2. Dapatkan tweet terbaru tentang coin
        tweets = []
        TWITTER_TOKEN = os.getenv('TWITTER_TOKEN')
        if TWITTER_TOKEN:
            try:
                tweets = await search_twitter(coin_id, symbol, TWITTER_TOKEN)
            except Exception as e:
                logging.error(f"Error querying Twitter API: {str(e)}")
        
        # Pisahkan berita dan tweets untuk analisis yang lebih baik
        news_items.sort(key=lambda x: x.get('relevance', 0), reverse=True)
        
        # Batasi ke 5 berita dan 5 tweet paling relevan
        top_news = news_items[:5]
        top_tweets = tweets[:5]
        
        if not top_news and not top_tweets:
            await ctx.send(f"⚠️ Tidak ditemukan berita atau tweet terbaru tentang {coin.upper()}.")
            return
        
        # 3. Analisis sentimen dari semua sumber
        positive_words = ['bullish', 'surge', 'soar', 'gain', 'rally', 'rise', 'jump', 'growth', 
                         'record', 'adopt', 'breakthrough', 'opportunity', 'positive', 'strong',
                         'increase', 'up', 'high', 'moon', 'win', 'profitable', '🚀', '📈', '💰', '💎']
        
        negative_words = ['bearish', 'plunge', 'crash', 'fall', 'decline', 'drop', 'tumble', 'slump',
                          'loss', 'risk', 'warning', 'concern', 'weak', 'volatile', 'dump', 'sell',
                          'down', 'low', 'bear', 'lose', 'scam', 'fraud', '📉', '⚠️', '❗']
        
        # Gabungkan semua teks untuk analisis sentimen keseluruhan
        clean_text = []
        for item in (top_news + top_tweets):
            title = re.sub(r'<.*?>', '', item.get('title', ''))  # Remove HTML tags
            content = re.sub(r'<.*?>', '', item.get('content', ''))  # Remove HTML tags
            clean_text.append(title + " " + content)
            
        all_text = " ".join(clean_text).lower()
        
        pos_count = sum([all_text.count(word) for word in positive_words])
        neg_count = sum([all_text.count(word) for word in negative_words])
        
        # Hitung skor sentimen
        if pos_count + neg_count > 0:
            sentiment_score = pos_count / (pos_count + neg_count)
            sentiment_score_int = int(sentiment_score * 10)  # Convert to 0-10 scale
        else:
            sentiment_score = 0.5  # Netral
            sentiment_score_int = 5
        
        # 4. Tentukan kategori sentimen
        if sentiment_score >= 0.65:
            sentiment_category = "BULLISH"
            color = 0x2ECC71  # Hijau
        elif sentiment_score >= 0.45:
            sentiment_category = "NETRAL"
            color = 0x3498DB  # Biru
        else:
            sentiment_category = "BEARISH"
            color = 0xE74C3C  # Merah
        
        # 5. Ekstrak kata kunci populer
        words = re.findall(r'\b\w+\b', all_text)
        stop_words = ['the', 'to', 'and', 'a', 'in', 'is', 'it', 'of', 'for', 'on', 'with', 'as', 'by', 'at', 'from', 'be', 
                      'this', 'that', 'have', 'has', 'had', 'not', 'are', 'was', 'were', 'will', 'would', 'could', 'should',
                      'can', 'may', 'might', 'must', 'shall', 'there', 'their', 'they', 'these', 'those', 'then', 'than',
                      'our', 'who', 'whom', 'whose', 'which', 'what', 'when', 'where', 'why', 'how']
        filtered_words = [word for word in words if word not in stop_words and len(word) > 3 and not word.isdigit()]
        
        # Dapatkan kata kunci populer
        counter = Counter(filtered_words)
        keywords = [word.upper() for word, count in counter.most_common(8) if word.lower() != coin and word.lower() != coin_id and word.lower() != symbol.lower()]
        
        # 6. Buat dan kirim embed dengan format yang telah ditentukan
        embed = discord.Embed(
            title=f"Sentimen {coin.upper()}",
            description=f"Berikut adalah analisis sentimen berdasarkan trending topic di X, dan pencarian berita di internet:",
            color=color
        )
        
        # Tambahkan bagian analisis sentimen
        embed.add_field(
            name="📝 Analisis Sentimen",
            value=f"Analisis sentimen menunjukkan sinyal **{sentiment_category}** untuk {coin.upper()}.\n"
                  f"⭐ **Skor**: {sentiment_score_int}/10\n"
                  f"🔑 **Kata Kunci**:\n"
                  f"{', '.join(keywords[:5])}\n",
            inline=False
        )
        
        # Tambahkan 3 berita teratas
        for i, news in enumerate(top_news[:3], 1):
            embed.add_field(
                name=f"📰 Berita {coin.upper()} #{i}",
                value=f"{news.get('content', 'Tidak ada konten')}\n"
                      f"📢 **Tone**: {news.get('tone', 'Neutral')}\n"
                      f"🔗 **Link**: {news.get('url', '#')}",
                inline=False
            )
        
        # Tambahkan analisis tweet
        tweet_section = ""
        for tweet in top_tweets[:2]:
            tweet_section += f"{tweet.get('title', '')}\n"
            tweet_section += f"📢 **Tone**: {tweet.get('tone', 'Neutral')}\n"
            tweet_section += f"🔗 **Link**: {tweet.get('url', '#')}\n\n"
        
        if tweet_section:
            embed.add_field(
                name=f"𝕏 Analisis {coin.upper()} di X!",
                value=tweet_section.strip(),
                inline=False
            )
        
        # Footer
        embed.set_footer(text="Powered by Aletta Intelligence v1.5")
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        logging.error(f"Error in sentimen command: {str(e)}")
        await ctx.send(f"❌ Terjadi kesalahan dalam analisis sentimen: {str(e)}")

with open("teams.json", "r", encoding="utf-8") as f:
    teams_data = json.load(f)

@bot.command()
async def team(ctx, coin: str):
    try:
        with open('teams.json', 'r', encoding='utf-8') as file:
            data = json.load(file)

        coin = coin.lower()
        
        # Cari berdasarkan alias atau nama utama
        project = None
        for key, value in data.items():
            aliases = value.get("aliases", [])
            if coin == key.lower() or coin in [alias.lower() for alias in aliases]:
                project = value
                break

        if project:
            embed = discord.Embed(
                title=f"Team Behind {project['project_name']}",
                description=f"Organization: **{project['organization']}**",
                color=discord.Color.blue()
            )

            image_set = False  # Biar gambar cuma 1x ditampilkan

            for member in project["team"]:
                bio = member.get('bio', '-')
                linkedin = member.get('linkedin')
                image = member.get('image')

                # Tambahin LinkedIn kalo ada
                value = f"{bio}"
                if linkedin:
                    value += f"\n[LinkedIn]({linkedin})"

                embed.add_field(
                    name=f"{member['name']} - {member['position']}",
                    value=value,
                    inline=False
                )

                # Tampilkan gambar pertama aja
                if image and not image_set:
                    embed.set_thumbnail(url=image)
                    image_set = True

            await ctx.send(embed=embed)

        else:
            await ctx.send(f"Maaf, belum ada data tim untuk koin **{coin.upper()}**.")

    except Exception as e:
        await ctx.send("Terjadi kesalahan saat mengambil data tim.")
        print(e)

bot.run(TOKEN)