import telebot
from telebot import types
from datetime import datetime, timedelta
import threading
import time
import requests

# Bot and admin configurations
API_TOKEN = '7116762784:AAGInd7ZhOC6YUIO53eFnFi72uwD5f1Fa8A'
ADMIN_ID = 6048641920  # Replace with your actual admin user ID
bot = telebot.TeleBot(API_TOKEN)

# SMM Panel API configuration
SMM_PANEL_API_KEY = "026cfadc63fe2dd1a342776c716415f9"
SMM_PANEL_API_URL = "https://your-smm-panel-api-url"  # Replace with the actual API URL

# Service IDs and quantities
SERVICES = {
    "🧡 tiktok_likes": {"id": 1111, "quantity": 1000},
    "🧡 tiktok_views": {"id": 1205, "quantity": 10000},
    "🧡 tiktok_followers": {"id": 1092, "quantity": 100},
    "✔️ instagram_likes": {"id": 101, "quantity": 500},
    "✔️ instagram_views": {"id": 78, "quantity": 1000},
    "✔️ instagram_comments": {"id": 477, "quantity": 50},
    "♛ twitter_impression": {"id": 1065, "quantity": 5000},
    "♛ telegram_impression": {"id": 1544, "quantity": 100}
}

# Data storage
user_verified = {}
user_last_submission = {}
user_requested_service = {}
user_messages = {}
user_feedback = {}
premium_users = {}
user_profiles = {}
user_points = {}
user_referrals = {}
user_referral_counts = {}
user_notifications = {}
user_languages = {}
user_affiliate_rewards = {}
scheduled_posts = {}
ads = {}
user_ad_interactions = {}
user_interactions = {}
user_behavior_responses = {}

# Admin commands to dynamically manage services and buttons
admin_services = {}
admin_buttons = []

# Helper functions
def create_main_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    buttons = [
        ("🛠 Services", "services"),
        ("🏆 My Rank", "my_rank"),
        ("🏅 Leaderboard", "leaderboard"),
        ("📩 Feedback", "feedback"),
        ("💎 Premium", "premium"),
        ("👤 Profile", "profile"),
        ("🔗 Referral Program", "referral_program"),
        ("💵 Withdraw Funds", "withdraw_funds"),
        ("🔔 Notifications", "notifications"),
        ("📣 Campaigns", "campaigns"),
        ("📝 Content Generator", "content_generator")
    ]
    # Add dynamically created buttons
    for button in admin_buttons:
        buttons.append(button)
    for i in range(0, len(buttons), 2):
        row = [types.InlineKeyboardButton(text=buttons[j][0], url=buttons[j][1] if buttons[j][1].startswith('http') else None, callback_data=buttons[j][1] if not buttons[j][1].startswith('http') else None) for j in range(i, min(i+2, len(buttons)))]
        keyboard.add(*row)
    return keyboard

def create_verification_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    verify_button = types.InlineKeyboardButton(text="✅ Verify", callback_data="verify")
    keyboard.add(verify_button)
    return keyboard

def create_service_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    service_buttons = []
    for service_name in SERVICES.keys():
        service_buttons.append((service_name.replace("_", " ").title(), service_name))
    for i in range(0, len(service_buttons), 2):
        row = [types.InlineKeyboardButton(text=service_buttons[j][0], callback_data=service_buttons[j][1]) for j in range(i, min(i+2, len(service_buttons)))]
        keyboard.add(*row)
    back_button = types.InlineKeyboardButton(text="🔙 Back", callback_data="back")
    keyboard.add(back_button)
    return keyboard

def create_back_button_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    back_button = types.InlineKeyboardButton(text="🔙 Back", callback_data="back")
    keyboard.add(back_button)
    return keyboard

def create_main_menu_button_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    main_menu_button = types.InlineKeyboardButton(text="🔙 Main Menu", callback_data="main_menu")
    keyboard.add(main_menu_button)
    return keyboard

def create_premium_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    benefits_button = types.InlineKeyboardButton(text="📈 Premium Benefits", callback_data="premium_benefits")
    cost_button = types.InlineKeyboardButton(text="💵 Premium Cost", callback_data="premium_cost")
    keyboard.add(benefits_button, cost_button)
    return keyboard

def create_notifications_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    enable_button = types.InlineKeyboardButton(text="🔔 Enable Notifications", callback_data="enable_notifications")
    disable_button = types.InlineKeyboardButton(text="🔕 Disable Notifications", callback_data="disable_notifications")
    keyboard.add(enable_button, disable_button)
    return keyboard

