from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CallbackQueryHandler, MessageHandler, Filters, CommandHandler, CallbackContext
from heat5_func import tirar_screenshot_heatmap
from liq2_func import tirar_screenshot_liqmap

TELEGRAM_TOKEN = '7713411417:AAFS1SPBpxvYHxX_8X5Hx8qgEyZBlwrksks'

IGNORAR_PALAVRAS = ["CANCELAR", "PARAR", "AJUDA"]

ativo_em_espera = {}
cancelado = {}

def start(update: Update, context: CallbackContext):
    keyboard = [[InlineKeyboardButton("▶️ Iniciar consulta", callback_data='iniciar')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="🤖 Bot ativo e pronto para uso.",
                             reply_markup=reply_markup)

def exibir_botoes(update: Update, context: CallbackContext, ativo_base: str):
    keyboard = [
        [
            InlineKeyboardButton("📊 Heatmap", callback_data=f"heat_{ativo_base}"),
            InlineKeyboardButton("🌍 Liquidation Map", callback_data=f"liq_{ativo_base}"),
        ],
        [
            InlineKeyboardButton("🔁 Ver Ambos", callback_data=f"ambos_{ativo_base}"),
        ],
        [
            InlineKeyboardButton("🔄 Consultar outro ativo", callback_data="novo"),
            InlineKeyboardButton("❌ Cancelar", callback_data="cancelar"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=f"✅ Ativo recebido: *{ativo_base}*. Escolha uma das opções abaixo:",
                             parse_mode="Markdown",
                             reply_markup=reply_markup)

def enviar_finalizacao(chat_id, context):
    keyboard = [[InlineKeyboardButton("🔄 Consultar outro ativo", callback_data="novo")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=chat_id, text="✅ Processo finalizado! Deseja consultar outro ativo?", reply_markup=reply_markup)

def botao_clicado(update: Update, context: CallbackContext):
    query = update.callback_query
    try:
        query.answer()
    except Exception as e:
        print("⚠️ Erro ao responder query:", e)
        return
    chat_id = query.message.chat_id

    if query.data in ['iniciar', 'novo', 'reiniciar']:
        cancelado[chat_id] = False
        context.bot.send_message(chat_id=chat_id, text="✍️ Digite o nome do ativo (ex: BTC, ETH, SOL)...")
        return
    elif query.data == 'cancelar':
        ativo_em_espera.pop(chat_id, None)
        cancelado[chat_id] = True
        context.bot.send_message(chat_id=chat_id, text="❌ Processo cancelado. Voltando ao menu inicial...")
        start(update, context)
        return

    if '_' in query.data:
        acao, ativo_base = query.data.split('_', 1)
        if acao == "heat":
            if cancelado.get(chat_id):
                context.bot.send_message(chat_id=chat_id, text="❌ Processo cancelado. Voltando ao menu inicial...")
                start(update, context)
                return
            context.bot.send_message(chat_id=chat_id, text=f"🔄 Buscando Heatmap para *{ativo_base}*...", parse_mode="Markdown")
            tirar_screenshot_heatmap(ativo_base, "Binance", chat_id, context, cancelado)
            enviar_finalizacao(chat_id, context)
        elif acao == "liq":
            if cancelado.get(chat_id):
                context.bot.send_message(chat_id=chat_id, text="❌ Processo cancelado. Voltando ao menu inicial...")
                start(update, context)
                return
            context.bot.send_message(chat_id=chat_id, text=f"🔄 Buscando Liquidation Map para *{ativo_base}*...", parse_mode="Markdown")
            tirar_screenshot_liqmap(ativo_base, "Binance", chat_id, context, cancelado)
            enviar_finalizacao(chat_id, context)
        elif acao == "ambos":
            if cancelado.get(chat_id):
                context.bot.send_message(chat_id=chat_id, text="❌ Processo cancelado. Voltando ao menu inicial...")
                start(update, context)
                return
            context.bot.send_message(chat_id=chat_id, text=f"🔄 Buscando ambos mapas para *{ativo_base}*...", parse_mode="Markdown")
            tirar_screenshot_heatmap(ativo_base, "Binance", chat_id, context, cancelado)
            if cancelado.get(chat_id):
                context.bot.send_message(chat_id=chat_id, text="❌ Processo cancelado após primeiro mapa. Voltando ao menu inicial...")
                start(update, context)
                return
            tirar_screenshot_liqmap(ativo_base, "Binance", chat_id, context, cancelado)
            enviar_finalizacao(chat_id, context)
def receber_mensagem(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    if update.message and update.message.text:
        texto = update.message.text.strip().upper()
        if texto in IGNORAR_PALAVRAS:
            context.bot.send_message(chat_id=chat_id, text="🔕 Comando ignorado.")
            return

        if not texto.isalpha():
            context.bot.send_message(chat_id=chat_id, text="❌ Envie apenas o nome do ativo, como `ETH`, `BTC`, `SOL`...", parse_mode="Markdown")
            return

        ativo_em_espera[chat_id] = texto
        exibir_botoes(update, context, texto)

def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(botao_clicado))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, receber_mensagem))
    print("🚀 Bot unificado com botões e inteligência aprimorada pronto!")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()


# Utilitário em caso de cancelamento durante chamadas internas
def exibir_botoes_fake(update, context, ativo_base):
    keyboard = [
        [
            InlineKeyboardButton("📊 Heatmap", callback_data=f"heat_{ativo_base}"),
            InlineKeyboardButton("🌍 Liquidation Map", callback_data=f"liq_{ativo_base}"),
        ],
        [
            InlineKeyboardButton("🔁 Ver Ambos", callback_data=f"ambos_{ativo_base}"),
        ],
        [
            InlineKeyboardButton("🔄 Consultar outro ativo", callback_data="novo"),
            InlineKeyboardButton("♻️ Reiniciar tudo", callback_data="reiniciar"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=chat_id,
                             text="✅ Pronto para nova consulta.",
                             parse_mode="Markdown",
                             reply_markup=reply_markup)
