import telebot, json, os, time, threading, traceback
from telebot import types
from flask import Flask
from threading import Thread

BOT_TOKEN = "8963887399:AAFwzzB4dQvqPBt2baaO_vzJLCQc6qMw7Gk"
OWNER_ID = 7142950609

bot = telebot.TeleBot(BOT_TOKEN)
DB_FILE = "database.json"

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot Running ✅"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

Thread(target=run_web, daemon=True).start()

DEFAULT_DB = {
    "users": {},
    "admins": [OWNER_ID],
    "channels": [],
    "rewards": {},
    "ads": {},
    "ads_targets": [],
    "settings": {
        "forward_on": False,
        "refer_on": True,
        "refer_target": 3,
        "refer_reward": None,
        "ads_on": False,
        "ads_time": 60,
        "auto_delete_on": True
    },
    "states": {}
}

def load_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_DB, f, indent=2, ensure_ascii=False)
        return DEFAULT_DB.copy()

    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except:
        data = DEFAULT_DB.copy()

    for k, v in DEFAULT_DB.items():
        if k not in data:
            data[k] = v

    for k, v in DEFAULT_DB["settings"].items():
        if k not in data["settings"]:
            data["settings"][k] = v

    if OWNER_ID not in data["admins"]:
        data["admins"].append(OWNER_ID)

    return data

db = load_db()

def save_db():
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)

def is_admin(uid):
    return uid == OWNER_ID or uid in db["admins"]

def set_state(uid, state):
    db["states"][str(uid)] = state
    save_db()

def get_state(uid):
    return db["states"].get(str(uid))

def clear_state(uid):
    db["states"].pop(str(uid), None)
    save_db()

def add_user(user):
    uid = str(user.id)
    if uid not in db["users"]:
        db["users"][uid] = {
            "id": user.id,
            "name": user.first_name or "User",
            "username": user.username or "",
            "verified": False,
            "refs": [],
            "referred_by": None,
            "joined": int(time.time())
        }
        save_db()

def safe_delete(chat_id, msg_id):
    try:
        bot.delete_message(chat_id, msg_id)
    except:
        pass

def loading_animation(chat_id):
    try:
        msg = bot.send_message(chat_id, "⚡ LOADING...\n▱▱▱▱▱▱▱▱▱▱ 0%")
        frames = [
            "⚡ LOADING...\n▰▱▱▱▱▱▱▱▱▱ 10%",
            "⚡ LOADING...\n▰▰▱▱▱▱▱▱▱▱ 20%",
            "⚡ LOADING...\n▰▰▰▱▱▱▱▱▱▱ 30%",
            "⚡ LOADING...\n▰▰▰▰▱▱▱▱▱▱ 40%",
            "⚡ LOADING...\n▰▰▰▰▰▱▱▱▱▱ 50%",
            "⚡ LOADING...\n▰▰▰▰▰▰▱▱▱▱ 60%",
            "⚡ LOADING...\n▰▰▰▰▰▰▰▱▱▱ 70%",
            "⚡ LOADING...\n▰▰▰▰▰▰▰▰▱▱ 80%",
            "⚡ LOADING...\n▰▰▰▰▰▰▰▰▰▱ 90%",
            "✅ READY...\n▰▰▰▰▰▰▰▰▰▰ 100%"
        ]
        for f in frames:
            time.sleep(0.18)
            try:
                bot.edit_message_text(f, chat_id, msg.message_id)
            except:
                pass
        safe_delete(chat_id, msg.message_id)
    except:
        pass

