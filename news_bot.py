import feedparser, requests, json, os, hashlib, re
from datetime import datetime, timezone, timedelta
from html import unescape
from io import BytesIO
from PIL import Image

SETTINGS_FILE = "settings.json"
POSTED_FILE = "posted_items.json"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID", "@ksbskehwb")

# ======== كلمات ممنوعة (محتوى إباحي + ايتشي + هنتاي) ========
EXCLUDE_WORDS = [
    "ecchi", "hentai", "adult", "xxx", "porn", "18+", "nsfw", "sex",
    "erotic", "lewd", "doujin", "jav", "ahegao", "lolicon", "shotacon",
    "onlyfans", "strip", "nude", "naked", "risque", "bikini",
    "إباحي", "سكس", "عراة", "عاري", "إغراء", "جنسي",
    "omegaverse", "beastmen", "beast man", "harem",
]

# ======== قائمة محظورة لأنميات/ألعاب ممنوعة ========
BLOCKED_TITLES = [
    "highschool dxd", "high school dxd", "to love-ru", "to love ru",
    "ishuzoku reviewers", "interspecies reviewers",
    "redo of healer", "redo healer",
    "shinmai maou no testament", "testament sister new devil",
    "shinmai maou", "how not to summon a demon lord",
    "why the hell are you here teacher",
    "valkyrie drive", "queen's blade", "senran kagura",
    "eromanga sensei", "domestic girlfriend", "domestic na kanojo",
    "kiss x sis", "kissxsiss", "kiss sis",
    "prison school", "shimoneta", "monster musume",
    "keijo", "high school of the dead",
    "freezing", "sekirei", "haganai",
    "rosario vampire", "rosario to vampire",
    "dragon maid", "kobayashi-san chi no maid dragon",
]

