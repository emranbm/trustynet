#!/usr/bin/env python3
"""
SafeFolks Telegram Bot

This bot records trust relationships in Telegram groups.
When added to a group, it records that the group owner trusts all other members.
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Set
from pathlib import Path

from telegram import Update, Chat
from telegram.ext import (
    Application,
    CommandHandler,
    ChatMemberHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# Import config
try:
    from config import BOT_TOKEN, DATA_FILE
except ImportError:
    print("Error: config.py not found!")
    print("Please copy config.example.py to config.py and add your bot token.")
    exit(1)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class TrustStorage:
    """Handles storage and retrieval of trust relationships."""
    
    def __init__(self, data_file: str):
        self.data_file = Path(data_file)
        self.data = self._load_data()
    
    def _load_data(self) -> Dict:
        """Load trust data from file."""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading data: {e}")
                return {"groups": {}, "trusts": []}
        return {"groups": {}, "trusts": []}
    
    def _save_data(self):
        """Save trust data to file."""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving data: {e}")
    
    def add_group(self, group_id: int, group_name: str, owner_id: int, owner_name: str):
        """Record a group with its owner."""
        group_id_str = str(group_id)
        self.data["groups"][group_id_str] = {
            "name": group_name,
            "owner_id": owner_id,
            "owner_name": owner_name,
            "added_at": datetime.now().isoformat()
        }
        self._save_data()
        logger.info(f"Added group {group_name} (ID: {group_id}) with owner {owner_name}")
    
    def add_trust(self, group_id: int, truster_id: int, truster_name: str, 
                  trustee_id: int, trustee_name: str):
        """Record a trust relationship."""
        trust_record = {
            "group_id": group_id,
            "truster_id": truster_id,
            "truster_name": truster_name,
            "trustee_id": trustee_id,
            "trustee_name": trustee_name,
            "created_at": datetime.now().isoformat()
        }
        
        # Check if trust already exists
        for trust in self.data["trusts"]:
            if (trust["group_id"] == group_id and 
                trust["truster_id"] == truster_id and 
                trust["trustee_id"] == trustee_id):
                logger.info(f"Trust already exists: {truster_name} -> {trustee_name}")
                return
        
        self.data["trusts"].append(trust_record)
        self._save_data()
        logger.info(f"Added trust: {truster_name} trusts {trustee_name} in group {group_id}")
    
    def get_group_trusts(self, group_id: int) -> List[Dict]:
        """Get all trust relationships for a group."""
        return [t for t in self.data["trusts"] if t["group_id"] == group_id]
    
    def get_user_trusts(self, user_id: int) -> List[Dict]:
        """Get all trusts where user is the truster."""
        return [t for t in self.data["trusts"] if t["truster_id"] == user_id]


# Initialize storage
storage = TrustStorage(DATA_FILE)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command."""
    await update.message.reply_text(
        "👋 Welcome to SafeFolks Bot!\n\n"
        "Add me to a group to start recording trust relationships.\n"
        "I will record that the group owner trusts all members.\n\n"
        "Commands:\n"
        "/start - Show this message\n"
        "/status - Show trust information for this group\n"
        "/help - Show help information"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /help command."""
    await update.message.reply_text(
        "🤝 SafeFolks Bot Help\n\n"
        "This bot records trust relationships in Telegram groups.\n\n"
        "How it works:\n"
        "1. Add the bot to your group\n"
        "2. The bot automatically detects the group owner\n"
        "3. The bot records that the owner trusts all group members\n"
        "4. Trust relationships are stored and can be queried\n\n"
        "Commands:\n"
        "/start - Welcome message\n"
        "/status - Show trust information\n"
        "/help - Show this help\n\n"
        "Note: Only the group owner's trust is recorded (not vice versa)."
    )


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /status command - show trust information for the group."""
    chat = update.effective_chat
    
    if chat.type == "private":
        await update.message.reply_text(
            "This command only works in groups.\n"
            "Add me to a group to see trust information."
        )
        return
    
    group_id = chat.id
    group_id_str = str(group_id)
    
    # Check if group is registered
    if group_id_str not in storage.data["groups"]:
        await update.message.reply_text(
            "⚠️ This group is not registered yet.\n"
            "Please use /scan to scan group members."
        )
        return
    
    group_info = storage.data["groups"][group_id_str]
    trusts = storage.get_group_trusts(group_id)
    
    message = (
        f"📊 Trust Status for {chat.title}\n\n"
        f"👑 Owner: {group_info['owner_name']}\n"
        f"🤝 Total Trust Relationships: {len(trusts)}\n\n"
    )
    
    if trusts:
        message += "Trust List:\n"
        for trust in trusts:
            message += f"• {trust['truster_name']} → {trust['trustee_name']}\n"
    else:
        message += "No trust relationships recorded yet.\n"
        message += "Use /scan to scan group members."
    
    await update.message.reply_text(message)


async def scan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /scan command - scan group members and record trusts."""
    chat = update.effective_chat
    user = update.effective_user
    
    if chat.type == "private":
        await update.message.reply_text(
            "This command only works in groups.\n"
            "Add me to a group first."
        )
        return
    
    try:
        # Get chat administrators to find the owner
        admins = await chat.get_administrators()
        owner = None
        
        for admin in admins:
            if admin.status == "creator":
                owner = admin.user
                break
        
        if not owner:
            await update.message.reply_text(
                "⚠️ Could not detect group owner. Please try again."
            )
            return
        
        # Get member count
        member_count = await chat.get_member_count()
        
        # Store group information
        storage.add_group(
            group_id=chat.id,
            group_name=chat.title,
            owner_id=owner.id,
            owner_name=owner.full_name
        )
        
        await update.message.reply_text(
            f"✅ Group registered!\n\n"
            f"👑 Owner: {owner.full_name}\n"
            f"👥 Members: ~{member_count}\n\n"
            f"Recording trust relationships...\n"
            f"(Owner trusts all members)"
        )
        
        # Note: We cannot easily get all members without special permissions
        # So we'll record trusts as we see members interact
        logger.info(f"Group {chat.title} scanned. Owner: {owner.full_name}")
        
    except Exception as e:
        logger.error(f"Error in scan command: {e}")
        await update.message.reply_text(
            f"❌ Error scanning group: {str(e)}\n"
            "Make sure the bot has admin privileges."
        )


async def track_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Track messages to record trust relationships."""
    chat = update.effective_chat
    user = update.effective_user
    
    # Only process group messages
    if chat.type not in ["group", "supergroup"]:
        return
    
    group_id = chat.id
    group_id_str = str(group_id)
    
    # Check if group is registered
    if group_id_str not in storage.data["groups"]:
        return
    
    group_info = storage.data["groups"][group_id_str]
    owner_id = group_info["owner_id"]
    owner_name = group_info["owner_name"]
    
    # If the message is from someone other than the owner, 
    # record that owner trusts this member
    if user.id != owner_id:
        storage.add_trust(
            group_id=group_id,
            truster_id=owner_id,
            truster_name=owner_name,
            trustee_id=user.id,
            trustee_name=user.full_name
        )


async def chat_member_updated(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Track when members join the group."""
    chat = update.effective_chat
    new_member = update.chat_member.new_chat_member
    
    # Only process group events
    if chat.type not in ["group", "supergroup"]:
        return
    
    group_id = chat.id
    group_id_str = str(group_id)
    
    # Check if group is registered
    if group_id_str not in storage.data["groups"]:
        return
    
    group_info = storage.data["groups"][group_id_str]
    owner_id = group_info["owner_id"]
    owner_name = group_info["owner_name"]
    
    # If a new member joined (not the owner), record trust
    if new_member.user.id != owner_id and new_member.status in ["member", "administrator"]:
        storage.add_trust(
            group_id=group_id,
            truster_id=owner_id,
            truster_name=owner_name,
            trustee_id=new_member.user.id,
            trustee_name=new_member.user.full_name
        )
        logger.info(f"New member {new_member.user.full_name} joined, trust recorded")


def main():
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("scan", scan_command))
    
    # Track messages to record trusts
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, track_message)
    )
    
    # Track member updates
    application.add_handler(ChatMemberHandler(chat_member_updated))
    
    # Start the bot
    logger.info("Starting SafeFolks Bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
