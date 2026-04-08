"""
scraper.py — Auto-pulls NBA, MLB, GOLF players from realapp.tools API into Firebase.
Run with: python3 scraper.py
"""

import firebase_admin
from firebase_admin import credentials, firestore
import requests
import os
import json
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

# --- Firebase Setup ---
try:
    firebase_creds = os.environ.get("FIREBASE_CREDENTIALS")
    if firebase_creds:
        cred = credentials.Certificate(json.loads(firebase_creds))
    else:
        cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("Firebase connected.")
except FileNotFoundError:
    print("Error: serviceAccountKey.json not found.")
    exit()

# --- realapp.tools API config ---
SUPABASE_URL = "https://mfsyhtuqybbxprgwwykd.supabase.co"
TOKEN = "sb_publishable_Al7QsFGnNTlknoI8KVxjag_JUwrytZy"
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

ALLOWED_SPORTS = {"nba", "mlb", "golf"}

RAX_EARNINGS = {
    "General": 200, "Common": 1000, "Uncommon": 1500,
    "Rare": 2000, "Epic": 5000, "Legendary": 12500,
    "Mystic": 37500, "Iconic": 999999
}

GOLF_PLAYERS = [
    "Scottie Scheffler","Rory McIlroy","Jon Rahm","Xander Schauffele","Collin Morikawa",
    "Viktor Hovland","Patrick Cantlay","Tony Finau","Justin Thomas","Jordan Spieth",
    "Dustin Johnson","Brooks Koepka","Bryson DeChambeau","Tommy Fleetwood","Shane Lowry",
    "Matt Fitzpatrick","Hideki Matsuyama","Max Homa","Keegan Bradley","Wyndham Clark",
    "Sahith Theegala","Ludvig Aberg","Akshay Bhatia","Si Woo Kim","Jake Knapp",
    "Sungjae Im","Tom Kim","Chris Kirk","Adam Scott","Jason Day","Rickie Fowler",
    "Billy Horschel","Sepp Straka","Corey Conners","Kurt Kitayama","Harris English",
    "Denny McCarthy","Taylor Moore","Eric Cole","Davis Thompson","Nick Taylor",
    "Mackenzie Hughes","Adam Hadwin","Aaron Rai","Thriston Lawrence","Dean Burmester",
    "Rasmus Hojgaard","Nicolai Hojgaard","Adrian Meronk","Tyrrell Hatton","Robert MacIntyre",
    "Min Woo Lee","Cam Davis","Lucas Herbert","Cameron Smith","Talor Gooch","Patrick Reed",
    "Bubba Watson","Webb Simpson","Zach Johnson","Kevin Kisner","Brian Harman",
    "Luke List","Brendan Steele","Joel Dahmen","Beau Hossler","Nate Lashley",
    "Chez Reavie","Charley Hoffman","Kevin Streelman","Emiliano Grillo","Joaquin Niemann",
    "Mito Pereira","Christiaan Bezuidenhout","Rafa Cabrera Bello","Alex Noren",
    "Henrik Stenson","Ian Poulter","Lee Westwood","Paul Casey","Sergio Garcia",
    "Padraig Harrington","Graeme McDowell","Martin Kaymer","Bernd Wiesberger",
    "Matthias Schwab","Jorge Campillo","Pablo Larrazabal","Adri Arnaus",
    "Pontus Nyholm","Max Greyserman","Chris Gotterup","Sahith Theegala",
    "Austin Eckroat","Peter Malnati","Callum Tarren","Ben Griffin","Andrew Novak",
    "Hayden Buckley","MJ Daffue","Greyson Sigg","Ryan Gerard","Carl Yuan",
    "Pierceson Coody","Zac Blair","Martin Trainer","Hank Lebioda","Will Gordon",
    "Trevor Cone","Vince Whaley","Kramer Hickok","Tyler Duncan","Scott Gutschewski",
    "Xander Schauffele","Rory McIlroy","Scottie Scheffler","Jon Rahm","Viktor Hovland",
    "Tommy Fleetwood","Shane Lowry","Tyrrell Hatton","Robert MacIntyre","Matt Wallace",
    "Thorbjorn Olesen","Marcus Armitage","Richie Ramsay","Grant Forrest","Ewen Ferguson",
    "Connor Syme","David Law","Calum Hill","Liam Johnston","Cormac Sharvin",
]

