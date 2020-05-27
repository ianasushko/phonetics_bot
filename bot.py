import os
import logging
import telebot
from telebot import apihelper
apihelper.ENABLE_MIDDLEWARE = True

import cherrypy

API_TOKEN = 'my_tocken'

WEBHOOK_HOST = 'shielded-mesa-54064.herokuapp.com'
WEBHOOK_PORT = int(os.environ['PORT'])
WEBHOOK_LISTEN = '0.0.0.0'

WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/" % (API_TOKEN)

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

bot = telebot.TeleBot(API_TOKEN)

class WebhookServer(object): #сервер 
    @cherrypy.expose
    def index(self):
        if 'content-length' in cherrypy.request.headers and \
           'content-type' in cherrypy.request.headers and \
           cherrypy.request.headers['content-type'] == 'application/json':
            length = int(cherrypy.request.headers['content-length'])
            json_string = cherrypy.request.body.read(length).decode("utf-8")
            update = telebot.types.Update.de_json(json_string)
            bot.process_new_updates([update])
            return ''
        else:
            raise cherrypy.HTTPError(403)

def start_bot():
    # Remove webhook, it fails sometimes the set if there is a previous webhook
    bot.remove_webhook()

    # Set webhook
    bot.set_webhook(url=f"https://{WEBHOOK_HOST}:443" + WEBHOOK_URL_PATH)

    # Disable CherryPy requests log
    access_log = cherrypy.log.access_log
    for handler in tuple(access_log.handlers):
        access_log.removeHandler(handler)

    # Start cherrypy server
    cherrypy.config.update({
        'server.socket_host'    : WEBHOOK_LISTEN,
        'server.socket_port'    : WEBHOOK_PORT
        })

    cherrypy.quickstart(WebhookServer(), WEBHOOK_URL_PATH, {'/': {}})