def create_campaigns_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    advertiser_button = types.InlineKeyboardButton(text="📢 Advertisers", callback_data="advertisers")
    user_button = types.InlineKeyboardButton(text="👥 Users", callback_data="users")
    keyboard.add(advertiser_button, user_button)
    back_button = types.InlineKeyboardButton(text="🔙 Back", callback_data="back")
    keyboard.add(back_button)
    return keyboard

def create_advertiser_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    contact_admin_button = types.InlineKeyboardButton(text="💬 Contact Admin", callback_data="contact_admin")
    keyboard.add(contact_admin_button)
    back_button = types.InlineKeyboardButton(text="🔙 Back", callback_data="campaigns")
    keyboard.add(back_button)
    return keyboard

def create_user_ads_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    for ad_id, ad in ads.items():
        ad_button = types.InlineKeyboardButton(text=ad['title'], callback_data=f"view_ad_{ad_id}")
        keyboard.add(ad_button)
    back_button = types.InlineKeyboardButton(text="🔙 Back", callback_data="campaigns")
    keyboard.add(back_button)
    return keyboard

def create_ad_interaction_keyboard(ad_id):
    keyboard = types.InlineKeyboardMarkup()
    complete_ad_button = types.InlineKeyboardButton(text="✅ Complete Ad", callback_data=f"complete_ad_{ad_id}")
    keyboard.add(complete_ad_button)
    back_button = types.InlineKeyboardButton(text="🔙 Back", callback_data="users")
    keyboard.add(back_button)
    return keyboard

def create_content_generator_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    caption_button = types.InlineKeyboardButton(text="📝 Generate Caption", callback_data="generate_caption")
    hashtag_button = types.InlineKeyboardButton(text="🔖 Generate Hashtags", callback_data="generate_hashtags")
    image_button = types.InlineKeyboardButton(text="🖼️ Generate Image", callback_data="generate_image")
    back_button = types.InlineKeyboardButton(text="🔙 Back", callback_data="back")
    keyboard.add(caption_button, hashtag_button)
    keyboard.add(image_button)
    keyboard.add(back_button)
    return keyboard

def create_manage_ads_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    for ad_id, ad in ads.items():
        ad_button = types.InlineKeyboardButton(text=f"Remove {ad['title']}", callback_data=f"remove_ad_{ad_id}")
        keyboard.add(ad_button)
    back_button = types.InlineKeyboardButton(text="🔙 Back", callback_data="admin")
    keyboard.add(back_button)
    return keyboard

# Referral link generator
def generate_referral_link(user_id):
    referral_link = f"https://t.me/your_bot_username?start={user_id}"
    if user_id not in user_referrals:
        user_referrals[user_id] = []
    user_referral_counts[user_id] = len(user_referrals[user_id])
    return referral_link

# Update user points
def update_points(user_id, points):
    if user_id not in user_points:
        user_points[user_id] = 0
    user_points[user_id] += points

# Place order on SMM panel
def place_order(service_key, link):
    service = SERVICES[service_key]
    payload = {
        "key": SMM_PANEL_API_KEY,
        "action": "add",
        "service": service["id"],
        "quantity": service["quantity"],
        "link": link
    }
    try:
        response = requests.post(SMM_PANEL_API_URL, data=payload, proxies={})
        response_data = response.json()
        if response_data.get("status") == "success":
            return f"Order placed successfully: Order ID {response_data.get('order')}"
        else:
            return f"Failed to place order: {response_data.get('error')}"
    except requests.exceptions.RequestException as e:
        return f"Error placing order: {str(e)}"

# Custom greeting and behavior-based responses
def get_custom_greeting(user_id):
    if user_id not in user_interactions:
        user_interactions[user_id] = 0
    user_interactions[user_id] += 1
    if user_interactions[user_id] == 1:
        return "👋 Welcome! We're glad to have you here. How can we assist you today?"
    elif user_interactions[user_id] < 5:
        return "👋 Welcome back! How can we assist you today?"
    else:
        return "👋 Hello again, our loyal user! What would you like to do next?"

def get_behavior_based_response(user_id):
    if user_id in user_behavior_responses:
        return user_behavior_responses[user_id]
    else:
        return "How can we assist you today?"

# Notify referrer on successful referral
def notify_referrer(referrer_id, new_user_id):
    if referrer_id in user_verified:
        bot.send_message(
            referrer_id,
            f"🎉 User {new_user_id} has joined using your referral link! You have received your reward.",
            reply_markup=create_main_menu_button_keyboard()
        )