NBA_PLAYERS = [
    "LeBron James","Stephen Curry","Kevin Durant","Giannis Antetokounmpo","Nikola Jokic",
    "Luka Doncic","Joel Embiid","Jayson Tatum","Devin Booker","Anthony Davis",
    "Kawhi Leonard","Paul George","Damian Lillard","Kyrie Irving","James Harden",
    "Anthony Edwards","Ja Morant","Zion Williamson","Trae Young","Donovan Mitchell",
    "Bam Adebayo","Rudy Gobert","Karl-Anthony Towns","Domantas Sabonis","De'Aaron Fox",
    "Tyrese Haliburton","Shai Gilgeous-Alexander","Cade Cunningham","Evan Mobley","Scottie Barnes",
    "Franz Wagner","Paolo Banchero","Jalen Brunson","Tyrese Maxey","Mikal Bridges",
    "Jaylen Brown","Khris Middleton","Jrue Holiday","Brook Lopez","Bobby Portis",
    "Draymond Green","Klay Thompson","Andrew Wiggins","Jordan Poole","Chris Paul",
    "Russell Westbrook","John Wall","Bradley Beal","Kristaps Porzingis","Julius Randle",
    "RJ Barrett","Immanuel Quickley","OG Anunoby","Pascal Siakam","Fred VanVleet",
    "Scottie Barnes","Gary Trent Jr","Precious Achiuwa","Jarrett Allen","Darius Garland",
    "Caris LeVert","Isaac Okoro","Dean Wade","Lamar Stevens","Robin Lopez",
    "LaMelo Ball","Miles Bridges","Terry Rozier","Gordon Hayward","Mason Plumlee",
    "Jalen McDaniels","Theo Maledon","James Bouknight","Kai Jones","JT Thor",
    "Desmond Bane","Jaren Jackson Jr","Ja Morant","Steven Adams","Brandon Clarke",
    "De'Anthony Melton","Ziaire Williams","Santi Aldama","John Konchar","Xavier Tillman",
    "Deni Avdija","Kyle Kuzma","Bradley Beal","Monte Morris","Delon Wright",
    "Corey Kispert","Isaiah Todd","Jordan Schakel","Devon Dotson","Cassius Winston",
    "Austin Reaves","Lonnie Walker","Wenyen Gabriel","Damian Jones","Kendrick Nunn",
    "Victor Wembanyama","Cooper Flagg","Amen Thompson","Ausar Thompson","Chet Holmgren",
    "Jalen Williams","Josh Giddey","Luguentz Dort","Isaiah Joe","Kenrich Williams",
    "Jamal Murray","Michael Porter Jr","Aaron Gordon","Bones Hyland","Vlatko Cancar",
    "Jaylen Nowell","Naz Reid","Kyle Anderson","Taurean Prince","Jordan McLaughlin",
    "Jalen Johnson","Trae Young","Dejounte Murray","Clint Capela","John Collins",
    "Bogdan Bogdanovic","Kevin Huerter","Onyeka Okongwu","Danilo Gallinari","Lou Williams",
]

MLB_PLAYERS = [
    "Shohei Ohtani","Aaron Judge","Mookie Betts","Freddie Freeman","Trea Turner",
    "Fernando Tatis Jr","Juan Soto","Ronald Acuna Jr","Bryce Harper","Mike Trout",
    "Yordan Alvarez","Jose Altuve","Alex Bregman","Kyle Tucker","Framber Valdez",
    "Gerrit Cole","Jacob deGrom","Max Scherzer","Justin Verlander","Zack Wheeler",
    "Brandon Woodruff","Corbin Burnes","Freddy Peralta","Josh Hader","Devin Williams",
    "Paul Goldschmidt","Nolan Arenado","Tommy Edman","Miles Mikolas","Adam Wainwright",
    "Yadier Molina","Harrison Bader","Dylan Carlson","Lars Nootbaar","Brendan Donovan",
    "Pete Alonso","Francisco Lindor","Jeff McNeil","Starling Marte","Max Scherzer",
    "Taijuan Walker","Chris Bassitt","Edwin Diaz","Trevor May","Seth Lugo",
    "Julio Rodriguez","Ty France","Eugenio Suarez","Jesse Winker","Marco Gonzales",
    "Logan Gilbert","Robbie Ray","George Kirby","Cal Raleigh","Jarred Kelenic",
    "Vladimir Guerrero Jr","Bo Bichette","George Springer","Kevin Gausman","Alek Manoah",
    "Jose Berrios","Lourdes Gurriel Jr","Teoscar Hernandez","Matt Chapman","Alejandro Kirk",
    "Garrett Crochet","Dylan Cease","Lucas Giolito","Lance Lynn","Liam Hendriks",
    "Tim Anderson","Yoan Moncada","Jose Abreu","Eloy Jimenez","Luis Robert",
    "Yoshinobu Yamamoto","Gavin Stone","Bobby Miller","James Outman","Miguel Vargas",
    "Walker Buehler","Clayton Kershaw","Tony Gonsolin","Julio Urias","Max Muncy",
    "Will Smith","Austin Barnes","Cody Bellinger","Chris Taylor","Hanser Alberto",
    "Paul Skenes","Ke'Bryan Hayes","Bryan Reynolds","Oneil Cruz","Manny Machado",
    "Xander Bogaerts","Jake Cronenworth","Ha-Seong Kim","Joe Musgrove","Yu Darvish",
    "Cristopher Sanchez","Aaron Nola","Ranger Suarez","Zack Wheeler","Nick Castellanos",
]