def verify_animation(chat_id):
    try:
        msg = bot.send_message(chat_id, "⌛ CHECKING...\n▱▱▱▱▱▱▱▱▱▱ 0%")
        frames = [
            "⌛ CHECKING...\n▰▱▱▱▱▱▱▱▱▱ 10%",
            "⌛ CHECKING...\n▰▰▱▱▱▱▱▱▱▱ 20%",
            "⌛ CHECKING...\n▰▰▰▱▱▱▱▱▱▱ 30%",
            "⌛ CHECKING...\n▰▰▰▰▱▱▱▱▱▱ 40%",
            "⌛ CHECKING...\n▰▰▰▰▰▱▱▱▱▱ 50%",
            "⌛ CHECKING...\n▰▰▰▰▰▰▱▱▱▱ 60%",
            "⌛ CHECKING...\n▰▰▰▰▰▰▰▱▱▱ 70%",
            "⌛ CHECKING...\n▰▰▰▰▰▰▰▰▱▱ 80%",
            "⌛ CHECKING...\n▰▰▰▰▰▰▰▰▰▱ 90%",
            "⌛ CHECKING...\n▰▰▰▰▰▰▰▰▰▰ 100%"
        ]
        for f in frames:
            time.sleep(0.25)
            try:
                bot.edit_message_text(f, chat_id, msg.message_id)
            except:
                pass
        safe_delete(chat_id, msg.message_id)
    except:
        pass

def start_keyboard():
    kb = types.InlineKeyboardMarkup(row_width=2)

    btns = []
    for ch in db["channels"]:
        btns.append(types.InlineKeyboardButton(ch["name"], url=ch["link"]))

    for i in range(0, len(btns), 2):
        kb.row(*btns[i:i+2])

    kb.add(types.InlineKeyboardButton("🎯 VERIFY", callback_data="verify_join"))
    return kb

def claim_keyboard():
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("🎁 CLAIM REWARD", callback_data="claim_reward"))
    return kb

def welcome_text(user):
    return f"""🔥 WELCOME {user.first_name or 'User'} ⚡

👥 Total Users: {len(db["users"])}

💗 Join all channels
🎯 Then click VERIFY"""

def send_welcome(message):
    user = message.from_user
    add_user(user)
    loading_animation(message.chat.id)

    text = welcome_text(user)

    try:
        photos = bot.get_user_profile_photos(user.id, limit=1)
        if photos.total_count > 0:
            file_id = photos.photos[0][-1].file_id
            bot.send_photo(message.chat.id, file_id, caption=text, reply_markup=start_keyboard())
        else:
            bot.send_message(message.chat.id, text, reply_markup=start_keyboard())
    except:
        bot.send_message(message.chat.id, text, reply_markup=start_keyboard())

def check_join(uid):
    missing = []
    for ch in db["channels"]:
        try:
            mem = bot.get_chat_member(ch["chat"], uid)
            if mem.status not in ["member", "administrator", "creator"]:
                missing.append(ch["name"])
        except:
            missing.append(ch["name"])
    return len(missing) == 0, missing

@bot.message_handler(commands=["start"])
def start_cmd(message):
    add_user(message.from_user)
    uid = str(message.from_user.id)

    parts = message.text.split()
    if len(parts) > 1 and db["settings"]["refer_on"]:
        ref = parts[1]
        if ref != uid and ref in db["users"]:
            if db["users"][uid].get("referred_by") is None:
                db["users"][uid]["referred_by"] = ref
                if uid not in db["users"][ref]["refs"]:
                    db["users"][ref]["refs"].append(uid)
                save_db()

    send_welcome(message)

@bot.callback_query_handler(func=lambda c: c.data == "verify_join")
def verify_join(call):
    add_user(call.from_user)
    verify_animation(call.message.chat.id)

    ok, missing = check_join(call.from_user.id)

    if not ok:
        txt = "❌ Pehle ye channels join karo:\n\n"
        txt += "\n".join([f"• {x}" for x in missing])
        return bot.send_message(call.message.chat.id, txt, reply_markup=start_keyboard())

    db["users"][str(call.from_user.id)]["verified"] = True
    save_db()

    bot.send_message(
        call.message.chat.id,
        "✅ VERIFIED SUCCESSFULLY\n\n🎁 Reward claim karo.",
        reply_markup=claim_keyboard()
    )

