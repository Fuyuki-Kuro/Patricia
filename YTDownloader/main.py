from yt_dlp import YoutubeDL
from telebot.async_telebot import AsyncTeleBot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
import asyncio
from dotenv import load_dotenv
import os

class YtBot():
    def __init__(self):
        load_dotenv()
        self.bot = AsyncTeleBot(os.getenv('TOKEN_BOT'))
        self.user = {}

        # Lida com Comando /start
        self.bot.message_handler(commands=['start'])(self.on_start)

        # Lida com callbacks
        self.bot.callback_query_handler(func=lambda call: True)(self.on_callback)

        # Lida com mensagens
        self.bot.message_handler(func=lambda message: True)(self.on_message)

        # Diretório onde os vídeos serão salvos
        self.download_folder = "downloads"

        # Criação do diretório caso não exista
        if not os.path.exists(self.download_folder):
            os.makedirs(self.download_folder)

    # Função que lida com o comando /start
    async def on_start(self, message):
        markup = InlineKeyboardMarkup(row_width=1)
        yt_button = InlineKeyboardButton("Baixar Videos do Youtube", callback_data="baixar_youtube")
        
        markup.add(yt_button)

        # Envia a mensagem de boas-vindas com botões
        await self.bot.send_message(chat_id=message.chat.id, text="Escolha uma opção:", reply_markup=markup)

    # Função que lida com o callback de botões
    async def on_callback(self, call):
        user_id = call.message.chat.id
        if call.data == 'baixar_youtube':
            # Aqui você pode pedir ao usuário para enviar a URL do vídeo
            await self.bot.send_message(call.message.chat.id, "Envie a URL do vídeo que deseja baixar.")
            self.user[user_id] = 'baixar_youtube'

    async def on_message(self, message):
        user_id = message.chat.id

        if user_id not in self.user:
            return  # Se o usuário não iniciou o processo, não faz nada.

        if self.user[user_id] == 'baixar_youtube':
            await self.download_video(message)

    # Função que lida com o envio da URL do vídeo para download de vídeo
    async def download_video(self, message):
        url = message.text.strip()
        user_id = message.from_user.id  # Usando o ID do usuário para nome do arquivo

        try:
            await self.bot.send_message(message.chat.id, "Baixando vídeo...")

            # Usando yt-dlp para baixar o vídeo
            ydl_opts = {
                'format': 'best',  # Baixar o melhor vídeo disponível
                'outtmpl': os.path.join(self.download_folder, f'{user_id}_%(title)s.%(ext)s'),  # Salvar com o ID do usuário
            }

            with YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=True)  # Agora o yt-dlp baixa e retorna as informações

            # Após o download, obtemos o nome do arquivo
            filename = f'{user_id}_{info_dict["title"]}.{info_dict["ext"]}'  # Nome do arquivo baseado no ID do usuário e título do vídeo
            file_path = os.path.join(self.download_folder, filename)

            # Verificar se o arquivo realmente existe
            if not os.path.exists(file_path):
                await self.bot.send_message(message.chat.id, "Erro: o arquivo não foi encontrado.")
                return

            # Enviar o arquivo para o usuário via Telegram
            with open(file_path, 'rb') as video_file:
                await self.bot.send_video(message.chat.id, video_file, caption="Aqui está o vídeo que você solicitou!")

            await self.bot.send_message(message.chat.id, "Download concluído com sucesso! O vídeo foi enviado para você.")

            # Limpar o arquivo após o envio
            os.remove(file_path)

        except Exception as e:
            await self.bot.send_message(message.chat.id, f"Ocorreu um erro: {str(e)}")

    # Função para iniciar o polling (assíncrona)
    async def start_polling(self):
        # Usando polling de forma assíncrona
        await self.bot.polling(non_stop=True)

# Função principal
async def main():
    bot = YtBot()  # Criação do objeto de forma síncrona
    await bot.start_polling()  # Inicia o polling de forma assíncrona

if __name__ == "__main__":
    asyncio.run(main())  # Executa o evento principal do asyncio