def call_api(action, payload={}):
    resp = requests.post(
        f"{SUPABASE_URL}/functions/v1/market-data",
        headers=HEADERS,
        json={"action": action, "payload": payload},
        timeout=15
    )
    resp.raise_for_status()
    return resp.json()


def send_email_alert(buy_signals):
    """Sends an email with the top buy signals."""
    gmail = os.environ.get("GMAIL_ADDRESS")
    password = os.environ.get("GMAIL_PASSWORD")
    if not gmail or not password:
        print("No email credentials set, skipping alert.")
        return
    if not buy_signals:
        return

    lines = [f"🔥 RaxCartel — {len(buy_signals)} BUY signals found\n"]
    for p in buy_signals:
        lines.append(
            f"• {p['name']} ({p['rarity']} {p['season']}) — {p['sport']}\n"
            f"  Price: {p['market_value']:,} RAX | R/R: {p['rr_ratio']:.1f} | Deal: {p['deal_score']}/95\n"
            f"  Breakeven: {p['days_to_breakeven']} days\n"
        )
    lines.append("\nView dashboard: https://raxcartel.onrender.com")

    msg = MIMEText("\n".join(lines))
    msg["Subject"] = f"🟢 RaxCartel: {len(buy_signals)} Buy Signals"
    msg["From"] = gmail
    msg["To"] = gmail

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gmail, password)
            server.send_message(msg)
        print(f"Email sent to {gmail} with {len(buy_signals)} buy signals.")
    except Exception as e:
        print(f"Email failed: {e}")



    resp = requests.post(
        f"{SUPABASE_URL}/functions/v1/market-data",
        headers=HEADERS,
        json={"action": action, "payload": payload},
        timeout=15
    )
    resp.raise_for_status()
    return resp.json()


def fetch_players(season=2026):
    print(f"Fetching players for season {season}...")
    data = call_api("get_homepage_cards", {"season": season, "filters": {}})
    cards = data.get("cards", [])
    print(f"  Got {len(cards)} cards from homepage.")
    return cards


def fetch_steals(season=2026):
    print(f"Fetching steals/undervalued for season {season}...")
    data = call_api("get_steals_cards", {"season": season})
    cards = data.get("cards", [])
    print(f"  Got {len(cards)} steal cards.")
    return cards


def fetch_players_by_name(player_list, sport_filter, season=2026):
    """Searches for players by name and fetches their cheapest live listing."""
    print(f"\nFetching {sport_filter.upper()} players ({len(player_list)} names)...")
    cards = []
    seen_ids = set()

    for name in player_list:
        try:
            data = call_api("get_player_suggestions", {"query": name.split()[0], "season": season})
            suggestions = [s for s in data.get("suggestions", []) if s.get("sport","").lower() == sport_filter.lower()]
            for player in suggestions:
                eid = player.get("entityId")
                if eid in seen_ids:
                    continue
                seen_ids.add(eid)
                sales = call_api("get_player_sales_by_entity", {"entityId": eid, "season": season})
                summary = sales.get("summary", {})
                p_info = summary.get("player", {})
                listings = summary.get("listings", [])
                live = [l for l in listings if not l.get("is_ended")]
                if not live:
                    continue
                cheapest = min(live, key=lambda x: x.get("bid", 999999))
                rarity_map = {3: "Rare", 4: "Epic", 5: "Legendary", 6: "Mystic", 7: "Iconic"}
                rarity = rarity_map.get(cheapest.get("rarity"), "Rare")
                price = cheapest.get("bid", 0)
                rr = p_info.get("avg_rax_per_rating", 0) or 0
                fair_value = round(rr * (cheapest.get("value") or 80)) if rr else 0

                cards.append({
                    "playerName": player.get("name", name),
                    "sport": sport_filter.lower(),
                    "season": season,
                    "entityId": eid,
                    "rarityLabel": rarity,
                    "listingPrice": price,
                    "currentRr": rr,
                    "avgRr": rr,
                    "fairValue": fair_value,
                    "trendingScore": 50,
                    "valuationStatus": "unknown",
                })
                print(f"  {player.get('name', name):<30} {rarity:<10} {price:>6,} RAX")
        except Exception:
            continue

    print(f"  Found {len(cards)} {sport_filter.upper()} players with live listings.")
    return cards