# Notify user on service usage
def notify_service_usage(user_id, service_name, points):
    bot.send_message(
        user_id,
        f"✅ You have used the {service_name} service and earned {points} points!",
        reply_markup=create_main_menu_button_keyboard()
    )

# Notify user on campaign completion
def notify_campaign_completion(user_id, points):
    bot.send_message(
        user_id,
        f"🎉 You have completed a campaign job and earned {points} points!",
        reply_markup=create_main_menu_button_keyboard()
    )

# Command handlers
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    greeting_message = get_custom_greeting(user_id)
    if user_id not in user_verified:
        bot.send_message(
            message.chat.id,
            f"{greeting_message}\n\nPlease follow the following channels to proceed:\n\n"
            "1. [Telegram Channel](https://t.me/your_telegram_channel) 📱\n"
            "2. [WhatsApp Channel](https://wa.me/your_whatsapp_channel) 📞\n\n"
            "After following both channels, click 'Verify' to proceed.",
            parse_mode='Markdown',
            reply_markup=create_verification_keyboard()
        )
    else:
        bot.send_message(
            message.chat.id,
            greeting_message,
            reply_markup=create_main_keyboard()
        )

@bot.message_handler(commands=['admin'])
def admin_command(message):
    if message.from_user.id == ADMIN_ID:
        bot.send_message(
            message.chat.id,
            "Admin Commands:\n"
            "/admin_view_feedback - View all user feedback\n"
            "/admin_clear_data - Clear all user data\n"
            "/admin_status - Check bot status\n"
            "/admin_view_profiles - View all user profiles\n"
            "/admin_view_referrals - View referral data\n"
            "/admin_promote_user - Promote a user to premium\n"
            "/admin_view_points - View user points\n"
            "/admin_add_points - Add points to a user\n"
            "/admin_remove_points - Remove points from a user\n"
            "/admin_notify_all - Send a notification to all users\n"
            "/admin_upload_ad - Upload a new advertisement\n"
            "/admin_manage_ads - Manage (remove) advertisements\n"
            "/admin_add_service - Add a new service\n"
            "/admin_add_button - Add a new button\n"
            "/admin_remove_button - Remove a button"
        )
    else:
        bot.send_message(message.chat.id, "You are not authorized to use this command.")

@bot.message_handler(commands=['admin_add_service'])
def admin_add_service(message):
    if message.from_user.id == ADMIN_ID:
        bot.send_message(
            message.chat.id,
            "Please provide the service details in the following format:\nName | Service ID | Quantity",
            reply_markup=types.ReplyKeyboardRemove()
        )
        bot.register_next_step_handler(message, add_service_details)
    else:
        bot.send_message(message.chat.id, "You are not authorized to use this command.")

def add_service_details(message):
    try:
        name, service_id, quantity = message.text.split(" | ")
        service_key = name.lower().replace(" ", "_")
        SERVICES[service_key] = {"id": int(service_id), "quantity": int(quantity)}
        bot.send_message(message.chat.id, "Service added successfully.", reply_markup=create_main_menu_button_keyboard())
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {e}\nPlease ensure the format is correct: Name | Service ID | Quantity")

@bot.message_handler(commands=['admin_add_button'])
def admin_add_button(message):
    if message.from_user.id == ADMIN_ID:
        bot.send_message(
            message.chat.id,
            "Please provide the button details in the following format:\nText | Callback Data or URL",
            reply_markup=types.ReplyKeyboardRemove()
        )
        bot.register_next_step_handler(message, add_button_details)
    else:
        bot.send_message(message.chat.id, "You are not authorized to use this command.")

def add_button_details(message):
    try:
        text, callback_data = message.text.split(" | ")
        admin_buttons.append((text, callback_data))
        bot.send_message(message.chat.id, "Button added successfully.", reply_markup=create_main_menu_button_keyboard())
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {e}\nPlease ensure the format is correct: Text | Callback Data or URL")

@bot.message_handler(commands=['admin_remove_button'])
def admin_remove_button(message):
    if message.from_user.id == ADMIN_ID:
        bot.send_message(
            message.chat.id,
            "Please provide the button text you want to remove.",
            reply_markup=types.ReplyKeyboardRemove()
        )
        bot.register_next_step_handler(message, remove_button)
    else:
        bot.send_message(message.chat.id, "You are not authorized to use this command.")