# ======== القائمة البيضاء لأنميات وألعاب كبرى ========
MAJOR_ANIME = [
    # شونين عالمي
    "one piece", "naruto", "boruto", "attack on titan", "shingeki no kyojin",
    "demon slayer", "kimetsu no yaiba", "jujutsu kaisen", "jujutsu kaisen",
    "dragon ball", "dragonball", "dbz", "dbs", "dragon ball super", "dragon ball z",
    "my hero academia", "boku no hero", "chainsaw man", "solo leveling",
    "death note", "fullmetal alchemist", "hunter x hunter", "hunter x hunter",
    "bleach", "spy x family", "spy family", "tokyo revengers",
    "vinland saga", "frieren", "sousou no frieren",
    "mob psycho", "mob psycho 100", "one punch man", "onepunch man",
    "sword art online", "sao", "re:zero", "re zero",
    "steins;gate", "steins gate", "code geass",
    "evangelion", "neon genesis evangelion", "ghost in the shell",
    "akira", "cyberpunk edgerunners", "edgerunners",
    "dandadan", "hell's paradise", "hells paradise", "jigokuraku",
    "kaiju no. 8", "kaiju number 8", "mashle",
    "wind breaker", "delicious in dungeon", "dungeon meshi",
    "konosuba", "overlord", "that time i got reincarnated as a slime",
    "tensura", "mushoku tensei", "jobless reincarnation",
    "classroom of the elite", "youkoso jitsuryoku",
    "oshi no ko", "kaguya-sama", "kaguya sama", "love is war",
    "sakamoto days", "dorohedoro", "to your eternity",
    "summertime rendering", "odd taxi", "ranking of kings",
    "heavenly delusion", "tengoku daimakyo",
    # مانجا وكلاسيكيات
    "made in abyss", "violet evergarden",
    "your lie in april", "shigatsu wa kimi no uso",
    "a silent voice", "koe no katachi",
    "your name", "kimi no na wa", "spirited away", "howl's moving castle",
    "princess mononoke", "totoro", "studio ghibli", "ghibli",
    "gintama", "jojo", "jojo's bizarre", "jojo bizarre",
    "fate", "fate/stay", "fate grand order", "fgo",
    # رياضة
    "haikyuu", "kuroko's basketball", "kuroko no basket",
    "slam dunk", "blue lock", "ao ashi",
    # أطفال وعائلة
    "pokemon", "pokémon", "digimon", "yu-gi-oh", "yugioh",
    "detective conan", "conan", "case closed",
    "doraemon", "shin-chan", "shinchan",
    "sailor moon", "cardcaptor sakura",
    # ويب تون وكورية
    "tower of god", "god of high school", "the god of high school",
    "noblesse", "lookism",
    # أفلام ومخرجين
    "makoto shinkai", "hayao miyazaki", "satoshi kon",
    "mamoru hosoda", "mappa", "ufotable", "kyoto animation", "toei",
    "crunchyroll", "netflix anime", "netflix",
    # مانجا مشهورة
    "berserk", "vagabond", "monster", "20th century boys", "pluto",
    "goodnight punpun", "oyasumi punpun",
    "kingdom", "tokyo ghoul",
    "hajime no ippo", "initial d",
    "great teacher onizuka", "gto",
    "rurouni kenshin", "yu yu hakusho",
    "fist of the north star", "hokuto no ken",
    "saint seiya", "ranma", "inuyasha",
    "trigun", "hellsing", "lupin iii",
    "assassination classroom", "ansatsu kyoushitsu",
    "food wars", "shokugeki no soma",
    "ace of diamond", "daiya no ace",
    "the promised neverland", "yakusoku no neverland",
    "dr. stone", "black clover",
    "fire force", "enen no shouboutai",
    "the quintessential quintuplets",
    "rent-a-girlfriend", "kanojo okarishimasu",
    "komi can't communicate", "komi-san",
    "fruits basket", "nana",
    "blade of the immortal", "lone wolf and cub",
    "the rose of versailles", "banana fish",
    "ouran high school host club",
    "mushishi", "natsume's book of friends",
    "silver spoon", "barakamon",
    "march comes in like a lion", "sangatsu no lion",
    "chihayafuru", "space brothers",
    "beck", "sakamichi no apollon",
    "anohana", "clannad", "angel beats",
    "higurashi", "umineko",
    "haruhi suzumiya", "lucky star", "k-on", "love live",
    "yuru camp", "laid-back camp",
    "non non biyori",
    "girls' last tour", "shoujo shuumatsu ryokou",
    "land of the lustrous", "houseki no kuni",
    "the ancient magus' bride",
    "witch hat atelier",
    "the girl from the other side",
    "assassination classroom", "dr. stone",
    "promised neverland",
    "slam dunk", "real", "vagabond",
    "planet", "planetes",
    # مانهوا وويبتون كورية
    "omniscient reader's viewpoint", "omniscient reader",
    "the beginning after the end",
    "the legend of the northern blade",
    "a returner's magic should be special",
    "second life ranker", "overgeared",
    "the max level hero has returned",
    "kill the hero", "trash of the count's family",
    "sss-class suicide hunter", "sss class suicide hunter",
    "the s-classes that i raised",
    "unordinary", "the gamer",
    "hardcore leveling warrior",
    "girls of the wild's", "the boxer",
    "study group", "weak hero",
    "viral hit", "how to fight",
    "true beauty",
    "sweet home", "shotgun boy",
    "bastard", "pigpen",
    "the horizon", "annarasumanara",
    "dice", "the god of high school",
    "tower of god", "noblesse", "lookism",
    # مانجا تتحول لأنمي (قريباً أو حديثاً)
    "witch hat atelier", "tongari boushi no atelier",
    "the summer hikaru died", "medalist",
    "the fable", "kagurabachi",
    "gachiakuta", "orb", "on the movements of the earth",
    "blue box", "ao no hako",
    "the elusive samurai", "nige jouzu no wakagimi",
    "mission yozakura family", "yozakura family",
    "days with my stepsister",
    "alya sometimes hides her feelings in russian",
    "makeine", "too many losing heroines",
    "the dangers in my heart", "boku no kokoro no yabai yatsu",
    "skip and loafer", "insomniacs after school",
    "my love story with yamada-kun at lv999",
    "ranger reject", "sentai daishikkaku",
    "undead unluck", "undead unluck",
    "chained soldier", "mato seihei no slave",
    "the 100 girlfriends", "100 girlfriends",
    "bucchigiri", "ishura",
    "synduality", "stardust telepath",
    "pseudo harem", "senpai is an otokonoko",
    "the café terrace and its goddesses",
    "when will ayumu make his move",
    "a wild last boss appeared",
    "the unwanted undead adventurer",
    "the witch and the beast",
    "solo leveling", "solo leveling",
    "the beginning after the end",
    # مانجا صاعدة (جديدة ومشهورة)
    "ichi the witch", "centuria",
    "ruridragon", "ruri dragon",
    "astro royale", "yokai buster murakami",
    "ultimate exorcist kiyoshi", "nue's exorcist",
    "mamayuyu", "super psychic policeman chojo",
    "the ichinose family's deadly sins",
    "two on ice", "fabricant 100",
    "the bugle call", "you and i are polar opposites",
    "rage of bahamut", "manabi no sora",
    # روايات ولايت نوفل مشهورة
    "mushoku tensei", "jobless reincarnation",
    "classroom of the elite", "youkoso jitsuryoku",
    "re:zero", "re zero",
    "sword art online", "sao",
    "overlord", "konosuba",
    "tensura", "that time i got reincarnated as a slime",
    "no game no life",
    "the rising of the shield hero",
    "tate no yuusha",
    "danmachi", "is it wrong to try to pick up girls in a dungeon",
    "a certain magical index", "toaru",
    "spice and wolf",
    "toradora", "oomuroke",
    "the melancholy of haruhi suzumiya",
    "baccano", "durarara",
    "kino's journey",
    "boogiepop", "monogatari",
    "oresuki", "goblin slayer",
    "grimgar of fantasy and ash",
    "saga of tanya the evil", "youjo senki",
    "trapped in a dating sim", "mobuSeka",
    "the world's finest assassin gets reincarnated",
    "the greatest demon lord is reborn as a typical nobody",
    "chillin' in another world with level 2 super cheat powers",
    "the strongest sage with the weakest crest",
    "arifureta", "arifureta from commonplace to world's strongest",
    "death march to the parallel world rhapsody",
    "in another world with my smartphone",
    "campfire cooking in another world with my absurd skill",
    "banished from the hero's party",
    "the great cleric",
    "by the grace of the gods",
    "parallel world pharmacy",
    "ascendance of a bookworm", "honzuki no gekokujou",
    "torture princess", "kumo desu ga nani ka",
    "majo no tabitabi", "the journey of elaina",
    "to your eternity", "fumetsu no anata e",
    # عناوين ناقصة إضافية
    "gundam", "mobile suit gundam",
    "fairy tail", "edens zero",
    "madoka magica", "puella magi madoka magica",
    "psycho-pass", "psycho pass",
    "gurren lagann", "tengen toppa gurren lagann",
    "kill la kill", "little witch academia",
    "soul eater", "fire force",
    "noragami", "bungo stray dogs",
    "blue exorcist", "ao no exorcist",
    "magi", "seven deadly sins", "nanatsu no taizai",
    "the irregular at magic high school", "mahouka",
    "a certain scientific railgun", "toaru kagaku no railgun",
    "akame ga kill", "parasyte", "kiseijuu",
    "erased", "boku dake ga inai machi",
    "samurai champloo", "space dandy",
    "another", "terror in resonance",
    "hell girl", "jigoku shoujo",
    "seraph of the end", "owari no seraph",
    "radiant", "the ancient magus bride",
    "dr. stone", "black clover",
    "asta", "yuno",
    "the rising of the shield hero", "tate no yuusha",
    "log horizon", "grimgar",
    "ascendance of a bookworm", "honzuki no gekokujou",
    "the saga of tanya the evil", "youjo senki",
    "kumo desu ga", "so i'm a spider so what",
    "arifureta", "death march",
    "in another world with my smartphone",
    "campfire cooking in another world",
    "banished from the hero's party",
    "by the grace of the gods",
    "parallel world pharmacy",
    "the great cleric",
    "trapped in a dating sim",
    "the world's finest assassin",
    "the greatest demon lord is reborn",
    "chillin in another world",
    "the strongest sage with the weakest crest",
    "sasaki and peeps",
    "the misfit of demon king academy",
    "maou gakuin",
    # أسماء أنميات إضافية
    "devil may cry", "castlevania", "arcane",
    "wistoria", "tsue to tsurugi", "mebius dust",
    "nippon sangoku",
    "the ghost in the shell",
    "kyoto animation", "oval gear",
    "akira", "mob psycho",
    "ultimate exorcist kiyoshi", "nue exorcist",
    "tokyo revengers", "wind breaker",
]

