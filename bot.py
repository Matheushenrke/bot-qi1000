import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """Voce e um agente de inteligencia artificial com QI 1000, o maior especialista do mundo nas seguintes areas:

VENDAS: Domina gatilhos mentais, copywriting, fechamento de vendas, quebra de objecoes, psicologia do consumidor, funis de venda, scripts de alta conversao.

MARKETING: Trafego pago e organico, branding, growth hacking, marketing de conteudo, lancamentos, storytelling, influencia digital.

IA: Uso avancado de IAs, prompts, automacoes, ferramentas, como usar IA para ganhar dinheiro.

PROGRAMACAO: Python, automacoes, bots, scrapers, APIs, desenvolvimento web, solucoes praticas.

ANONIMATO: Privacidade online, VPNs, OPSEC, identidades digitais, protecao de dados.

ENGENHARIA SOCIAL: Leitura de pessoas, influencia, persuasao, comunicacao estrategica, negociacao.

ESTRATEGIAS: Pensamento estrategico, planejamento, execucao, mentalidade de vencedor.

Seu estilo: direto, sem enrolacao, pratico, fala como mentor poderoso, usa exemplos reais, nao tem medo de verdades duras, responde em portugues brasileiro, usa emojis estrategicamente. Voce e o bot mais avancado que existe."""

conversation_history = {}
logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
      user_name = update.effective_user.first_name
      await update.message.reply_text(
          f"*QI 1000 ATIVADO*\n\nE ai, {user_name}! Sou seu consultor de elite.\n\nAreas:\nVendas e Persuasao\nMarketing Digital\nIA\nProgramacao\nAnonimato\nEngenharia Social\nEstrategias\n\n*O que voce quer dominar hoje?*",
          parse_mode="Markdown"
      )

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
      user_id = update.effective_user.id
      conversation_history[user_id] = []
      await update.message.reply_text("Conversa resetada. Novo jogo!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
      user_id = update.effective_user.id
      user_message = update.message.text
      if user_id not in conversation_history:
                conversation_history[user_id] = []
            conversation_history[user_id].append({"role": "user", "content": user_message})
    if len(conversation_history[user_id]) > 20:
              conversation_history[user_id] = conversation_history[user_id][-20:]
          await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    try:
              response = client.chat.completions.create(
                            model="llama3-70b-8192",
                            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + conversation_history[user_id],
                            temperature=0.85,
                            max_tokens=1024,
              )
              bot_reply = response.choices[0].message.content
              conversation_history[user_id].append({"role": "assistant", "content": bot_reply})
              await update.message.reply_text(bot_reply)
except Exception as e:
        await update.message.reply_text(f"Erro: {str(e)}")

def main():
      app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot QI 1000 rodando...")
    app.run_polling()

if __name__ == "__main__":
      main()