def remove_button(message):
    try:
        text = message.text
        global admin_buttons
        admin_buttons = [button for button in admin_buttons if button[0] != text]
        bot.send_message(message.chat.id, "Button removed successfully.", reply_markup=create_main_menu_button_keyboard())
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {e}\nPlease ensure the button text is correct.")

@bot.message_handler(commands=['admin_promote_user'])
def admin_promote_user(message):
    if message.from_user.id == ADMIN_ID:
        bot.send_message(
            message.chat.id,
            "Please provide the user ID of the user you want to promote to premium.",
            reply_markup=types.ReplyKeyboardRemove()
        )
        bot.register_next_step_handler(message, promote_user_to_premium)
    else:
        bot.send_message(message.chat.id, "You are not authorized to use this command.")

def promote_user_to_premium(message):
    user_id = message.text
    if user_id.isdigit():
        user_id = int(user_id)
        premium_users[user_id] = {
            "start_date": datetime.now(),
            "end_date": datetime.now() + timedelta(days=30)
        }
        bot.send_message(
            message.chat.id,
            f"User {user_id} has been promoted to premium.",
            reply_markup=create_back_button_keyboard()
        )
        bot.send_message(
            user_id,
            "Congratulations! You have been promoted to a premium user. Enjoy the benefits!",
            reply_markup=create_main_menu_button_keyboard()
        )
    else:
        bot.send_message(message.chat.id, "Invalid user ID. Please try again.")

@bot.message_handler(commands=['admin_view_points'])
def admin_view_points(message):
    if message.from_user.id == ADMIN_ID:
        bot.send_message(
            message.chat.id,
            "Please provide the user ID of the user whose points you want to view.",
            reply_markup=types.ReplyKeyboardRemove()
        )
        bot.register_next_step_handler(message, view_user_points)

def view_user_points(message):
    user_id = message.text
    if user_id.isdigit():
        user_id = int(user_id)
        points = user_points.get(user_id, 0)
        affiliate_rewards = user_affiliate_rewards.get(user_id, 0)
        bot.send_message(
            message.chat.id,
            f"User {user_id} has {points} points and {affiliate_rewards} affiliate reward points.",
            reply_markup=create_back_button_keyboard()
        )
    else:
        bot.send_message(message.chat.id, "Invalid user ID. Please try again.")

@bot.message_handler(commands=['admin_add_points'])
def admin_add_points(message):
    if message.from_user.id == ADMIN_ID:
        bot.send_message(
            message.chat.id,
            "Please provide the user ID and the number of points to add (format: user_id points).",
            reply_markup=types.ReplyKeyboardRemove()
        )
        bot.register_next_step_handler(message, add_points)

def add_points(message):
    try:
        user_id, points = map(int, message.text.split())
        if user_id not in user_points:
            user_points[user_id] = 0
        user_points[user_id] += points
        bot.send_message(
            message.chat.id,
            f"Added {points} points to user {user_id}.",
            reply_markup=create_back_button_keyboard()
        )
    except ValueError:
        bot.send_message(message.chat.id, "Invalid format. Please provide the user ID and points separated by a space.")

@bot.message_handler(commands=['admin_remove_points'])
def admin_remove_points(message):
    if message.from_user.id == ADMIN_ID:
        bot.send_message(
            message.chat.id,
            "Please provide the user ID and the number of points to remove (format: user_id points).",
            reply_markup=types.ReplyKeyboardRemove()
        )
        bot.register_next_step_handler(message, remove_points)

def remove_points(message):
    try:
        user_id, points = map(int, message.text.split())
        if user_id in user_points:
            user_points[user_id] = max(0, user_points[user_id] - points)
            bot.send_message(
                message.chat.id,
                f"Removed {points} points from user {user_id}.",
                reply_markup=create_back_button_keyboard()
            )
        else:
            bot.send_message(message.chat.id, "User does not exist.")
    except ValueError:
        bot.send_message(message.chat.id, "Invalid format. Please provide the user ID and points separated by a space.")

@bot.message_handler(commands=['admin_view_feedback'])
def admin_view_feedback(message):
    if message.from_user.id == ADMIN_ID:
        feedback_list = "\n".join(f"{user_id}: {feedback}" for user_id, feedback in user_feedback.items())
        bot.send_message(
            message.chat.id,
            f"User Feedback:\n\n{feedback_list}" if feedback_list else "No feedback available.",
            reply_markup=create_back_button_keyboard()
        )
    else:
        bot.send_message(message.chat.id, "You are not authorized to use this command.")