MAJOR_GAMES = [
    # ألعاب عالمية كبرى
    "grand theft auto", "gta", "call of duty", "cod",
    "final fantasy", "ffvii", "ff7", "ffxvi", "ff16", "ffvii remake",
    "elden ring", "dark souls", "sekiro", "bloodborne", "demon's souls",
    "zelda", "tears of the kingdom", "breath of the wild",
    "pokemon", "pokémon", "super mario", "mario",
    "nintendo", "nintendo switch", "switch 2",
    "playstation", "ps5", "ps4", "ps3",
    "xbox", "xbox series", "xbox series x", "xbox series s",
    "god of war", "ragnarok",
    "spider-man", "spiderman", "marvel's spider-man",
    "the last of us", "uncharted",
    "red dead redemption", "rdr2", "rdr",
    "cyberpunk 2077", "cyberpunk",
    "the witcher", "witcher", "witcher 4",
    "assassin's creed", "assassins creed",
    "far cry", "metal gear solid", "mgs", "metal gear",
    "resident evil", "biohazard",
    "street fighter", "mortal kombat",
    "minecraft", "fortnite",
    "valorant", "league of legends", "lol",
    "overwatch", "apex legends", "pubg",
    "dota", "dota 2", "counter-strike", "csgo", "cs2",
    "starfield", "skyrim", "elder scrolls",
    "fallout", "diablo",
    "warcraft", "world of warcraft", "wow",
    "star wars", "starwars",
    "doom", "quake", "wolfenstein",
    "batman", "arkham", "suicide squad kill the justice league",
    "hogwarts legacy", "harry potter",
    "silent hill", "alan wake", "control",
    "monster hunter", "monsterhunter", "monster hunter wilds",
    "dragon quest", "persona", "shin megami tensei", "metaphor refantazio",
    "kingdom hearts", "nier", "nier automata",
    "sonic", "mega man", "megaman",
    "tekken", "guilty gear",
    "ghost of tsushima", "ghost of yotei",
    "helldivers", "helldivers 2",
    "baldur's gate", "baldurs gate 3", "bg3",
    "prince of persia", "the lost crown",
    "stalker", "stalker 2",
    "warhammer", "space marine 2",
    "roblox", "among us",
    "tom clancy", "rainbow six", "siege", "the division",
    "mass effect", "dragon age",
    "half-life", "portal", "left 4 dead", "team fortress",
    "bio shock", "bioshock",
    "dead space", "dead island", "dying light",
    "outlast", "amnesia",
    "splinter cell", "hitman",
    "gran turismo", "forza", "forza horizon",
    "need for speed", "nfs", "burnout",
    "fifa", "ea sports", "pro evolution soccer", "pes", "efootball",
    "nba 2k", "madden",
    "rocket league", "fall guys",
    "among us",
    "it takes two", "split fiction",
    "black myth wukong", "wukong",
    "lies of p", "wo long", "rise of the ronin",
    "like a dragon", "yakuza",
    "final fantasy", "ff",
    "atomic heart",
    "hi-fi rush", "hifi rush",
    "sea of stars", "chained echoes",
    "hades", "hades 2",
    "hollow knight", "silksong",
    "celeste", "cuphead",
    "stray", "kena",
]

ALL_MAJOR = [w.lower() for w in MAJOR_ANIME + MAJOR_GAMES]

# ======== ترجمة ========
translator = None
_mal_cache = {}

def get_translator():
    global translator
    if translator is None:
        try:
            from deep_translator import GoogleTranslator
            translator = GoogleTranslator(source="en", target="ar")
        except Exception:
            translator = False
    return translator

def translate(text):
    t = get_translator()
    if t and text:
        try: return t.translate(text[:4000])
        except Exception: pass
    return text

# ======== دوال JSON ========
def load_json(path, default):
    if not os.path.exists(path): return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ======== دوال نصية ========
def clean_html(text):
    return re.sub(r"<[^>]+>", "", text).strip()

def extract_text(url):
    try:
        resp = requests.get(url, headers={"User-Agent": UA}, timeout=15)
        if resp.ok:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(resp.text, "html.parser")
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()
            text = soup.get_text(separator="\n", strip=True)
            lines = [l for l in text.split("\n") if len(l) > 40]
            return "\n".join(lines[:20])
    except: pass
    return ""

# ======== فلترة المحتوى ========
def is_blocked(title, description):
    text = (title + " " + description).lower()
    return any(w in text for w in EXCLUDE_WORDS)

def is_blocked_title(title):
    t = title.lower().strip()
    for blocked in BLOCKED_TITLES:
        if blocked in t or t in blocked:
            return True
    return False

def is_major_title(title, description):
    text = (title + " " + description).lower()
    for major in ALL_MAJOR:
        if major in text:
            return True
    return False