@bot.callback_query_handler(func=lambda c: c.data == "claim_reward")
def claim_reward(call):
    uid = str(call.from_user.id)

    if uid not in db["users"] or not db["users"][uid]["verified"]:
        return bot.answer_callback_query(call.id, "Pehle verify karo ❌")

    refs = len(db["users"][uid].get("refs", []))
    target = int(db["settings"].get("refer_target", 3))

    if refs < target:
        bot_username = bot.get_me().username
        link = f"https://t.me/{bot_username}?start={uid}"
        return bot.send_message(
            call.message.chat.id,
            f"❌ Reward locked\n\n👥 Refer: {refs}/{target}\n\nApna refer link share karo:\n{link}"
        )

    reward_id = db["settings"].get("refer_reward")
    if not reward_id or reward_id not in db["rewards"]:
        return bot.send_message(call.message.chat.id, "❌ Refer reward set nahi hai.")

    return send_reward(call.message.chat.id, db["rewards"][reward_id])

def send_reward(chat_id, reward):
    sent = None
    try:
        typ = reward["type"]
        con = reward["content"]
        cap = reward.get("caption", "🎁 Reward")

        if typ == "text":
            sent = bot.send_message(chat_id, con)
        elif typ == "photo":
            sent = bot.send_photo(chat_id, con, caption=cap)
        elif typ == "video":
            sent = bot.send_video(chat_id, con, caption=cap)
        else:
            sent = bot.send_document(chat_id, con, caption=cap)

        if db["settings"]["auto_delete_on"] and sent:
            threading.Timer(300, lambda: safe_delete(chat_id, sent.message_id)).start()

    except Exception as e:
        bot.send_message(chat_id, f"❌ Reward error: {e}")
      # =====================
# ADMIN PANEL
# =====================

def admin_keyboard():
    kb = types.InlineKeyboardMarkup(row_width=2)

    kb.add(
        types.InlineKeyboardButton("➕ Add Channel", callback_data="admin_add_channel"),
        types.InlineKeyboardButton("❌ Remove Channel", callback_data="admin_remove_channel")
    )

    kb.add(
        types.InlineKeyboardButton("📋 List Channel", callback_data="admin_list_channel"),
        types.InlineKeyboardButton("🎁 Add Reward", callback_data="admin_add_reward")
    )

    kb.add(
        types.InlineKeyboardButton("🗑 Remove Reward", callback_data="admin_remove_reward"),
        types.InlineKeyboardButton("📦 List Reward", callback_data="admin_list_reward")
    )

    kb.add(
        types.InlineKeyboardButton("📢 Ads Panel", callback_data="admin_ads_panel"),
        types.InlineKeyboardButton("🔁 Refer ON/OFF", callback_data="admin_refer_toggle")
    )

    kb.add(
        types.InlineKeyboardButton("🎯 Refer Target", callback_data="admin_refer_target"),
        types.InlineKeyboardButton("🎁 Refer Reward", callback_data="admin_refer_reward")
    )

    kb.add(
        types.InlineKeyboardButton("🔐 Forward ON/OFF", callback_data="admin_forward_toggle"),
        types.InlineKeyboardButton("🗑 Auto Delete ON/OFF", callback_data="admin_auto_delete_toggle")
    )

    kb.add(
        types.InlineKeyboardButton("📊 Stats", callback_data="admin_stats"),
        types.InlineKeyboardButton("👥 Multi Admin", callback_data="admin_multi_admin")
    )

    kb.add(
        types.InlineKeyboardButton("📢 Text Broadcast", callback_data="admin_text_broadcast"),
        types.InlineKeyboardButton("🖼 Media Broadcast", callback_data="admin_media_broadcast")
    )

    kb.add(
        types.InlineKeyboardButton("⚪ Button Broadcast", callback_data="admin_button_broadcast")
    )

    return kb

@bot.message_handler(commands=["admin"])
def admin_panel(message):
    if not is_admin(message.from_user.id):
        return

    bot.send_message(
        message.chat.id,
        "👑 ADMIN PANEL",
        reply_markup=admin_keyboard()
    )

# =====================
# ADS PANEL
# =====================