@bot.message_handler(commands=['admin_clear_data'])
def admin_clear_data(message):
    if message.from_user.id == ADMIN_ID:
        user_verified.clear()
        user_last_submission.clear()
        user_requested_service.clear()
        user_messages.clear()
        user_feedback.clear()
        premium_users.clear()
        user_profiles.clear()
        user_points.clear()
        user_referrals.clear()
        user_referral_counts.clear()
        user_notifications.clear()
        user_affiliate_rewards.clear()
        scheduled_posts.clear()
        ads.clear()
        user_ad_interactions.clear()
        bot.send_message(message.chat.id, "All user data has been cleared.", reply_markup=create_back_button_keyboard())
    else:
        bot.send_message(message.chat.id, "You are not authorized to use this command.")

@bot.message_handler(commands=['admin_view_profiles'])
def admin_view_profiles(message):
    if message.from_user.id == ADMIN_ID:
        profiles_list = "\n".join(f"ID: {user_id}, Name: {user_profiles.get(user_id, 'Unknown')}, Points: {user_points.get(user_id, 0)}, Referrals: {user_referral_counts.get(user_id, 0)}, Affiliate Rewards: {user_affiliate_rewards.get(user_id, 0)}" for user_id in user_profiles)
        bot.send_message(
            message.chat.id,
            f"User Profiles:\n\n{profiles_list}" if profiles_list else "No profiles available.",
            reply_markup=create_back_button_keyboard()
        )
    else:
        bot.send_message(message.chat.id, "You are not authorized to use this command.")

@bot.message_handler(commands=['admin_view_referrals'])
def admin_view_referrals(message):
    if message.from_user.id == ADMIN_ID:
        referrals_list = "\n".join(f"ID: {user_id}, Referrals: {', '.join(map(str, user_referrals.get(user_id, [])))}" for user_id in user_referrals)
        bot.send_message(
            message.chat.id,
            f"User Referrals:\n\n{referrals_list}" if referrals_list else "No referrals available.",
            reply_markup=create_back_button_keyboard()
        )
    else:
        bot.send_message(message.chat.id, "You are not authorized to use this command.")

@bot.message_handler(commands=['admin_status'])
def admin_status(message):
    if message.from_user.id == ADMIN_ID:
        status_message = "Bot Status:\n\n"
        status_message += f"Number of verified users: {len(user_verified)}\n"
        status_message += f"Number of premium users: {len(premium_users)}\n"
        status_message += f"Number of services requested: {len(user_requested_service)}\n"
        status_message += f"Number of feedback messages: {len(user_feedback)}\n"
        status_message += f"Number of points distributed: {sum(user_points.values())}\n"
        status_message += f"Number of referrals: {sum(len(referrals) for referrals in user_referrals.values())}\n"
        bot.send_message(message.chat.id, status_message, reply_markup=create_back_button_keyboard())
    else:
        bot.send_message(message.chat.id, "You are not authorized to use this command.")

@bot.message_handler(commands=['admin_notify_all'])
def admin_notify_all(message):
    if message.from_user.id == ADMIN_ID:
        bot.send_message(
            message.chat.id,
            "Please provide the notification message you want to send to all users.",
            reply_markup=types.ReplyKeyboardRemove()
        )
        bot.register_next_step_handler(message, notify_all_users)
    else:
        bot.send_message(message.chat.id, "You are not authorized to use this command.")

def notify_all_users(message):
    notification_message = message.text
    for user_id in user_verified:
        bot.send_message(user_id, f"🔔 Notification: {notification_message}")
    bot.send_message(message.chat.id, "Notification sent to all users.", reply_markup=create_back_button_keyboard())

@bot.message_handler(commands=['admin_upload_ad'])
def admin_upload_ad(message):
    if message.from_user.id == ADMIN_ID:
        bot.send_message(
            message.chat.id,
            "Please provide the advertisement details in the following format:\nTitle | Description | Reward Points",
            reply_markup=types.ReplyKeyboardRemove()
        )
        bot.register_next_step_handler(message, upload_ad_details)
    else:
        bot.send_message(message.chat.id, "You are not authorized to use this command.")

def upload_ad_details(message):
    try:
        title, description, reward = message.text.split(" | ")
        ad_id = str(len(ads) + 1)
        ads[ad_id] = {"title": title, "description": description, "reward": int(reward)}
        bot.send_message(message.chat.id, "Advertisement uploaded successfully.", reply_markup=create_main_menu_button_keyboard())
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {e}\nPlease ensure the format is correct: Title | Description | Reward Points")

