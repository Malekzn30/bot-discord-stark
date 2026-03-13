# Commandes manquantes à ajouter dans bot.py

@bot.command()
@commands.is_owner()
async def autoreact(ctx, channel: nextcord.TextChannel = None, *emojis):
    """Configure les réactions automatiques pour un salon"""
    if not channel:
        channel = ctx.channel
    
    if not emojis:
        # Afficher la configuration actuelle
        channel_id_str = str(channel.id)
        
        if channel_id_str in config.AUTO_REACT_CHANNELS:
            current_emojis = config.AUTO_REACT_CHANNELS[channel_id_str]
            embed = nextcord.Embed(
                title="🔄 Réactions Automatiques",
                description=f"**Salon:** {channel.mention}",
                color=0x3498db
            )
            
            emoji_text = " ".join(current_emojis)
            embed.add_field(name="😊 Emojis actuels", value=emoji_text, inline=False)
            embed.add_field(
                name="📝 Comment modifier",
                value="`+autoreact #salon 😂 ❤️ 👍` pour définir de nouveaux emojis",
                inline=False
            )
            
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"❌ Aucune réaction automatique configurée pour {channel.mention}")
        return
    
    # Configurer les réactions automatiques
    channel_id_str = str(channel.id)
    config.AUTO_REACT_CHANNELS[channel_id_str] = list(emojis)
    
    embed = nextcord.Embed(
        title="✅ Réactions Automatiques Configurées",
        description=f"**Salon:** {channel.mention}",
        color=0x2ecc71
    )
    
    emoji_text = " ".join(emojis)
    embed.add_field(name="😊 Emojis configurés", value=emoji_text, inline=False)
    embed.add_field(
        name="📝 Utilisation",
        value=f"Le bot réagira avec ces emojis à tous les messages dans {channel.mention}",
        inline=False
    )
    
    await ctx.send(embed=embed)
    
    # Sauvegarder dans un fichier pour persistance
    try:
        import json
        os.makedirs("data", exist_ok=True)
        with open("data/auto_react_config.json", "w") as f:
            json.dump(config.AUTO_REACT_CHANNELS, f, indent=2)
        print(f"[AUTO_REACT] Configuration sauvegardée pour {channel.id}")
    except Exception as e:
        print(f"[AUTO_REACT] Erreur sauvegarde: {e}")

@bot.command()
@commands.is_owner()
async def stopautoreact(ctx, channel: nextcord.TextChannel = None):
    """Arrête les réactions automatiques pour un salon"""
    if not channel:
        channel = ctx.channel
    
    channel_id_str = str(channel.id)
    
    if channel_id_str in config.AUTO_REACT_CHANNELS:
        del config.AUTO_REACT_CHANNELS[channel_id_str]
        
        embed = nextcord.Embed(
            title="🛑 Réactions Automatiques Arrêtées",
            description=f"**Salon:** {channel.mention}",
            color=0xe74c3c
        )
        
        embed.add_field(
            name="📝 Action",
            value="Le bot ne réagira plus automatiquement dans ce salon",
            inline=False
        )
        
        await ctx.send(embed=embed)
        
        # Sauvegarder la modification
        try:
            import json
            os.makedirs("data", exist_ok=True)
            with open("data/auto_react_config.json", "w") as f:
                json.dump(config.AUTO_REACT_CHANNELS, f, indent=2)
            print(f"[AUTO_REACT] Configuration supprimée pour {channel.id}")
        except Exception as e:
            print(f"[AUTO_REACT] Erreur sauvegarde: {e}")
    else:
        await ctx.send(f"❌ Aucune réaction automatique n'était configurée pour {channel.mention}")

@bot.command()
@commands.is_owner()
async def setactivity(ctx, *, activity: str = None):
    """Définit l'activité du bot"""
    if not activity:
        await ctx.send("❌ Spécifie une activité: `+setactivity Joue à Minecraft`")
        return
    
    try:
        await bot.change_presence(activity=nextcord.Game(name=activity))
        await ctx.send(f"✅ Activité définie: **{activity}**")
    except Exception as e:
        await ctx.send(f"❌ Erreur: {e}")

@bot.command()
@commands.is_owner()
async def setstatus(ctx, status: str = None):
    """Définit le statut du bot"""
    if not status:
        await ctx.send("❌ Spécifie un statut: `+setstatus idle/dnd/online`")
        return
    
    status_map = {
        "online": nextcord.Status.online,
        "idle": nextcord.Status.idle,
        "dnd": nextcord.Status.dnd,
        "invisible": nextcord.Status.invisible
    }
    
    if status.lower() not in status_map:
        await ctx.send("❌ Statut invalide. Utilise: `online`, `idle`, `dnd`, `invisible`")
        return
    
    try:
        await bot.change_presence(status=status_map[status.lower()])
        await ctx.send(f"✅ Statut défini: **{status.lower()}**")
    except Exception as e:
        await ctx.send(f"❌ Erreur: {e}")