def check_anime_rating(title):
    if not title:
        return "unknown"
    t = title.lower()
    for cached_t, rating in _mal_cache.items():
        if cached_t in t or t in cached_t:
            return rating
    try:
        resp = requests.get("https://api.jikan.moe/v4/anime",
                            params={"q": title, "limit": 1, "sfw": True}, timeout=10)
        if resp.ok:
            data = resp.json()
            if data.get("data"):
                anime = data["data"][0]
                rating = (anime.get("rating") or "").lower()
                genres = [g["name"].lower() for g in anime.get("genres", [])]
                _mal_cache[t] = rating
                if "hentai" in genres or "ecchi" in genres:
                    return "blocked"
                if rating in ("rx - hentai", "r+ - mild nudity", "rx"):
                    return "blocked"
                return rating
    except: pass
    return "unknown"

# ======== معالجة الصور ========
def extract_images_from_article(url):
    images = []
    try:
        resp = requests.get(url, headers={"User-Agent": UA}, timeout=15)
        if resp.ok:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(resp.text, "html.parser")
            og = soup.find("meta", property="og:image")
            if og and og.get("content"):
                images.append(og["content"])
            for img in soup.find_all("img"):
                src = img.get("src") or img.get("data-src") or ""
                if src and src.startswith("http") and src not in images:
                    images.append(src)
                    if len(images) >= 5:
                        break
    except: pass
    return images[:5]

def remove_watermark(img_url, source_name):
    try:
        resp = requests.get(img_url, headers={"User-Agent": UA}, timeout=15)
        if not resp.ok:
            return img_url
        content_type = resp.headers.get("content-type", "")
        if "image" not in content_type:
            return img_url
        img = Image.open(BytesIO(resp.content))
        w, h = img.size
        cropped = False
        sn = source_name.lower()
        if "animenewsnetwork" in sn or "ann" in sn:
            img = img.crop((0, 0, w - 50, h - 50))
            cropped = True
        elif "gamereactor" in sn:
            img = img.crop((0, 0, w, h - 40))
            cropped = True
        elif h > 100:
            strip = img.crop((0, h - 15, w, h))
            try:
                ext = strip.getextrema()
                if isinstance(ext[0], (list, tuple)):
                    ranges = [mx - mn for mn, mx in ext]
                else:
                    ranges = [ext[1] - ext[0]]
                if all(r < 30 for r in ranges):
                    img = img.crop((0, 0, w, h - 40))
                    cropped = True
            except: pass
        if cropped:
            buf = BytesIO()
            img.save(buf, format="PNG")
            buf.seek(0)
            return buf
    except: pass
    return img_url

# ======== صياغة المنشور (نمط Baqer) ========
def build_caption_ar(title, description, extra_texts, settings):
    title_ar = translate(title) if settings.get("translate_enabled", True) else title
    desc_ar = translate(clean_html(description)[:300]) if settings.get("translate_enabled", True) else clean_html(description)[:300]
    lines = []
    if extra_texts:
        for txt in extra_texts[:5]:
            lines.append(f"<b>\u25c8 {txt.strip()[:200]}</b>")
    else:
        desc_short = "\n".join(desc_ar.split("\n")[:1])[:200]
        lines.append(f"<b>\u2756 {unescape(title_ar)}</b>")
        if desc_short and desc_short != title_ar[:100]:
            lines.append(f"<b>\u25c8 {unescape(desc_short)}</b>")
    lines.append("")
    lines.append(" @ksbskehwb")
    return "\n".join(lines)



# ======== إرسال تيليجرام وقوائم ========
def inline_keyboard(link):
    kb = []
    if link:
        kb.append([{"text": "\U0001f517 المصدر", "url": link}])
    kb.append([{"text": "\U0001f4e2 @ksbskehwb", "url": "https://t.me/ksbskehwb"}])
    return json.dumps({"inline_keyboard": kb})

def make_menu(chat_id, text, buttons, parse_mode=""):
    kb = json.dumps({"inline_keyboard": buttons})
    return requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={"chat_id": chat_id, "text": text[:4096], "parse_mode": parse_mode, "reply_markup": kb},
        timeout=15).ok

def edit_menu(chat_id, msg_id, text, buttons, parse_mode=""):
    kb = json.dumps({"inline_keyboard": buttons})
    return requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText",
        data={"chat_id": chat_id, "message_id": msg_id, "text": text[:4096], "parse_mode": parse_mode, "reply_markup": kb},
        timeout=15).ok

def answer_cb(cb_id, text=""):
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery",
        data={"callback_query_id": cb_id, "text": text, "show_alert": False}, timeout=5)

def send_message(chat_id, text, parse_mode="", link=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text[:4096], "parse_mode": parse_mode}
    if link:
        payload["reply_markup"] = inline_keyboard(link)
    try:
        r = requests.post(url, data=payload, timeout=15)
        if not r.ok:
            print(f"[SEND FAIL] {r.status_code} {r.text[:100]}")
        else:
            print(f"[SEND OK] chat={chat_id}")
    except Exception as e:
        print(f"[SEND ERROR] {e}")

def send_media_group(images, caption, channel, link=None):
    if not images:
        return False
    media = []
    files = {}
    for i, img in enumerate(images):
        if hasattr(img, "read"):
            fn = f"img{i}.png"
            files[fn] = (fn, img, "image/png")
            if i == 0:
                item = {"type": "photo", "media": f"attach://{fn}", "caption": caption[:1024], "parse_mode": "HTML"}
                if link:
                    item["reply_markup"] = inline_keyboard(link)
                media.append(item)
            else:
                media.append({"type": "photo", "media": f"attach://{fn}"})
        elif isinstance(img, str) and img.startswith("http"):
            if i == 0:
                item = {"type": "photo", "media": img, "caption": caption[:1024], "parse_mode": "HTML"}
                if link:
                    item["reply_markup"] = inline_keyboard(link)
                media.append(item)
            else:
                media.append({"type": "photo", "media": img})
    if not media:
        return False
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMediaGroup"
    payload = {"chat_id": channel, "media": json.dumps(media)}
    try:
        resp = requests.post(url, data=payload, files=files if files else None, timeout=30)
        print(f"[SEND MEDIA] {resp.status_code}")
        return resp.ok
    except Exception as e:
        print(f"[SEND MEDIA ERROR] {e}")
        return False