def ads_keyboard():
    kb = types.InlineKeyboardMarkup(row_width=2)

    kb.add(
        types.InlineKeyboardButton("➕ Add Ads", callback_data="ads_add"),
        types.InlineKeyboardButton("❌ Remove Ads", callback_data="ads_remove")
    )

    kb.add(
        types.InlineKeyboardButton("📋 List Ads", callback_data="ads_list"),
        types.InlineKeyboardButton("📌 Ads ON/OFF", callback_data="ads_toggle")
    )

    kb.add(
        types.InlineKeyboardButton("⏱ Ads Time", callback_data="ads_time"),
        types.InlineKeyboardButton("➕ Add Target", callback_data="ads_add_target")
    )

    kb.add(
        types.InlineKeyboardButton("❌ Remove Target", callback_data="ads_remove_target"),
        types.InlineKeyboardButton("📋 List Target", callback_data="ads_list_target")
    )

    kb.add(
        types.InlineKeyboardButton("🚀 Run Ads Now", callback_data="ads_run_now")
    )

    return kb

@bot.callback_query_handler(func=lambda c: c.data == "admin_ads_panel")
def admin_ads_panel(call):
    if not is_admin(call.from_user.id):
        return

    bot.send_message(
        call.message.chat.id,
        "📢 ADS PANEL",
        reply_markup=ads_keyboard()
    )

# =====================
# CHANNEL BUTTONS
# =====================

@bot.callback_query_handler(func=lambda c: c.data == "admin_add_channel")
def add_channel_btn(call):
    if not is_admin(call.from_user.id):
        return

    set_state(call.from_user.id, "add_channel")

    bot.send_message(
        call.message.chat.id,
        "Send:\n\nNAME | USERNAME | LINK"
    )

@bot.callback_query_handler(func=lambda c: c.data == "admin_remove_channel")
def remove_channel_btn(call):
    if not is_admin(call.from_user.id):
        return

    set_state(call.from_user.id, "remove_channel")

    bot.send_message(call.message.chat.id, "Send channel name.")

@bot.callback_query_handler(func=lambda c: c.data == "admin_list_channel")
def list_channel_btn(call):
    if not is_admin(call.from_user.id):
        return

    if not db["channels"]:
        return bot.send_message(call.message.chat.id, "❌ No channels.")

    text = "📋 CHANNELS\n\n"

    for i, ch in enumerate(db["channels"], 1):
        text += f"{i}. {ch['name']}\n{ch['chat']}\n{ch['link']}\n\n"

    bot.send_message(call.message.chat.id, text)

# =====================
# REWARD BUTTONS
# =====================

@bot.callback_query_handler(func=lambda c: c.data == "admin_add_reward")
def add_reward_btn(call):
    if not is_admin(call.from_user.id):
        return

    set_state(call.from_user.id, "add_reward")

    bot.send_message(
        call.message.chat.id,
        "🎁 Send reward now.\n\nSupport: text / photo / video / file / APK"
    )

@bot.callback_query_handler(func=lambda c: c.data == "admin_remove_reward")
def remove_reward_btn(call):
    if not is_admin(call.from_user.id):
        return

    set_state(call.from_user.id, "remove_reward")

    bot.send_message(call.message.chat.id, "Send reward ID.")

@bot.callback_query_handler(func=lambda c: c.data == "admin_list_reward")
def list_reward_btn(call):
    if not is_admin(call.from_user.id):
        return

    if not db["rewards"]:
        return bot.send_message(call.message.chat.id, "❌ No rewards.")

    text = "📦 REWARDS\n\n"

    for rid, r in db["rewards"].items():
        text += f"🆔 {rid}\nTYPE: {r['type']}\n\n"

    bot.send_message(call.message.chat.id, text)
# =====================
# STATS
# =====================

@bot.callback_query_handler(func=lambda c: c.data == "admin_stats")
def stats_btn(call):
    if not is_admin(call.from_user.id):
        return

    text = f"""📊 BOT STATS

👥 Users: {len(db["users"])}
📢 Channels: {len(db["channels"])}
🎁 Rewards: {len(db["rewards"])}
📣 Ads: {len(db["ads"])}
👑 Admins: {len(db["admins"])}

🔁 Refer: {"ON ✅" if db["settings"]["refer_on"] else "OFF ❌"}
🔐 Forward: {"ON ✅" if db["settings"]["forward_on"] else "OFF ❌"}
📣 Ads: {"ON ✅" if db["settings"]["ads_on"] else "OFF ❌"}
🗑 Auto Delete: {"ON ✅" if db["settings"]["auto_delete_on"] else "OFF ❌"}
"""

    bot.send_message(call.message.chat.id, text)

