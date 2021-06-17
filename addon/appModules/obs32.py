# -*- coding: utf-8 -*-
# Copyright (C) 2021 Gerardo Kessler <ReaperYOtrasYerbas@gmail.com>
# This file is covered by the GNU General Public License.

import appModuleHandler
from scriptHandler import script
import api
import controlTypes
from time import sleep
import winUser
from ui import message as msg
import speech
from keyboardHandler import KeyboardInputGesture
from threading import Thread

class AppModule(appModuleHandler.AppModule):

	appsKey = KeyboardInputGesture.fromName("applications")
	downArrow = KeyboardInputGesture.fromName("downArrow")

	@script(
category="OBS Studio",
description="Pulsa el botón Iniciar transmisión",
gesture="kb:control+t"
)
	def script_transmision(self, gesture):
		self. buttonSelect(0)

	@script(
category="OBS Studio",
description="Pulsa el botón Iniciar grabación",
gesture="kb:control+r"
)
	def script_grabacion(self, gesture):
		self. buttonSelect(1)

	@script(
category="OBS Studio",
description="Pulsa el botón ajustes",
gesture="kb:control+a"
)
	def script_ajustes(self, gesture):
		self. buttonSelect(3)

	@script(
category="OBS Studio",
description="Pulsa el botón pausar grabación",
gesture="kb:control+p"
)
	def script_pausar(self, gesture):
		self. buttonSelect(6)

	def buttonSelect(self, button):
		fg = api.getForegroundObject()
		obj = fg.lastChild.children[0].children[button]
		obj.doAction()
		Thread(target=self.mute, args=(obj.name,)).start()

	@script(
		category="OBS Studio",
		description="Selecciona la fuente según su órden  de posición",
		gestures=[f"kb:{i}" for i in range(0, 10)]
	)
	def script_fuente(self, gesture):
		x = int(gesture.mainKeyName) - 1
		fg = api.getForegroundObject()
		for child in fg.children:
			if child.UIAAutomationId == 'OBSBasic.sourcesDock':
				fuentesWindow = child
				break
		try:
			obj = fuentesWindow.children[0].children[0].children[0].children[x]
			api.moveMouseToNVDAObject(obj)
			winUser.mouse_event(winUser.MOUSEEVENTF_LEFTDOWN,0,0,None,None)
			winUser.mouse_event(winUser.MOUSEEVENTF_LEFTUP,0,0,None,None)
			Thread(target=self.mute, args=(obj.name,)).start()
		except IndexError:
			msg("Sin fuente asignada")

	@script(
		category="OBS Studio",
		description="Crea una nueva fuente",
		gesture="kb:control+n"
	)
	def script_nuevaFuente(self, gesture):
		fg = api.getForegroundObject()
		for child in fg.children:
			if child.UIAAutomationId == 'OBSBasic.sourcesDock':
				fuentesWindow = child
				break
		add = fuentesWindow.firstChild.firstChild.firstChild.next.firstChild
		api.moveMouseToNVDAObject(add)
		winUser.mouse_event(winUser.MOUSEEVENTF_LEFTDOWN,0,0,None,None)
		winUser.mouse_event(winUser.MOUSEEVENTF_LEFTUP,0,0,None,None)
		sleep(0.1)
		self.appsKey.send()
		sleep(0.1)
		self.downArrow.send()

	@script(
		category="OBS Studio",
		description="Enfoca la fuente de audio según su número de órden",
		gestures=[f"kb:control+{i}" for i in range(0, 10)]
	)
	def script_audio(self, gesture):
		key = int(gesture.mainKeyName) - 1
		fg = api.getForegroundObject()
		for child in fg.children:
			if child.UIAAutomationId == 'OBSBasic.mixerDock':
				audioWindow = child
				break
		try:
			obj = audioWindow.firstChild.firstChild.firstChild.firstChild.firstChild.children[key].firstChild
			obj.setFocus()
			Thread(target=self.mute, args=(obj.next.name,)).start()
		except IndexError:
			msg("Sin propiedades de audio")

	def mute(self, str):
		speech.speechMode = speech.speechMode_off
		sleep(0.1)
		speech.speechMode = speech.speechMode_talk
		msg(str)

	@script(
		category="OBS Studio",
		description="Informa el tiempo  grabado",
		gesture="kb:control+shift+r"
	)
	def script_statusRecord(self, gesture):
		fg = api.getForegroundObject()
		for child in fg.children:
			if child.UIAAutomationId == 'OBSBasic.statusbar':
				estadoWindow = child
				break
		timeRecord = estadoWindow.children[6].name
		msg(timeRecord)

	@script(
		category="OBS Studio",
		description="Informa el tiempo transmitido",
		gesture="kb:control+shift+t"
	)
	def script_statusTransmission(self, gesture):
		fg = api.getForegroundObject()
		for child in fg.children:
			if child.UIAAutomationId == 'OBSBasic.statusbar':
				estadoWindow = child
				break
		timeRecord = estadoWindow.children[4].name
		msg(timeRecord)