# ======== معالجة الأوامر ========
def process_commands(settings):
    offset = settings.get("update_offset", 0)
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    try:
        data = requests.get(url, params={"offset": offset, "timeout": 5}, timeout=10).json()
    except:
        return settings
    if not data.get("ok"):
        return settings
    changed = False

    # Menu helpers
    def main_menu_b(owner=False):
        b = []
        if owner:
            b.append([{"text": "\U0001f4e6 المصادر", "callback_data": "sources"},
                      {"text": "\u2699\ufe0f الإعدادات", "callback_data": "settings"}])
        b.append([{"text": "\U0001f4ca الإحصائيات", "callback_data": "stats"}])
        b.append([{"text": "\U0001f30d القناة", "url": "https://t.me/ksbskehwb"},
                  {"text": "\U0001f916 /menu", "callback_data": "main"}])
        return b

    def srcs_menu(srcs):
        b = []
        for name, info in srcs.items():
            en = info.get("enabled", True) if isinstance(info, dict) else True
            s = "\u2705" if en else "\u274c"
            action = "off" if en else "on"
            b.append([{"text": f"{s} {name}", "callback_data": f"src|{action}|{name}"}])
        b.append([{"text": "\u2795 إضافة مصدر", "callback_data": "addsrc"}])
        b.append([{"text": "\U0001f519 رجوع", "callback_data": "main"}])
        return b

    def settings_menu(s):
        wl = "\u2705" if s.get("whitelist_enabled", True) else "\u274c"
        ml = "\u2705" if s.get("mal_check_enabled", True) else "\u274c"
        tr = "\u2705" if s.get("translate_enabled", True) else "\u274c"
        b = [
            [{"text": f"\U0001f4e6 القائمة البيضاء {wl}", "callback_data": "set|whitelist"}],
            [{"text": f"\U0001f50d فحص MAL {ml}", "callback_data": "set|mal"}],
            [{"text": f"\U0001f310 الترجمة {tr}", "callback_data": "set|translate"}],
            [{"text": f"\u23f1 التكرار: {s['interval_minutes']}د", "callback_data": "set|interval"}],
            [{"text": f"\U0001f4c5 فلترة: {s['max_age_days']} يوم", "callback_data": "set|maxage"}],
            [{"text": f"\U0001f4ca الحد: {s['max_per_run']}", "callback_data": "set|maxitems"}],
            [{"text": "\U0001f519 رجوع", "callback_data": "main"}],
        ]
        return b

    for update in data.get("result", []):
        nid = update["update_id"]
        if nid >= offset: offset = nid + 1

        # ====== Callback Queries ======
        cb = update.get("callback_query")
        if cb:
            chat_id = cb["message"]["chat"]["id"]
            msg_id = cb["message"]["message_id"]
            uid = cb["from"]["id"]
            username = cb.get("from", {}).get("username", "")
            cb_id = cb["id"]
            cb_data = cb.get("data", "")
            is_owner = (uid == settings.get("owner_id") or username.lower() == settings.get("owner_username", "").lower())

            if cb_data not in ("main", "stats") and not is_owner:
                answer_cb(cb_id, "\u274c غير مصرح"); continue

            settings["_commands_processed"] = True; changed = True
            srcs = settings.get("sources", {})
            ch = settings.get("channel_id", "@ksbskehwb")

            if cb_data == "main":
                posted = load_json(POSTED_FILE, [])
                active = sum(1 for v in srcs.values() if (v.get("enabled") if isinstance(v, dict) else v))
                txt = (
                    "\U0001f916 *بوت أخبار الأنمي والألعاب*\n\n"
                    f"\U0001f4f0 منشورات: {len(posted)}\n"
                    f"\U0001f4e6 مصادر نشطة: {active}/{len(srcs)}\n"
                    f"\u23f1 التكرار: كل {settings['interval_minutes']} د\n\n"
                    f"\U0001f4e2 @{ch.lstrip('@')}\n\U0001f464 @Ozzrr"
                )
                answer_cb(cb_id)
                edit_menu(chat_id, msg_id, txt, main_menu_b(is_owner), parse_mode="Markdown")

            elif cb_data == "sources" and is_owner:
                answer_cb(cb_id)
                if not srcs:
                    edit_menu(chat_id, msg_id, "\U0001f4e6 لا توجد مصادر مضافة.\nاستعمل /addsource", srcs_menu(srcs))
                else:
                    txt = "\U0001f4e6 *المصادر* - اضغط لتفعيل/تعطيل"
                    edit_menu(chat_id, msg_id, txt, srcs_menu(srcs), parse_mode="Markdown")

            elif cb_data.startswith("src|") and is_owner:
                _, action, name = cb_data.split("|", 2)
                if name in srcs and isinstance(srcs[name], dict):
                    srcs[name]["enabled"] = (action == "on")
                    settings["sources"] = srcs
                    save_json(SETTINGS_FILE, settings)
                answer_cb(cb_id, "\u2705 تم التبديل")
                edit_menu(chat_id, msg_id, "\U0001f4e6 *المصادر*", srcs_menu(srcs), parse_mode="Markdown")

            elif cb_data == "addsrc" and is_owner:
                answer_cb(cb_id, "أرسل: /addsource <اسم> <رابط RSS>")
                send_message(chat_id, "\u2795 أرسل الأمر التالي:\n/addsource <اسم المصدر> <رابط RSS>")

            elif cb_data == "settings" and is_owner:
                answer_cb(cb_id)
                s = settings
                edit_menu(chat_id, msg_id, f"\u2699\ufe0f *الإعدادات*\n\n\u23f1 التكرار: {s['interval_minutes']}د\n\U0001f4c5 فلترة: {s['max_age_days']} يوم\n\U0001f4ca الحد: {s['max_per_run']}\n",
                    settings_menu(s), parse_mode="Markdown")

            elif cb_data.startswith("set|") and is_owner:
                _, key = cb_data.split("|", 1)
                if key == "whitelist":
                    settings["whitelist_enabled"] = not settings.get("whitelist_enabled", True)
                elif key == "mal":
                    settings["mal_check_enabled"] = not settings.get("mal_check_enabled", True)
                elif key == "translate":
                    settings["translate_enabled"] = not settings.get("translate_enabled", True)
                elif key in ("interval", "maxage", "maxitems"):
                    answer_cb(cb_id, f"استعمل الأمر: /{key} <قيمة>")
                    continue
                save_json(SETTINGS_FILE, settings)
                answer_cb(cb_id, "\u2705 تم التبديل")
                s = settings
                edit_menu(chat_id, msg_id, f"\u2699\ufe0f *الإعدادات*", settings_menu(s), parse_mode="Markdown")

            elif cb_data == "stats":
                posted = load_json(POSTED_FILE, [])
                active = sum(1 for v in srcs.values() if (v.get("enabled") if isinstance(v, dict) else v))
                edit_menu(chat_id, msg_id,
                    f"\U0001f4ca *إحصائيات البوت*\n\n"
                    f"\U0001f4f0 إجمالي المنشور: {len(posted)}\n"
                    f"\U0001f4e6 مصادر نشطة: {active}/{len(srcs)}\n"
                    f"\u23f1 تكرار: كل {settings['interval_minutes']} د\n"
                    f"\U0001f4c5 فلترة: {settings['max_age_days']} يوم",
                    [[{"text": "\U0001f519 رجوع", "callback_data": "main"}]], parse_mode="Markdown")
                answer_cb(cb_id)

            elif cb_data in ("run", "trigger") and is_owner:
                send_message(chat_id, "\U0001f504 يتم التشغيل...")
                answer_cb(cb_id, "\U0001f504 جارِ التشغيل")

            continue

        # ====== Regular Messages ======
        msg = update.get("message") or update.get("edited_message")
        if not msg: continue
        chat_id = msg.get("chat", {}).get("id")
        uid = msg.get("from", {}).get("id")
        username = msg.get("from", {}).get("username", "")
        text = (msg.get("text") or "").strip()
        if not text: continue
        parts = text.split()
        cmd = parts[0].lower()
        arg = " ".join(parts[1:]) if len(parts) > 1 else ""

        if cmd in ("/start", "/menu"):
            is_owner = (uid == settings.get("owner_id") or username.lower() == settings.get("owner_username", "").lower())
            ch = settings.get("channel_id", "@ksbskehwb")
            make_menu(chat_id,
                "\U0001f916 *بوت أخبار الأنمي والألعاب*\n"
                "\u2728 ينشر أخبار الأنمي والمانجا والألعاب تلقائياً\n\n"
                f"\U0001f4e2 @{ch.lstrip('@')}\n\U0001f464 @Ozzrr",
                main_menu_b(is_owner), parse_mode="Markdown")
            settings["_commands_processed"] = True
            changed = True
            continue

        if uid != settings.get("owner_id") and username.lower() != settings.get("owner_username", "").lower():
            continue

        settings["_commands_processed"] = True
        srcs = settings.get("sources", {})

        if cmd == "/addsource":
            p = text.split(maxsplit=2)
            if len(p) >= 3:
                name = p[1]
                rss_url = p[2]
                srcs[name] = {"url": rss_url, "enabled": True}
                settings["sources"] = srcs
                send_message(chat_id, f"✅ تم إضافة المصدر:\n{name}\n{rss_url}")
                changed = True
            else:
                send_message(chat_id, "❌ استعمل: /addsource <الاسم> <رابط RSS>")

        elif cmd == "/removesource":
            if arg and arg in srcs:
                del srcs[arg]
                settings["sources"] = srcs
                send_message(chat_id, f"✅ تم حذف المصدر: {arg}")
                changed = True
            elif arg:
                send_message(chat_id, f"❌ المصدر \"{arg}\" غير موجود")
            else:
                send_message(chat_id, "❌ استعمل: /removesource <الاسم>")

        elif cmd == "/listsources":
            if not srcs:
                send_message(chat_id, "📡 لا توجد مصادر مضافة")
            else:
                lines = ["📡 المصادر المضافة:"]
                for name, info in srcs.items():
                    url = info.get("url", "?")
                    en = info.get("enabled", True)
                    s = "✅" if en else "❌"
                    lines.append(f"\n{s} {name}\n   {url}")
                send_message(chat_id, "".join(lines))

        elif cmd == "/source":
            p = text.split(maxsplit=2)
            if len(p) >= 3:
                name = p[1]
                val = p[2].lower()
                if name in srcs and isinstance(srcs[name], dict):
                    if val in ("on", "true", "1"):
                        srcs[name]["enabled"] = True
                        send_message(chat_id, f"✅ تم تفعيل {name}")
                    elif val in ("off", "false", "0"):
                        srcs[name]["enabled"] = False
                        send_message(chat_id, f"✅ تم إيقاف {name}")
                    else:
                        send_message(chat_id, "❌ استعمل: /source <الاسم> on/off")
                    settings["sources"] = srcs
                    changed = True
                elif name in srcs:
                    old = srcs[name]
                    srcs[name] = {"url": old if isinstance(old, str) else old.get("url", "?"), "enabled": val in ("on", "true", "1")}
                    settings["sources"] = srcs
                    send_message(chat_id, f"✅ تم تعديل {name}")
                    changed = True
                else:
                    send_message(chat_id, f"❌ المصدر {name} غير موجود")
            else:
                send_message(chat_id, "❌ استعمل: /source <الاسم> on/off")

        elif cmd == "/ref":
            p = text.split(maxsplit=2)
            if len(p) >= 3:
                main_url = p[1]
                extra_url = p[2]
                extras = settings.get("extra_sources", {})
                key = hashlib.md5(main_url.encode()).hexdigest()
                if key not in extras:
                    extras[key] = []
                extras[key].append(extra_url)
                settings["extra_sources"] = extras
                send_message(chat_id, f"✅ تم ربط مرجع إضافي:\n{extra_url}")
                changed = True
            else:
                send_message(chat_id, "❌ استعمل: /ref <الرابط الرئيسي> <الرابط الإضافي>")

        elif cmd == "/refs":
            extras = settings.get("extra_sources", {})
            if not extras:
                send_message(chat_id, "📎 لا توجد مراجع مخزنة")
            else:
                lines = ["📎 المراجع المخزنة:"]
                for key, urls in list(extras.items())[:10]:
                    lines.append(f"\n{key[:12]}... -> {len(urls)} رابط")
                send_message(chat_id, "".join(lines))

        elif cmd == "/delref":
            extras = settings.get("extra_sources", {})
            key = hashlib.md5(arg.encode()).hexdigest() if arg else ""
            if key in extras:
                del extras[key]
                settings["extra_sources"] = extras
                send_message(chat_id, "✅ تم حذف المرجع")
                changed = True
            else:
                send_message(chat_id, "❌ المرجع غير موجود")

        elif cmd == "/settings":
            s = settings
            src_str = "\n".join(f"  {k}: {'✅' if isinstance(v, dict) and v.get('enabled') else '❌' if isinstance(v, dict) else '✅' if v else '❌'}" for k, v in srcs.items())
            send_message(chat_id, f"⚙️ الإعدادات\n\n"
                f"⏱ التكرار: {s['interval_minutes']} د\n"
                f"📅 الفلترة: {s['max_age_days']} يوم\n"
                f"📊 الحد: {s['max_per_run']}\n"
                f"🌍 ترجمة: {'✅' if s.get('translate_enabled', True) else '❌'}\n"
                f"📡 المصادر ({len(srcs)}):\n{src_str}")
            changed = True

        elif cmd == "/status":
            posted = load_json(POSTED_FILE, [])
            send_message(chat_id, f"🤖 حالة البوت\n\n"
                f"✅ شغال\n📰 المنشور: {len(posted)}\n"
                f"⏱ {settings['interval_minutes']} د\n"
                f"📢 {settings.get('channel_id', '@ksbskehwb')}")

        elif cmd == "/stats":
            posted = load_json(POSTED_FILE, [])
            active = sum(1 for v in srcs.values() if (v.get('enabled') if isinstance(v, dict) else v))
            send_message(chat_id, f"📊 إحصائيات\n\n"
                f"📰 إجمالي: {len(posted)}\n"
                f"⏱ تكرار: كل {settings['interval_minutes']} د\n"
                f"📅 فلترة: {settings['max_age_days']} يوم\n"
                f"📊 حد: {settings['max_per_run']}\n"
                f"📡 مصادر نشطة: {active}/{len(srcs)}")

        elif cmd == "/interval":
            try:
                val = int(arg)
                if 5 <= val <= 180:
                    settings["interval_minutes"] = val
                    send_message(chat_id, f"✅ التكرار → {val} د")
                    changed = True
                else: send_message(chat_id, "❌ بين 5 و 180")
            except: send_message(chat_id, "❌ /interval <دقيقة>")

        elif cmd == "/maxage":
            try:
                val = int(arg)
                if 1 <= val <= 30:
                    settings["max_age_days"] = val
                    send_message(chat_id, f"✅ فلترة → {val} يوم")
                    changed = True
                else: send_message(chat_id, "❌ بين 1 و 30")
            except: send_message(chat_id, "❌ /maxage <عدد>")

        elif cmd == "/maxitems":
            try:
                val = int(arg)
                if 1 <= val <= 20:
                    settings["max_per_run"] = val
                    send_message(chat_id, f"✅ الحد → {val}")
                    changed = True
                else: send_message(chat_id, "❌ بين 1 و 20")
            except: send_message(chat_id, "❌ /maxitems <عدد>")

        elif cmd == "/whitelist":
            if arg == "on":
                settings["whitelist_enabled"] = True
                send_message(chat_id, "✅ تفعيل القائمة البيضاء")
                changed = True
            elif arg == "off":
                settings["whitelist_enabled"] = False
                send_message(chat_id, "✅ إيقاف القائمة البيضاء")
                changed = True
            else:
                send_message(chat_id, "❌ /whitelist on/off")

        elif cmd == "/mal":
            if arg == "on":
                settings["mal_check_enabled"] = True
                send_message(chat_id, "✅ تفعيل فحص MAL")
                changed = True
            elif arg == "off":
                settings["mal_check_enabled"] = False
                send_message(chat_id, "✅ إيقاف فحص MAL")
                changed = True
            else:
                send_message(chat_id, "❌ /mal on/off")

        elif cmd in ("/help", "/admin"):
            is_owner = True
            ch = settings.get("channel_id", "@ksbskehwb")
            make_menu(chat_id,
                "\U0001f916 *بوت أخبار الأنمي والألعاب*\n"
                "\u2728 ينشر أخبار الأنمي والمانجا والألعاب تلقائياً\n\n"
                f"\U0001f4e2 @{ch.lstrip('@')}\n\U0001f464 @Ozzrr",
                main_menu_b(is_owner), parse_mode="Markdown")

        elif cmd == "/run":
            send_message(chat_id, "🔄 يتم التشغيل...")
            changed = True

    settings["update_offset"] = offset
    if changed: save_json(SETTINGS_FILE, settings)
    return settings