# =====================
# MULTI ADMIN
# =====================

@bot.callback_query_handler(func=lambda c: c.data == "admin_multi_admin")
def multi_admin_btn(call):
    if call.from_user.id != OWNER_ID:
        return bot.answer_callback_query(call.id, "Only owner")

    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("➕ Add Admin", callback_data="add_admin"),
        types.InlineKeyboardButton("❌ Remove Admin", callback_data="remove_admin")
    )
    kb.add(types.InlineKeyboardButton("📋 List Admin", callback_data="list_admin"))

    bot.send_message(call.message.chat.id, "👥 MULTI ADMIN", reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data == "add_admin")
def add_admin_btn(call):
    if call.from_user.id != OWNER_ID:
        return
    set_state(call.from_user.id, "add_admin")
    bot.send_message(call.message.chat.id, "Send admin numeric ID.")

@bot.callback_query_handler(func=lambda c: c.data == "remove_admin")
def remove_admin_btn(call):
    if call.from_user.id != OWNER_ID:
        return
    set_state(call.from_user.id, "remove_admin")
    bot.send_message(call.message.chat.id, "Send admin numeric ID.")

@bot.callback_query_handler(func=lambda c: c.data == "list_admin")
def list_admin_btn(call):
    if call.from_user.id != OWNER_ID:
        return

    text = "👑 ADMINS\n\n"
    for a in db["admins"]:
        text += f"• {a}\n"

    bot.send_message(call.message.chat.id, text)

# =====================
# ADS BUTTONS
# =====================

@bot.callback_query_handler(func=lambda c: c.data == "ads_add")
def ads_add_btn(call):
    if not is_admin(call.from_user.id):
        return

    set_state(call.from_user.id, "add_ads")
    bot.send_message(call.message.chat.id, "Send ads text/photo/video/file.")

@bot.callback_query_handler(func=lambda c: c.data == "ads_remove")
def ads_remove_btn(call):
    if not is_admin(call.from_user.id):
        return

    set_state(call.from_user.id, "remove_ads")
    bot.send_message(call.message.chat.id, "Send ads ID.")

@bot.callback_query_handler(func=lambda c: c.data == "ads_list")
def ads_list_btn(call):
    if not is_admin(call.from_user.id):
        return

    if not db["ads"]:
        return bot.send_message(call.message.chat.id, "❌ No ads.")

    text = "📋 ADS\n\n"
    for aid, ad in db["ads"].items():
        text += f"🆔 {aid}\nTYPE: {ad['type']}\n\n"

    bot.send_message(call.message.chat.id, text)

@bot.callback_query_handler(func=lambda c: c.data == "ads_toggle")
def ads_toggle_btn(call):
    if not is_admin(call.from_user.id):
        return

    db["settings"]["ads_on"] = not db["settings"]["ads_on"]
    save_db()

    status = "ON ✅" if db["settings"]["ads_on"] else "OFF ❌"
    bot.send_message(call.message.chat.id, f"📢 Ads: {status}")

@bot.callback_query_handler(func=lambda c: c.data == "ads_time")
def ads_time_btn(call):
    if not is_admin(call.from_user.id):
        return

    set_state(call.from_user.id, "ads_time")
    bot.send_message(call.message.chat.id, "Send ads time in minutes.")

@bot.callback_query_handler(func=lambda c: c.data == "ads_add_target")
def ads_add_target_btn(call):
    if not is_admin(call.from_user.id):
        return

    set_state(call.from_user.id, "add_ads_target")
    bot.send_message(call.message.chat.id, "Send target @username or chat ID.")

@bot.callback_query_handler(func=lambda c: c.data == "ads_remove_target")
def ads_remove_target_btn(call):
    if not is_admin(call.from_user.id):
        return

    set_state(call.from_user.id, "remove_ads_target")
    bot.send_message(call.message.chat.id, "Send target to remove.")