@bot.message_handler(commands=['admin_manage_ads'])
def admin_manage_ads(message):
    if message.from_user.id == ADMIN_ID:
        bot.send_message(
            message.chat.id,
            "Manage Advertisements:\nSelect an ad to remove:",
            reply_markup=create_manage_ads_keyboard()
        )
    else:
        bot.send_message(message.chat.id, "You are not authorized to use this command.")

def remove_ad(ad_id):
    if ad_id in ads:
        del ads[ad_id]

# Callback query handler
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    user_id = call.from_user.id

    if call.data == "get_started":
        if user_id not in user_verified:
            bot.send_message(
                call.message.chat.id,
                "Please follow the following channels to proceed:\n\n"
                "1. [Telegram Channel](https://t.me/your_telegram_channel) 📱\n"
                "2. [WhatsApp Channel](https://wa.me/your_whatsapp_channel) 📞\n\n"
                "After following both channels, click 'Verify' to proceed.",
                parse_mode='Markdown',
                reply_markup=create_verification_keyboard()
            )
        else:
            bot.send_message(
                call.message.chat.id,
                "Welcome back! What would you like to do?",
                reply_markup=create_main_keyboard()
            )

    elif call.data == "verify":
        if user_id not in user_verified:
            user_verified[user_id] = True
            bot.send_message(
                call.message.chat.id,
                "✅ Thank you for following the channels! You can now choose a service below.",
                reply_markup=create_main_keyboard()
            )
        else:
            bot.send_message(
                call.message.chat.id,
                "You are already verified. Please choose a service below.",
                reply_markup=create_main_keyboard()
            )

    elif call.data == "services":
        bot.send_message(
            call.message.chat.id,
            "Please choose a service:",
            reply_markup=create_service_keyboard()
        )

    elif call.data in SERVICES.keys():
        service_key = call.data
        wait_time = timedelta(hours=1) if user_id in premium_users else timedelta(hours=3)
        if user_id in user_last_submission and datetime.now() < user_last_submission[user_id] + wait_time:
            remaining_time = (user_last_submission[user_id] + wait_time - datetime.now()).total_seconds() // 60
            bot.send_message(
                call.message.chat.id,
                f"🚫 You need to wait {int(remaining_time)} minutes before you can request another service.",
                reply_markup=create_main_menu_button_keyboard()
            )
        else:
            bot.send_message(
                call.message.chat.id,
                f"Please provide the link for the {service_key.replace('_', ' ').title()} service.",
                reply_markup=create_back_button_keyboard()
            )
            bot.register_next_step_handler(call.message, lambda message: process_service_request(message, service_key))

    elif call.data == "campaigns":
        bot.send_message(
            call.message.chat.id,
            "Select an option:",
            reply_markup=create_campaigns_keyboard()
        )

    elif call.data == "advertisers":
        bot.send_message(
            call.message.chat.id,
            "Advertisers Section:\nContact admin to upload your advertisement.",
            reply_markup=create_advertiser_keyboard()
        )

    elif call.data == "contact_admin":
        bot.send_message(
            call.message.chat.id,
            "Please contact @admin to upload your advertisement."
        )

    elif call.data == "users":
        if ads:
            bot.send_message(
                call.message.chat.id,
                "User Ads Section:\nChoose an ad to view and complete:",
                reply_markup=create_user_ads_keyboard()
            )
        else:
            bot.send_message(
                call.message.chat.id,
                "No ads available currently.",
                reply_markup=create_campaigns_keyboard()
            )

    elif call.data.startswith("view_ad_"):
        ad_id = call.data.split("_")[-1]
        ad = ads.get(ad_id)
        if ad:
            bot.send_message(
                call.message.chat.id,
                f"Ad: {ad['title']}\nDescription: {ad['description']}\nReward: {ad['reward']} points",
                reply_markup=create_ad_interaction_keyboard(ad_id)
            )
        else:
            bot.send_message(
                call.message.chat.id,
                "Ad not found.",
                reply_markup=create_user_ads_keyboard()
            )

    elif call.data.startswith("complete_ad_"):
        ad_id = call.data.split("_")[-1]
        ad = ads.get(ad_id)
        if ad:
            if user_id not in user_ad_interactions:
                user_ad_interactions[user_id] = []
            if ad_id not in user_ad_interactions[user_id]:
                user_ad_interactions[user_id].append(ad_id)
                update_points(user_id, ad['reward'])
                notify_campaign_completion(user_id, ad['reward'])
                bot.send_message(
                    call.message.chat.id,
                    f"Ad completed! You have earned {ad['reward']} points.",
                    reply_markup=create_user_ads_keyboard()
                )
            else:
                bot.send_message(
                    call.message.chat.id,
                    "You have already completed this ad.",
                    reply_markup=create_user_ads_keyboard()
                )
        else:
            bot.send_message(
                call.message.chat.id,
                "Ad not found.",
                reply_markup=create_user_ads_keyboard()
            )

    elif call.data == "my_rank":
        points = user_points.get(user_id, 0)
        if points == 0:
            bot.send_message(
                call.message.chat.id,
                "You have 0 points.",
                reply_markup=create_main_menu_button_keyboard()
            )
        else:
            rank = sorted(user_points.items(), key=lambda x: x[1], reverse=True).index((user_id, points)) + 1
            bot.send_message(
                call.message.chat.id,
                f"Your current rank is #{rank}. You have {points} points.",
                reply_markup=create_main_menu_button_keyboard()
            )

    elif call.data == "leaderboard":
        leaderboard = sorted(user_points.items(), key=lambda x: x[1], reverse=True)
        leaderboard_message = "🏅 Leaderboard 🏅\n\n"
        for i, (uid, points) in enumerate(leaderboard[:10], start=1):
            user_info = bot.get_chat(uid)
            username = user_info.username or user_info.first_name
            leaderboard_message += f"{i}. {username} - {points} points\n"
        bot.send_message(
            call.message.chat.id,
            leaderboard_message,
            reply_markup=create_main_menu_button_keyboard()
        )

    elif call.data == "feedback":
        bot.send_message(
            call.message.chat.id,
            "Please provide your feedback. We value your input!",
            reply_markup=create_back_button_keyboard()
        )
        bot.register_next_step_handler(call.message, handle_feedback)

    elif call.data == "premium":
        bot.send_message(
            call.message.chat.id,
            "💎 Premium Features 💎\n\n"
            "As a premium user, you get:\n"
            "- Faster access to services\n"
            "- Higher priority for requests\n"
            "- Access to exclusive services\n\n"
            "Would you like to know more?",
            reply_markup=create_premium_keyboard()
        )

    elif call.data == "premium_benefits":
        bot.send_message(
            call.message.chat.id,
            "💎 Premium Benefits 💎\n\n"
            "- Reduced wait time between requests\n"
            "- Priority handling of service requests\n"
            "- Exclusive access to new features\n\n"
            "Enjoy these and more by becoming a premium user!",
            reply_markup=create_back_button_keyboard()
        )

    elif call.data == "premium_cost":
        bot.send_message(
            call.message.chat.id,
            "💵 Premium Cost 💵\n\n"
            "The premium subscription costs $9.99 per month.\n"
            "Contact @admin to upgrade your account.",
            reply_markup=create_back_button_keyboard()
        )

    elif call.data == "profile":
        user_name = bot.get_chat(user_id).first_name
        profile_message = f"👤 Your Profile 👤\n\n"
        profile_message += f"ID: {user_id}\n"
        profile_message += f"Name: {user_name}\n"
        profile_message += f"Total Referrals: {user_referral_counts.get(user_id, 0)}\n"
        profile_message += f"Total Points: {user_points.get(user_id, 0)}\n"
        profile_message += f"Affiliate Rewards: {user_affiliate_rewards.get(user_id, 0)}"
        bot.send_message(
            call.message.chat.id,
            profile_message,
            reply_markup=create_back_button_keyboard()
        )

    elif call.data == "referral_program":
        referral_link = generate_referral_link(user_id)
        bot.send_message(
            call.message.chat.id,
            f"🔗 Referral Program 🔗\n\n"
            "Share this referral link with your friends and earn rewards!\n\n"
            f"Your referral link: {referral_link}\n\n"
            "You can earn additional rewards for every new user who joins using your link and completes their first service request.",
            reply_markup=create_back_button_keyboard()
        )

    elif call.data == "withdraw_funds":
        bot.send_message(
            call.message.chat.id,
            "💵 Withdraw Funds 💵\n\n"
            "To withdraw funds, please contact @admin.",
            reply_markup=create_back_button_keyboard()
        )

    elif call.data == "notifications":
        bot.send_message(
            call.message.chat.id,
            "🔔 Notification Settings 🔔\n\n"
            "You can enable or disable notifications.",
            reply_markup=create_notifications_keyboard()
        )

    elif call.data == "enable_notifications":
        user_notifications[user_id] = True
        bot.send_message(
            call.message.chat.id,
            "✅ Notifications have been enabled.",
            reply_markup=create_main_menu_button_keyboard()
        )

    elif call.data == "disable_notifications":
        user_notifications[user_id] = False
        bot.send_message(
            call.message.chat.id,
            "🔕 Notifications have been disabled.",
            reply_markup=create_main_menu_button_keyboard()
        )

    elif call.data == "content_generator":
        bot.send_message(
            call.message.chat.id,
            "Choose what you would like to generate:",
            reply_markup=create_content_generator_keyboard()
        )

    elif call.data == "generate_caption":
        bot.send_message(
            call.message.chat.id,
            "Please provide some details about the content you want to create a caption for.",
            reply_markup=create_back_button_keyboard()
        )
        bot.register_next_step_handler(call.message, generate_caption)

    elif call.data == "generate_hashtags":
        bot.send_message(
            call.message.chat.id,
            "Please provide some keywords related to the content you want to create hashtags for.",
            reply_markup=create_back_button_keyboard()
        )
        bot.register_next_step_handler(call.message, generate_hashtags)

    elif call.data == "generate_image":
        bot.send_message(
            call.message.chat.id,
            "Please provide a description for the image you want to generate.",
            reply_markup=create_back_button_keyboard()
        )
        bot.register_next_step_handler(call.message, generate_image)

    elif call.data == "back":
        if user_id in user_verified:
            bot.send_message(
                call.message.chat.id,
                "What would you like to do next?",
                reply_markup=create_main_keyboard()
            )
        else:
            bot.send_message(
                call.message.chat.id,
                "Please verify yourself to access the services.",
                reply_markup=create_verification_keyboard()
            )

    elif call.data == "main_menu":
        bot.send_message(
            call.message.chat.id,
            "What would you like to do next?",
            reply_markup=create_main_keyboard()
        )

    elif call.data.startswith("remove_ad_"):
        ad_id = call.data.split("_")[-1]
        remove_ad(ad_id)
        bot.send_message(
            call.message.chat.id,
            "Advertisement removed successfully.",
            reply_markup=create_manage_ads_keyboard()
        )