def save_players(cards):
    allowed = [c for c in cards if c.get("sport", "").lower() in ALLOWED_SPORTS]
    print(f"\nSaving {len(allowed)} NBA/MLB/GOLF players to Firebase...\n")

    saved = 0
    for c in allowed:
        name = c.get("playerName", "Unknown")
        sport = c.get("sport", "").upper()
        season = str(c.get("season", "2026"))
        rarity = c.get("rarityLabel", "Common")
        price = c.get("listingPrice") or 0
        rr = c.get("currentRr") or 0
        avg_rr = c.get("avgRr") or 0
        fair_value = c.get("fairValue") or 0
        deal_score = c.get("trendingScore") or 0
        valuation = c.get("valuationStatus", "")
        daily_rax = RAX_EARNINGS.get(rarity, 1000)
        breakeven = round(price / daily_rax, 1) if daily_rax and price else None
        profit_if_sold = fair_value - price if fair_value and price else None
        roi = round((profit_if_sold / price) * 100, 1) if profit_if_sold and price else None

        doc_id = f"{name} ({rarity} {season})"
        ref = db.collection("market_watch").document(doc_id)
        existing = ref.get()

        player_data = {
            "name": name,
            "sport": sport,
            "season": season,
            "rarity": rarity,
            "market_value": price,
            "fair_value": fair_value,
            "rr_ratio": rr,
            "avg_rr": avg_rr,
            "deal_score": deal_score,
            "valuation_status": valuation,
            "daily_rax_earn": daily_rax,
            "days_to_breakeven": breakeven,
            "profit_if_sold": profit_if_sold,
            "roi_pct": roi,
            "last_updated": datetime.now().isoformat()
        }

        if existing.exists:
            ref.update(player_data)
            status = "Updated"
        else:
            player_data.update({
                "buy_price": price,
                "sell_price": None,
                "profit_loss": None,
                "rating_progress": 0,
                "total_rax_invested": 0,
                "avg_points_last_5": 0.0,
                "games_this_week": 0,
                "schedule_strength": "Unknown",
                "upcoming_games": 0,
            })
            ref.set(player_data)
            status = "Added"

        tag = "🟢 BUY" if deal_score >= 60 else ("🟡 FAIR" if deal_score >= 40 else "🔴 SKIP")
        print(f"  {status:7} {doc_id:<45} {sport:<5} {rarity:<10} {price:>6,} RAX  {tag}")
        saved += 1

    print(f"\nDone. {saved} players saved.")


def main():
    print("\n=== RaxCartel Auto-Scraper ===")
    season = 2026

    all_cards = []
    homepage = fetch_players(season)
    steals = fetch_steals(season)
    golf = fetch_players_by_name(GOLF_PLAYERS, "golf", season)
    nba = fetch_players_by_name(NBA_PLAYERS, "nba", season)
    mlb = fetch_players_by_name(MLB_PLAYERS, "mlb", season)

    # Merge homepage + steals by listingId
    seen = set()
    for c in homepage + steals:
        lid = c.get("listingId")
        if lid not in seen:
            seen.add(lid)
            all_cards.append(c)

    # Add name-searched players, dedup by name+rarity+season
    existing_keys = {f"{c.get('playerName')}_{c.get('rarityLabel')}_{c.get('season')}" for c in all_cards}
    for c in golf + nba + mlb:
        key = f"{c.get('playerName')}_{c.get('rarityLabel')}_{c.get('season')}"
        if key not in existing_keys:
            existing_keys.add(key)
            all_cards.append(c)

    print(f"\nTotal unique cards: {len(all_cards)}")
    save_players(all_cards)

    # Email alert for buy signals
    buy_signals = [
        c for c in all_cards
        if c.get("sport", "").lower() in {"nba", "mlb", "golf"}
        and c.get("trendingScore", 0) >= 60
    ]
    formatted = []
    for c in buy_signals:
        rarity = c.get("rarityLabel", "Common")
        daily_rax = RAX_EARNINGS.get(rarity, 1000)
        price = c.get("listingPrice") or 0
        formatted.append({
            "name": c.get("playerName"),
            "sport": c.get("sport", "").upper(),
            "season": str(c.get("season", "2026")),
            "rarity": rarity,
            "market_value": price,
            "rr_ratio": c.get("currentRr") or 0,
            "deal_score": c.get("trendingScore") or 0,
            "days_to_breakeven": round(price / daily_rax, 1) if daily_rax and price else None
        })
    send_email_alert(formatted)


if __name__ == "__main__":
    main()
