import os
import socket

import clipboard
import keyboard
from flask import Flask, request
from flask_admin import Admin
from peewee import DoesNotExist

from model_views import CommomView
from models import Command, Clipbullet
from settings import *


app = Flask(__name__)
app.config.from_object(__name__)
admin = Admin(app, name='remote-commands', template_mode='bootstrap3')

# Adiciona as views na tela de Admin:
admin.add_view(CommomView(Command))
admin.add_view(CommomView(Clipbullet))

# Definição de endpoints da aplicação Flask
@app.route('/shortcut', methods=['POST'])
def shortcut():
    """
    Recebe um json que deve conter a chave 'command', com o nome de um atalho
    a ser executado.
    Atalhos válidos até o momento:
    - minimize_all: windows + d
    """
    data = request.get_json()
    if not data.get('command', False):
        return {
            "success": False,
            "message": "send command name in 'command' field"
        }
    if data.get('command') == 'minimize_all':
        keyboard.press_and_release('windows+d')
    elif data.get('command') == 'mute_unmute_meet':
        keyboard.press_and_release('ctrl+d')
    else:
        return {"success": False, "message": "command not found"}
    return {"success": True}

@app.route('/command/<int:command_index>', methods=['POST'])
def exec_command(command_index):
    """
    Executa um comando no terminal. O comando deve ser previamente cadastrado
    na tela de admin do Flask.
    Informar na URL o index do comando a ser executado.
    """
    try:
        to_exec = Command.get(index=command_index)
        command = to_exec.command
    except DoesNotExist:
        return {
            "success": False,
            "message": f"Nenhum comando cadastrado com index {command_index}"
        }

    # Executa o comando
    output = os.system(command)
    # output = subprocess.check_output(to_exec.command)

    if output == 0:
        return {"command": command, "success": True}
    else:
        return {"command": command, "success": False}

@app.route('/clipbullet/<int:paste_index>', methods=['POST'])
def load_clipbullet(paste_index):
    """
    Carrega um texto para o clipboard (famoso ctrl+v). O texto deve ser
    previamente cadatrado na tela de admin do Flask.
    Informar na URL o index do texto a ser copiado.
    """
    try:
        to_copy = Clipbullet.get(index=paste_index)
        clipboard.copy(to_copy.text)
    except DoesNotExist:
        return {
            "success": False,
            "message": f"Nenhum texto cadastrado com index {paste_index}"
        }
    return {"success": True}


if __name__ == '__main__':
    Command.create_table()
    Clipbullet.create_table()
    # Obter o IP local da máquina, apenas para exibição
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 1))
    local_ip = s.getsockname()[0]
    print(f"* Rodando app em {local_ip}")
    print(f"* Adicione comandos em http://{local_ip}:5000/admin")
    app.run(host='0.0.0.0')