# Handle service request
def process_service_request(message, service_key):
    user_id = message.from_user.id
    link = message.text
    result_message = place_order(service_key, link)
    user_last_submission[user_id] = datetime.now()
    service_name = service_key.replace('_', ' ').title()
    points = 10  # Award 10 points for placing an order
    update_points(user_id, points)
    notify_service_usage(user_id, service_name, points)
    bot.send_message(
        message.chat.id,
        f"{result_message}\n\nThank you for your submission!",
        reply_markup=create_main_menu_button_keyboard()
    )

# Handle feedback
def handle_feedback(message):
    user_id = message.from_user.id
    feedback = message.text
    user_feedback[user_id] = feedback
    bot.send_message(
        message.chat.id,
        "Thank you for your feedback!",
        reply_markup=create_main_menu_button_keyboard()
    )

# Content generation functions
def generate_caption(message):
    user_id = message.from_user.id
    content_details = message.text
    caption = f"Generated caption based on: {content_details}"
    bot.send_message(
        message.chat.id,
        f"Your generated caption: {caption}",
        reply_markup=create_main_menu_button_keyboard()
    )

def generate_hashtags(message):
    user_id = message.from_user.id
    keywords = message.text
    hashtags = f"#Generated #hashtags #based #on #keywords: {keywords}"
    bot.send_message(
        message.chat.id,
        f"Your generated hashtags: {hashtags}",
        reply_markup=create_main_menu_button_keyboard()
    )

def generate_image(message):
    user_id = message.from_user.id
    description = message.text
    image_url = f"https://dummyimage.com/600x400/000/fff&text={description.replace(' ', '+')}"
    bot.send_photo(
        message.chat.id,
        photo=image_url,
        caption="Here is your generated image.",
        reply_markup=create_main_menu_button_keyboard()
    )

# Notification thread
def send_notifications():
    while True:
        now = datetime.now()
        for user_id, enabled in user_notifications.items():
            if enabled:
                bot.send_message(
                    user_id,
                    f"🔔 Reminder: Stay engaged with our bot for more rewards! {now.strftime('%Y-%m-%d %H:%M:%S')}"
                )
        time.sleep(3600)  # Send notifications every hour

# Start notification thread
notification_thread = threading.Thread(target=send_notifications)
notification_thread.daemon = True
notification_thread.start()

# Start polling
if __name__ == '__main__':
    bot.polling(none_stop=True)
