# -*- coding: utf-8 -*-
# Copyright (C) 2021 Gerardo Kessler <ReaperYOtrasYerbas@gmail.com>
# This file is covered by the GNU General Public License.

import appModuleHandler
from scriptHandler import script
import api
import controlTypes
from time import sleep
import winUser
from ui import message
import speech
from keyboardHandler import KeyboardInputGesture
from threading import Thread
import addonHandler

# Lína de traducción
addonHandler.initTranslation()

class AppModule(appModuleHandler.AppModule):

	fg = ""
	sources = ""
	audio = ""
	status = ""
	appsKey = KeyboardInputGesture.fromName("applications")
	downArrow = KeyboardInputGesture.fromName("downArrow")
	tab = KeyboardInputGesture.fromName("tab")

	def event_NVDAObject_init(self, obj):
		self.fg = api.getForegroundObject()

	def windowObjects(self):
		if self.sources == "":
			self.tab.send()
			for child in self.fg.children:
				if child.UIAAutomationId == 'OBSBasic.sourcesDock':
					self.sources = child
				elif child.UIAAutomationId == 'OBSBasic.mixerDock':
					self.audio = child
				elif child.UIAAutomationId == 'OBSBasic.statusbar':
					self.status = child

	@script(
		category="OBS Studio",
		# Translators: Descripción del elemento en el diálogo gestos de entrada
		description= _('Pulsa el botón Iniciar transmisión'),
		gesture="kb:control+t"
	)
	def script_transmision(self, gesture):
		self. buttonSelect(0)

	@script(
		category="OBS Studio",
		#Translators: Descripción del elemento en el diálogo gestos de entrada
		description= _('Pulsa el botón Iniciar grabación'),
		gesture="kb:control+r"
	)
	def script_grabacion(self, gesture):
		self. buttonSelect(1)

	@script(
		category="OBS Studio",
		# Translators: Descripción del elemento en el diálogo gestos de entrada
		description= _('Pulsa el botón ajustes'),
		gesture="kb:control+a"
	)
	def script_ajustes(self, gesture):
		self. buttonSelect(3)

	@script(
		category="OBS Studio",
		# Translators: Descripción del elemento en el diálogo gestos de entrada
		description= _('Pulsa el botón pausar grabación'),
		gesture="kb:control+p"
	)
	def script_pausar(self, gesture):
		self. buttonSelect(6)

	def buttonSelect(self, button):
		try:
			obj = self.fg.lastChild.children[0].children[button]
			obj.doAction()
			Thread(target=self.mute, args=(obj.name,)).start()
		except (IndexError, AttributeError):
			pass

	@script(
		category="OBS Studio",
		# Translators: Descripción del elemento en el diálogo gestos de entrada
		description= _('Selecciona la fuente según su órden  de posición'),
		gestures=[f"kb:control+{i}" for i in range(0, 10)]
	)
	def script_fuente(self, gesture):
		x = int(gesture.mainKeyName) - 1
		self.windowObjects()
		try:
			obj = self.sources.children[0].children[0].children[0].children[x]
			api.moveMouseToNVDAObject(obj)
			winUser.mouse_event(winUser.MOUSEEVENTF_LEFTDOWN,0,0,None,None)
			winUser.mouse_event(winUser.MOUSEEVENTF_LEFTUP,0,0,None,None)
			Thread(target=self.mute, args=(obj.name,)).start()
		except IndexError:
			# Translators: Anuncia que no hay fuentes seleccionadas
			message(_('Sin fuente asignada'))

	@script(
		category="OBS Studio",
		# Translators: Descripción del elemento en el diálogo gestos de entrada
		description= _('Crea una nueva fuente'),
		gesture="kb:control+n"
	)
	def script_nuevaFuente(self, gesture):
		self.windowObjects()
		add = self.sources.firstChild.firstChild.firstChild.next.firstChild
		api.moveMouseToNVDAObject(add)
		winUser.mouse_event(winUser.MOUSEEVENTF_LEFTDOWN,0,0,None,None)
		winUser.mouse_event(winUser.MOUSEEVENTF_LEFTUP,0,0,None,None)
		sleep(0.1)
		self.appsKey.send()
		sleep(0.1)
		self.downArrow.send()

	@script(
		category="OBS Studio",
		# Translators: Descripción del elemento en el diálogo gestos de entrada
		description= _('Enfoca la fuente de audio según su número de órden'),
		gestures=[f"kb:control+shift+{i}" for i in range(0, 10)]
	)
	def script_audio(self, gesture):
		key = int(gesture.mainKeyName) - 1
		self.windowObjects()
		try:
			obj = self.audio.firstChild.firstChild.firstChild.firstChild.firstChild.children[key].firstChild
			obj.setFocus()
			Thread(target=self.mute, args=(obj.next.name,)).start()
		except (AttributeError, IndexError):
			# Translators: Anuncia que no se han encontrado propiedades de audio
			message(_('Sin propiedades de audio'))

	def mute(self, str):
		speech.speechMode = speech.speechMode_off
		sleep(0.1)
		speech.speechMode = speech.speechMode_talk
		message(str)

	@script(
		category="OBS Studio",
		# Translators: Descripción del elemento en el diálogo gestos de entrada
		description= _('Verbaliza el tiempo  grabado'),
		gesture="kb:control+shift+r"
	)
	def script_statusRecord(self, gesture):
		self.windowObjects()
		timeRecord = self.status.children[6].name
		message(timeRecord)

	@script(
		category="OBS Studio",
		# Translators: Descripción del elemento en el diálogo gestos de entrada
		description= _('Verbaliza el tiempo transmitido'),
		gesture="kb:control+shift+t"
	)
	def script_statusTransmission(self, gesture):
		self.windowObjects()
		timeRecord = self.status.children[4].name
		message(timeRecord)

	@script(
		category="OBS Studio",
		# Translators: Descripción del elemento en el diálogo gestos de entrada
		description= _('Enfoca el panel de botones'),
		gesture="kb:control+tab"
	)
	def script_buttonsFocus(self, gesture):
		try:
			self.fg.lastChild.firstChild.firstChild.setFocus()
		except AttributeError:
			pass
