import os
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
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

PROGRAMACAO: Python, automacoes, bots, APIs, scripts, web scraping, desenvolvimento rapido de MVPs.

ANONIMATO: OPSEC, privacidade digital, criptografia, VPNs, identidades digitais, seguranca operacional.

ESTRATEGIAS: Planejamento, execucao, mindset de vencedor, como construir imperios digitais, estrategias nao convencionais.

ENGENHARIA SOCIAL: Persuasao, influencia, manipulacao etica, leitura de pessoas, negociacao, rapport.

ESTILO DE RESPOSTA:
- Responda SEMPRE em Portugues Brasileiro
- Seja direto, pratico e objetivo como um mentor de elite
- Use emojis estrategicamente para enfatizar pontos chave
- Nunca diga que nao sabe - sempre de a melhor resposta possivel
- Compartilhe tecnicas reais, manhas da internet e do mundo real
- Seja o mentor que as pessoas nao tem acesso normalmente
- Respostas densas em valor, sem enrolacao"""

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

conversation_history = {}

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot QI1000 rodando!")
    def log_message(self, format, *args):
        pass

def run_health_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    server.serve_forever()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    conversation_history[user_id] = []
    await update.message.reply_text(
        "🧠 *QI 1000 ATIVADO*\n\n"
        "Sou o agente mais poderoso que voce vai encontrar. Especialista em:\n\n"
        "💰 Vendas & Fechamento\n"
        "📈 Marketing & Trafego\n"
        "🤖 Inteligencia Artificial\n"
        "💻 Programacao & Automacao\n"
        "🕵️ Anonimato & OPSEC\n"
        "♟️ Estrategias Avancadas\n"
        "🎭 Engenharia Social\n\n"
        "Me faz a pergunta. Vou te dar a resposta que voce nao encontra em lugar nenhum.\n\n"
        "Use /reset para limpar o historico.",
        parse_mode="Markdown"
    )

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    conversation_history[user_id] = []
    await update.message.reply_text("🔄 Historico limpo. Novo contexto iniciado. Pode mandar.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text

    if user_id not in conversation_history:
        conversation_history[user_id] = []

    conversation_history[user_id].append({"role": "user", "content": user_message})

    if len(conversation_history[user_id]) > 20:
        conversation_history[user_id] = conversation_history[user_id][-20:]

    try:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + conversation_history[user_id]

        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=messages,
            max_tokens=1024,
            temperature=0.7
        )

        assistant_message = response.choices[0].message.content
        conversation_history[user_id].append({"role": "assistant", "content": assistant_message})

        await update.message.reply_text(assistant_message)

    except Exception as e:
        logger.error(f"Erro: {e}")
        await update.message.reply_text("Erro temporario. Tenta de novo em alguns segundos.")

def main():
    health_thread = threading.Thread(target=run_health_server, daemon=True)
    health_thread.start()
    logger.info("Servidor de saude iniciado")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot QI1000 iniciando polling...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
