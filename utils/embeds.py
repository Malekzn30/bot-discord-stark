import nextcord

def create_embed(title="", description="", color=0x3498db, timestamp=None, guild=None, bot=None):
    """Créer un embed avec le design standard du bot"""
    
    embed = nextcord.Embed(
        title=title,
        description=description,
        color=color,
        timestamp=timestamp
    )
    
    # Icône du serveur comme thumbnail principale
    if guild and guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    
    # Auteur avec le nom du bot et sa PP
    if bot:
        embed.set_author(
            name="𝐒𝐭𝐚𝐫𝐊𝟗𝟐☆🇵🇸",
            icon_url=bot.user.display_avatar.url if bot.user.avatar else None
        )
        
        # Footer standard
        embed.set_footer(
            text="made by 𝐒𝐭𝐚𝐫𝐊𝟗𝟐☆🇵🇸",
            icon_url=bot.user.display_avatar.url if bot.user.avatar else None
        )
    
    return embed

def create_success_embed(title="", description="", guild=None, bot=None):
    """Créer un embed de succès (vert)"""
    return create_embed(
        title=f"✅ {title}",
        description=description,
        color=0x2ecc71,
        guild=guild,
        bot=bot
    )

def create_error_embed(title="", description="", guild=None, bot=None):
    """Créer un embed d'erreur (rouge)"""
    return create_embed(
        title=f"❌ {title}",
        description=description,
        color=0xff6b6b,
        guild=guild,
        bot=bot
    )

def create_warn_embed(title="", description="", guild=None, bot=None):
    """Créer un embed de warn (orange)"""
    return create_embed(
        title=f"⚠️ {title}",
        description=description,
        color=0xff6b6b,
        guild=guild,
        bot=bot
    )

def create_info_embed(title="", description="", guild=None, bot=None):
    """Créer un embed d'information (bleu)"""
    return create_embed(
        title=f"ℹ️ {title}",
        description=description,
        color=0x3498db,
        guild=guild,
        bot=bot
    )