# ======== الدالة الرئيسية ========
def main():
    global CHANNEL_ID
    if not BOT_TOKEN:
        print("TELEGRAM_BOT_TOKEN not set")
        return

    settings = load_json(SETTINGS_FILE, {
        "owner_id": 5381442151, "owner_username": "Ozzrr",
        "interval_minutes": 15, "max_age_days": 2, "max_per_run": 3,
        "channel_id": "@ksbskehwb",
        "sources": {},
        "extra_sources": {},
        "translate_enabled": True, "emoji_enabled": True,
        "whitelist_enabled": True, "mal_check_enabled": True,
        "update_offset": 0, "run_now": False, "last_full_run": 0, "_init_sent": False
    })

    # تصحيح تنسيق المصادر القديم → الجديد
    srcs = settings.get("sources", {})
    needs_migrate = False
    for name, info in list(srcs.items()):
        if not isinstance(info, dict):
            old_val = info
            srcs[name] = {"url": old_val if isinstance(old_val, str) else f"https://{name.lower().replace(' ','')}.com/rss", "enabled": bool(old_val) if not isinstance(old_val, str) else True}
            needs_migrate = True
    if needs_migrate:
        settings["sources"] = srcs
        save_json(SETTINGS_FILE, settings)

    CHANNEL_ID = settings.get("channel_id", "@ksbskehwb")

    settings = process_commands(settings)

    if settings.get("_commands_processed"):
        gh_token = os.environ.get("GITHUB_TOKEN", "")
        if gh_token:
            try:
                requests.post(
                    "https://api.github.com/repos/Bbnawf/news-bot/actions/workflows/277043592/dispatches",
                    headers={"Authorization": f"Bearer {gh_token}", "Accept": "application/vnd.github.v3+json"},
                    json={"ref": "main"}, timeout=10
                )
            except: pass

    now = datetime.now(timezone.utc)
    last_full = settings.get("last_full_run", 0)
    interval = settings.get("interval_minutes", 15)
    should_run = settings.get("run_now") or (now.timestamp() - last_full >= interval * 60)

    if should_run:
        settings["run_now"] = False
        settings["last_full_run"] = now.timestamp()
    save_json(SETTINGS_FILE, settings)

    if not should_run:
        rem = int(interval - (now.timestamp() - last_full) / 60)
        print(f"[WAIT] باقي {rem} د")
        return

    posted = load_json(POSTED_FILE, [])
    posted_set = set(posted)
    two_days_ago = now - timedelta(days=settings["max_age_days"])
    items_found = []
    whitelist_en = settings.get("whitelist_enabled", True)
    mal_en = settings.get("mal_check_enabled", True)
    extras = settings.get("extra_sources", {})

    for source_name, sinfo in srcs.items():
        if isinstance(sinfo, dict) and not sinfo.get("enabled", True):
            print(f"[OFF] {source_name}")
            continue
        feed_url = sinfo.get("url", "") if isinstance(sinfo, dict) else sinfo
        if not feed_url:
            continue
        try:
            feed = feedparser.parse(feed_url)
        except Exception as e:
            print(f"[RSS ERR] {source_name}: {e}")
            continue

        for entry in feed.entries:
            title = entry.get("title", "").strip()
            link = entry.get("link", "").strip()
            pub_date = entry.get("published_parsed") or entry.get("updated_parsed")
            description = entry.get("description", "") or entry.get("summary", "")
            if not title: continue
            if pub_date:
                pub_dt = datetime(*pub_date[:6], tzinfo=timezone.utc)
                if pub_dt < two_days_ago: continue
            # فحص المحتوى الممنوع
            if is_blocked(title, description):
                print(f"[BLOCKED] {title[:50]}...")
                continue
            if is_blocked_title(title):
                print(f"[BLOCKED TITLE] {title[:50]}...")
                continue
            # القائمة البيضاء (تطبق على جميع المصادر)
            if whitelist_en and not is_major_title(title, description):
                print(f"[SKIP WHITELIST] {title[:50]}...")
                continue
            # فحص تصنيف MAL
            if mal_en:
                rating = check_anime_rating(title)
                if rating == "blocked":
                    print(f"[MAL BLOCKED] {title[:50]}...")
                    continue
            # منع التكرار
            key = hashlib.md5((title + link).encode()).hexdigest()
            if key in posted_set: continue
            photo_url = ""
            if hasattr(entry, "media_content"):
                for media in entry.media_content:
                    if media.get("medium") == "image":
                        photo_url = media.get("url", ""); break
            if not photo_url and link:
                try:
                    resp = requests.get(link, headers={"User-Agent": UA}, timeout=15)
                    if resp.ok:
                        match = re.search(r'<meta\s+property="og:image"\s+content="([^"]+)"', resp.text)
                        if match: photo_url = match.group(1)
                except: pass

            # مصادر إضافية (references)
            extra_texts = []
            link_key = hashlib.md5(link.encode()).hexdigest()
            if link_key in extras:
                for extra_url in extras[link_key]:
                    et = extract_text(extra_url)
                    if et:
                        extra_texts.append(et[:300])

            items_found.append((title, description, source_name, link, photo_url, key, extra_texts))

    max_per = settings["max_per_run"]
    sent = 0
    channel = settings.get("channel_id", "@ksbskehwb")

    for title, description, source_name, link, photo_url, key, extra_texts in items_found:
        posted_set.add(key)
        if sent >= max_per: continue
        caption = build_caption_ar(title, description, extra_texts, settings)
        ok = False
        if photo_url:
            images = []
            main_img = remove_watermark(photo_url, source_name)
            images.append(main_img)
            extra_imgs = extract_images_from_article(link)
            added = 0
            for ei in extra_imgs[:5]:
                if ei == photo_url: continue
                processed = remove_watermark(ei, source_name)
                images.append(processed)
                added += 1
                if added >= 4: break
            ok = send_media_group(images, caption, channel, link=link)
        if not ok:
            ok = send_message(channel, caption, parse_mode="HTML", link=link)
        if ok:
            sent += 1
            print(f"[OK] {title[:50]}...")
        else:
            print(f"[FAIL] {title[:50]}...")

    save_json(POSTED_FILE, list(posted_set))
    print(f"\n[SENT] {sent} خبر")

if __name__ == "__main__":
    main()