@bot.callback_query_handler(func=lambda c: c.data == "ads_list_target")
def ads_list_target_btn(call):
    if not is_admin(call.from_user.id):
        return

    if not db["ads_targets"]:
        return bot.send_message(call.message.chat.id, "❌ No targets.")

    text = "🎯 TARGETS\n\n"
    for t in db["ads_targets"]:
        text += f"• {t}\n"

    bot.send_message(call.message.chat.id, text)

@bot.callback_query_handler(func=lambda c: c.data == "ads_run_now")
def ads_run_now_btn(call):
    if not is_admin(call.from_user.id):
        return

    run_ads_now()
    bot.send_message(call.message.chat.id, "🚀 Ads sent.")

# =====================
# BROADCAST BUTTONS
# =====================

@bot.callback_query_handler(func=lambda c: c.data == "admin_text_broadcast")
def text_broadcast_btn(call):
    if not is_admin(call.from_user.id):
        return

    set_state(call.from_user.id, "text_broadcast")
    bot.send_message(call.message.chat.id, "Send broadcast text.")

@bot.callback_query_handler(func=lambda c: c.data == "admin_media_broadcast")
def media_broadcast_btn(call):
    if not is_admin(call.from_user.id):
        return

    set_state(call.from_user.id, "media_broadcast")
    bot.send_message(call.message.chat.id, "Send photo/video/file.")

@bot.callback_query_handler(func=lambda c: c.data == "admin_button_broadcast")
def button_broadcast_btn(call):
    if not is_admin(call.from_user.id):
        return

    set_state(call.from_user.id, "button_broadcast")
    bot.send_message(call.message.chat.id, "Send:\nMessage | Button Name | Link")

# =====================
# HELPERS
# =====================

def send_saved_item(chat_id, item):
    typ = item["type"]
    con = item["content"]
    cap = item.get("caption", "")

    if typ == "text":
        return bot.send_message(chat_id, con)
    elif typ == "photo":
        return bot.send_photo(chat_id, con, caption=cap)
    elif typ == "video":
        return bot.send_video(chat_id, con, caption=cap)
    else:
        return bot.send_document(chat_id, con, caption=cap)

def run_ads_now():
    if not db["ads"] or not db["ads_targets"]:
        return

    ad = list(db["ads"].values())[0]

    for target in db["ads_targets"]:
        try:
            send_saved_item(target, ad)
            time.sleep(0.2)
        except:
            pass

def ads_loop():
    while True:
        try:
            if db["settings"]["ads_on"]:
                run_ads_now()
            time.sleep(int(db["settings"]["ads_time"]) * 60)
        except:
            time.sleep(60)

def broadcast_item(item):
    done = 0
    fail = 0

    for uid in list(db["users"].keys()):
        try:
            send_saved_item(int(uid), item)
            done += 1
            time.sleep(0.05)
        except:
            fail += 1

    return done, fail
# =====================
# REFER BUTTONS
# =====================

@bot.callback_query_handler(func=lambda c: c.data == "admin_refer_toggle")
def refer_toggle_btn(call):
    if not is_admin(call.from_user.id):
        return

    db["settings"]["refer_on"] = not db["settings"]["refer_on"]
    save_db()

    status = "ON ✅" if db["settings"]["refer_on"] else "OFF ❌"

    bot.send_message(
        call.message.chat.id,
        f"🔁 Refer system: {status}"
    )

@bot.callback_query_handler(func=lambda c: c.data == "admin_refer_target")
def refer_target_btn(call):
    if not is_admin(call.from_user.id):
        return

    set_state(call.from_user.id, "refer_target")

    bot.send_message(call.message.chat.id, "Send refer target number.")

@bot.callback_query_handler(func=lambda c: c.data == "admin_refer_reward")
def refer_reward_btn(call):
    if not is_admin(call.from_user.id):
        return

    set_state(call.from_user.id, "refer_reward")

    bot.send_message(call.message.chat.id, "Send reward ID for refer reward.")

# =====================
# FORWARD BUTTON
# =====================

