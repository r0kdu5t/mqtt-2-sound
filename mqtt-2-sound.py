#!/usr/bin/python
import paho.mqtt.client as mqtt
import yaml
import pygame
import time
import os
import sys
import random

#import RPi.GPIO as GPIO

#GPIO.setmode(GPIO.BOARD)
#GPIO.setup(3, GPIO.OUT)
#GPIO.output(3, GPIO.LOW)

config_f = open('config.yaml')
config = yaml.safe_load(config_f)
config_f.close()

# set up the mixer at 44100 frequency, with 16 signed bits per sample, 1 channel, with a 2048 sample buffer
pygame.mixer.init(44100, -16, 1, 2048)

currently_playing_file = ""

def getAnnounceFile(username):
	config_FileName = "audio/" + username + "_announce.cfg"
	if(os.path.exists(config_FileName)):
		print("Config file found.")
		config_File = open(config_FileName)
		line = config_File.readline()
		selectedFile = "audio/buzzer.ogg"
		skipCount = random.randint(0, int(line) -1)
		while(skipCount):
			line = config_File.readline()
			if(len(line) > 0):
				selectedFile = line.rstrip()
			skipCount = skipCount - 1
		config_File.close()
		print("Playing " + selectedFile + "###")
		#return "audio/" + selectedFile
		return os.path.join("audio", selectedFile)
	else :
		return "audio/%s_announce.ogg" % username

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and 
    # reconnect then subscriptions will be renewed.
    #client.subscribe("hello/world")
    mqttc.subscribe("door/outer/buzzer")
    mqttc.subscribe("door/outer/opened/username")

    mqttc.subscribe("door/inner/doorbell")
    mqttc.subscribe("door/inner/opened/username")

def on_message(client, obj, msg):
    print "Received %s on topic %s" % (msg.payload, msg.topic)
    if msg.topic == 'door/inner/doorbell':
        #GPIO.output(3, GPIO.HIGH)
        os.system("ogg123 -q audio/doorbell.ogg")
        time.sleep(1)
        #GPIO.output(3, GPIO.LOW)
    elif msg.topic == 'door/outer/buzzer':
    	os.system("mpg123 -q audio/ED209_Comply.mp3")
        #play("audio/buzzer.ogg")
        #play("audio/UnFoundBug/JumpVanHalen.ogg")
        time.sleep(1)
    elif msg.topic == 'door/inner/opened/username':
        os.system("ogg123 audio/outer_door_opened.ogg")
        time.sleep(1)
        print "Person: %s has arrived." % (msg.payload)
        os.system("pico2wave -w /tmp/test.wav \"Attention, " + msg.payload + " has arrived.\"; aplay /tmp/test.wav; rm /tmp/test.wav");
    elif msg.topic == 'door/outer/opened/username':
    	# Set volume to 50% for this clip
    	play(getAnnounceFile(msg.payload), 0.5)

def play(filename, level = 1.0):
    global currently_playing_file
    print(filename)
    print(os.path.isfile(filename))
    if os.path.isfile(filename):
        if (not pygame.mixer.music.get_busy()) or (currently_playing_file is not filename):
            print "Playing %s" % filename
            currently_playing_file = filename
            pygame.mixer.music.load(filename)
            pygame.mixer.music.set_volume(level)
            pygame.mixer.music.play()


#mqttc = mosquitto.Mosquitto(config['mqtt']['name'])
mqttc = mqtt.Client(config['mqtt']['name'])
#mqttc.connect(config['mqtt']['server'], 1883, 60, True)
mqttc.connect(config['mqtt']['server'], 1883, 60)


mqttc.on_connect = on_connect
mqttc.on_message = on_message


while True:
    try:
        mqttc.loop_forever()
#   except socket.error:
#       time.sleep(5)
    except KeyboardInterrupt:
        sys.exit(0)

## EOF
# https://github.com/zanejg/pi_doorbell/blob/master/doorbell/doorbell2.py