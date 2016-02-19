import tgl
import pprint
from functools import partial
import requests
import time
import urllib
import random
from lxml import html

#Mi ID
our_id = 173687438
pp = pprint.PrettyPrinter(indent=4)

binlog_done = False;

def on_binlog_replay_end():
    binlog_done = True;
    
def on_get_difference_end():
    pass

def on_our_id(id):
    our_id = id
    return "Set ID: " + str(our_id)

def msg_cb(success, msg):
    pp.pprint(success)
    pp.pprint(msg)
    
HISTORY_QUERY_SIZE = 100

def history_cb(msg_list, peer, success, msgs):
  print(len(msgs))
  msg_list.extend(msgs)
  print(len(msg_list))
  if len(msgs) == HISTORY_QUERY_SIZE:
    tgl.get_history(peer, len(msg_list), HISTORY_QUERY_SIZE, partial(history_cb, msg_list, peer));


def cb(success):
    print(success)
    
def on_secret_chat_update(peer, types):
    return "on_secret_chat_update"

def on_user_update():
    pass

def on_chat_update():
    pass

def on_msg_receive(msg):
    if msg.out and not binlog_done:
         return;

    if msg.dest.id == our_id: # direct message
        peer = msg.src
    else: # chatroom
        peer = msg.dest

    pp.pprint(msg)
    
    if msg.text == "Hola":
        peer.send_msg(" Hola!")

#   Manda la info en modo texto        
    if msg.text.startswith("-m"):
        name = msg.text[3:len(msg.text)]
        peer.send_msg(get_card_text(name))

    if msg.text.startswith("-i"):
        name = msg.text[3:len(msg.text)]
        data = get_card_json(name)
        
        if len(data) == 0:
            peer.send_msg('No se han encontrado resultados')
        if len(data) == 1:
            peer.send_msg('Se ha encontrado 1 opcion')
            peer.send_msg(data[0]['name'].encode('utf-8'))
            url = data[0]['editions'][0]['image_url'].encode('utf-8')
            i = 1
            while  url.endswith('/0.jpg'):
                url = data[0]['editions'][i]['image_url'].encode('utf-8')
                i+=1
            url = url.replace('https','http')
            urllib.urlretrieve(url,'test.jpg')
            peer.send_photo ('test.jpg')

        if len(data) > 1:
            peer.send_msg('Se han encontrado {} opciones'.format(len(data)))
            for i in range (0,len(data)):
                time.sleep(0.01)
                peer.send_msg('{}.- {} '.format(i, data[i]['name'].encode('utf-8')))

# Set callbacks
tgl.set_on_binlog_replay_end(on_binlog_replay_end)
tgl.set_on_get_difference_end(on_get_difference_end)
tgl.set_on_our_id(on_our_id)
tgl.set_on_msg_receive(on_msg_receive)
tgl.set_on_secret_chat_update(on_secret_chat_update)
tgl.set_on_user_update(on_user_update)
tgl.set_on_chat_update(on_chat_update)


def get_card_text(name):

    name = name.strip()
    name = name.replace(" ","+")
    
    url = "http://api.deckbrew.com/mtg/cards?name="+name
    
    r = requests.get(url, verify=False)
    
    data = r.json()
    
    for i in range (0,len(data)):
       
       text = '\n' + data[i]['name'].encode('utf-8') + '\t' + data[i]['cost'].encode('utf-8')
       for j in range(0,len(data[i]['types'])):
           text+=(data[i]['types'][j].encode('utf-8'))
       if 'creature' in data[i]['types'] :
           text+=(data[i]['power'].encode('utf-8') + '/' + data[i]['toughness'].encode('utf-8'))
       text+=('\n' +  data[i]['text'].encode('utf-8') + '\n')
       for k in range(0,len(data[i]['editions'])):
           text+=(data[i]['editions'][k]['set'].encode('utf-8') + '\t' + data[i]['editions'][k]['rarity'].encode('utf-8'))
    
    return text
def get_card_json(name):

    name = name.strip()
    name = name.replace(" ","+")
    
    url = "http://api.deckbrew.com/mtg/cards?name="+name
    
    r = requests.get(url, verify=False)
    
    return r.json()