@bot.callback_query_handler(func=lambda c: c.data == "admin_forward_toggle")
def forward_toggle_btn(call):
    if not is_admin(call.from_user.id):
        return

    db["settings"]["forward_on"] = not db["settings"]["forward_on"]
    save_db()

    status = "ON ✅" if db["settings"]["forward_on"] else "OFF ❌"

    bot.send_message(
        call.message.chat.id,
        f"🔐 Forward system: {status}"
    )

# =====================
# AUTO DELETE BUTTON
# =====================

@bot.callback_query_handler(func=lambda c: c.data == "admin_auto_delete_toggle")
def auto_delete_btn(call):
    if not is_admin(call.from_user.id):
        return

    db["settings"]["auto_delete_on"] = not db["settings"]["auto_delete_on"]
    save_db()

    status = "ON ✅" if db["settings"]["auto_delete_on"] else "OFF ❌"

    bot.send_message(
        call.message.chat.id,
        f"🗑 Auto delete: {status}"
  )
  # =====================
# STATE HANDLER
# =====================

@bot.message_handler(content_types=["text", "photo", "video", "document"])
def state_handler(message):
    uid = message.from_user.id
    state = get_state(uid)

    if state and not is_admin(uid):
        return

    if not state:
        if db["settings"].get("forward_on") and not is_admin(uid):
            try:
                bot.forward_message(OWNER_ID, message.chat.id, message.message_id)
            except:
                pass
        return

    if state == "add_channel":
        try:
            name, chat, link = [x.strip() for x in message.text.split("|")]
            db["channels"].append({"name": name, "chat": chat, "link": link})
            save_db()
            clear_state(uid)
            return bot.reply_to(message, "✅ Channel added.")
        except:
            return bot.reply_to(message, "❌ Format:\nNAME | @USERNAME | LINK")

    if state == "remove_channel":
        name = message.text.strip().lower()
        old = len(db["channels"])
        db["channels"] = [c for c in db["channels"] if c["name"].lower() != name]
        save_db()
        clear_state(uid)
        return bot.reply_to(message, "✅ Removed." if len(db["channels"]) < old else "❌ Not found.")

    if state == "add_reward":
        rid = str(int(time.time()))

        if message.content_type == "text":
            db["rewards"][rid] = {"type": "text", "content": message.text}

        elif message.content_type == "photo":
            db["rewards"][rid] = {
                "type": "photo",
                "content": message.photo[-1].file_id,
                "caption": message.caption or ""
            }

        elif message.content_type == "video":
            db["rewards"][rid] = {
                "type": "video",
                "content": message.video.file_id,
                "caption": message.caption or ""
            }

        elif message.content_type == "document":
            filename = message.document.file_name or ""
            rtype = "apk" if filename.lower().endswith(".apk") else "document"
            db["rewards"][rid] = {
                "type": rtype,
                "content": message.document.file_id,
                "caption": message.caption or ""
            }

        save_db()
        clear_state(uid)
        return bot.reply_to(message, f"✅ Reward added.\nID: {rid}")

    if state == "remove_reward":
        rid = message.text.strip()
        if rid in db["rewards"]:
            del db["rewards"][rid]
            save_db()
            clear_state(uid)
            return bot.reply_to(message, "✅ Reward removed.")
        return bot.reply_to(message, "❌ Reward ID not found.")

    if state == "refer_target":
        try:
            db["settings"]["refer_target"] = int(message.text.strip())
            save_db()
            clear_state(uid)
            return bot.reply_to(message, "✅ Refer target set.")
        except:
            return bot.reply_to(message, "❌ Number bhejo.")

    if state == "refer_reward":
        rid = message.text.strip()
        if rid not in db["rewards"]:
            return bot.reply_to(message, "❌ Reward ID not found.")

        db["settings"]["refer_reward"] = rid
        save_db()
        clear_state(uid)
        return bot.reply_to(message, "✅ Refer reward set.")

    if state == "add_admin":
        try:
            aid = int(message.text.strip())
            if aid not in db["admins"]:
                db["admins"].append(aid)
            save_db()
            clear_state(uid)
            return bot.reply_to(message, "✅ Admin added.")
        except:
            return bot.reply_to(message, "❌ Numeric ID bhejo.")

    if state == "remove_admin":
        try:
            aid = int(message.text.strip())
            if aid != OWNER_ID and aid in db["admins"]:
                db["admins"].remove(aid)
            save_db()
            clear_state(uid)
            return bot.reply_to(message, "✅ Admin removed.")
        except:
            return bot.reply_to(message, "❌ Numeric ID bhejo.")

    if state == "add_ads":
        aid = str(int(time.time()))

        if message.content_type == "text":
            db["ads"][aid] = {"type": "text", "content": message.text}

        elif message.content_type == "photo":
            db["ads"][aid] = {
                "type": "photo",
                "content": message.photo[-1].file_id,
                "caption": message.caption or ""
            }

        elif message.content_type == "video":
            db["ads"][aid] = {
                "type": "video",
                "content": message.video.file_id,
                "caption": message.caption or ""
            }

        elif message.content_type == "document":
            db["ads"][aid] = {
                "type": "document",
                "content": message.document.file_id,
                "caption": message.caption or ""
            }

        save_db()
        clear_state(uid)
        return bot.reply_to(message, f"✅ Ads added.\nID: {aid}")

    if state == "remove_ads":
        aid = message.text.strip()
        if aid in db["ads"]:
            del db["ads"][aid]
            save_db()
            clear_state(uid)
            return bot.reply_to(message, "✅ Ads removed.")
        return bot.reply_to(message, "❌ Ads ID not found.")

    if state == "ads_time":
        try:
            db["settings"]["ads_time"] = int(message.text.strip())
            save_db()
            clear_state(uid)
            return bot.reply_to(message, "✅ Ads time set.")
        except:
            return bot.reply_to(message, "❌ Number bhejo.")

    if state == "add_ads_target":
        target = message.text.strip()
        if target not in db["ads_targets"]:
            db["ads_targets"].append(target)
        save_db()
        clear_state(uid)
        return bot.reply_to(message, "✅ Target added.")

    if state == "remove_ads_target":
        target = message.text.strip()
        if target in db["ads_targets"]:
            db["ads_targets"].remove(target)
        save_db()
        clear_state(uid)
        return bot.reply_to(message, "✅ Target removed.")

    if state == "text_broadcast":
        item = {"type": "text", "content": message.text}
        done, fail = broadcast_item(item)
        clear_state(uid)
        return bot.reply_to(message, f"✅ Done\nSent: {done}\nFail: {fail}")

    if state == "media_broadcast":
        item = None

        if message.content_type == "photo":
            item = {"type": "photo", "content": message.photo[-1].file_id, "caption": message.caption or ""}

        elif message.content_type == "video":
            item = {"type": "video", "content": message.video.file_id, "caption": message.caption or ""}

        elif message.content_type == "document":
            item = {"type": "document", "content": message.document.file_id, "caption": message.caption or ""}

        else:
            return bot.reply_to(message, "❌ Media bhejo.")

        done, fail = broadcast_item(item)
        clear_state(uid)
        return bot.reply_to(message, f"✅ Done\nSent: {done}\nFail: {fail}")

    if state == "button_broadcast":
        try:
            text, btn, url = [x.strip() for x in message.text.split("|")]

            kb = types.InlineKeyboardMarkup()
            kb.add(types.InlineKeyboardButton(btn, url=url))

            done = 0
            fail = 0

            for user_id in list(db["users"].keys()):
                try:
                    bot.send_message(int(user_id), text, reply_markup=kb)
                    done += 1
                    time.sleep(0.05)
                except:
                    fail += 1

            clear_state(uid)
            return bot.reply_to(message, f"✅ Done\nSent: {done}\nFail: {fail}")

        except:
            return bot.reply_to(message, "❌ Format:\nMessage | Button Name | Link")


# =====================
# RUN BOT
# =====================

def run_bot():
    threading.Thread(target=ads_loop, daemon=True).start()

    while True:
        try:
            print("Bot started...")
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception as e:
            print("Bot crashed, restarting...")
            print(e)
            traceback.print_exc()
            time.sleep(5)


if __name__ == "__main__":
    run_bot()
