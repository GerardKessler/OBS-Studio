# -*- coding: utf-8 -*-
# Copyright (C) 2021 Gerardo Kessler <ReaperYOtrasYerbas@gmail.com>
# This file is covered by the GNU General Public License.

import appModuleHandler
from scriptHandler import script
import api
from time import sleep
import winUser
from ui import message
import speech
from keyboardHandler import KeyboardInputGesture
from threading import Thread
import addonHandler

# Lína de traducción
addonHandler.initTranslation()

def speak(str, time):
	if hasattr(speech, "SpeechMode"):
		speech.setSpeechMode(speech.SpeechMode.off)
		sleep(time)
		speech.setSpeechMode(speech.SpeechMode.talk)
	else:
		speech.speechMode = speech.speechMode_off
		sleep(time)
		speech.speechMode = speech.speechMode_talk
	if str != None:
		sleep(0.1)
		message(str)

class AppModule(appModuleHandler.AppModule):

	def __init__(self, *args, **kwargs):
		super(AppModule, self).__init__(*args, **kwargs)
		self.fg = ""
		self.sources = ""
		self.audio = ""
		self.status = ""
		self.appsKey = KeyboardInputGesture.fromName("applications")
		self.downArrow = KeyboardInputGesture.fromName("downArrow")
		self.tab = KeyboardInputGesture.fromName("tab")
		self.firstRun()
	category = "OBS Studio"

	def firstRun(self):
		Thread(target=self.assignFunctions, daemon= True).start()

	def assignFunctions(self):
		sleep(1)
		KeyboardInputGesture.fromName("tab").send()
		self.windowObjects()

	def windowObjects(self):
		if self.sources == "":
			self.fg = api.getForegroundObject()
			for k in range(5):
				self.tab.send()
			try:
				for child in self.fg.children:
					if child.UIAAutomationId == 'OBSBasic.sourcesDock':
						self.sources = child
					elif child.UIAAutomationId == 'OBSBasic.mixerDock':
						self.audio = child
					elif child.UIAAutomationId == 'OBSBasic.statusbar':
						self.status = child
			except AttributeError:
				pass

	@script(gesture="kb:f4")
	def script_openVideosFolder(self, gesture):
		try:
			message(_('Mostrar Grabaciones'))
			sleep(0.5)
			Thread(target=speak, args=(None, 0.5), daemon= True).start()
			KeyboardInputGesture.fromName("alt+f").send()
			KeyboardInputGesture.fromName("enter").send()
			Thread(target=speak, args=(None, 0.1), daemon=True).start()
		except:
			pass

	@script(
		category=category,
		# Translators: Descripción del elemento en el diálogo gestos de entrada
		description= _('Pulsa el botón Iniciar transmisión'),
		gesture="kb:control+t"
	)
	def script_transmision(self, gesture):
		self.buttonSelect(0)

	@script(
		category=category,
		#Translators: Descripción del elemento en el diálogo gestos de entrada
		description= _('Pulsa el botón Iniciar grabación'),
		gesture="kb:control+r"
	)
	def script_grabacion(self, gesture):
		self.buttonSelect(1)

	@script(
		category=category,
		# Translators: Descripción del elemento en el diálogo gestos de entrada
		description= _('Pulsa el botón ajustes'),
		gesture="kb:control+a"
	)
	def script_ajustes(self, gesture):
		self.buttonSelect(3)

	@script(
		category=category,
		# Translators: Descripción del elemento en el diálogo gestos de entrada
		description= _('Pulsa el botón pausar grabación'),
		gesture="kb:control+p"
	)
	def script_pausar(self, gesture):
		self.buttonSelect(6)

	def buttonSelect(self, button):
		try:
			obj = self.fg.lastChild.children[0].children[button]
			message(obj.name)
			sleep(0.1)
			obj.doAction()
			Thread(target=speak, args=(None, 0.3), daemon= True).start()
		except (IndexError, AttributeError):
			pass

	@script(gestures=[f"kb:control+{i}" for i in range(1, 10)])
	def script_fuente(self, gesture):
		x = int(gesture.mainKeyName) - 1
		self.windowObjects()
		try:
			obj = self.sources.children[0].children[0].children[0].children[x]
			api.moveMouseToNVDAObject(obj)
			message(obj.name)
			sleep(0.1)
			winUser.mouse_event(winUser.MOUSEEVENTF_LEFTDOWN,0,0,None,None)
			winUser.mouse_event(winUser.MOUSEEVENTF_LEFTUP,0,0,None,None)
			Thread(target=speak, args=(None, 0.2), daemon= True).start()
		except (IndexError, AttributeError):
			# Translators: Anuncia que no hay fuentes seleccionadas
			message(_('Sin fuente asignada'))

	@script(
		category=category,
		# Translators: Descripción del elemento en el diálogo gestos de entrada
		description= _('Crea una nueva fuente'),
		gesture="kb:control+n"
	)
	def script_nuevaFuente(self, gesture):
		self.windowObjects()
		add = self.sources.firstChild.firstChild.firstChild.next.firstChild
		message(add.name)
		sleep(0.1)
		api.moveMouseToNVDAObject(add)
		winUser.mouse_event(winUser.MOUSEEVENTF_LEFTDOWN,0,0,None,None)
		winUser.mouse_event(winUser.MOUSEEVENTF_LEFTUP,0,0,None,None)
		sleep(0.1)
		self.appsKey.send()
		sleep(0.1)
		self.downArrow.send()

	@script(gestures=[f"kb:control+shift+{i}" for i in range(1, 10)])
	def script_audio(self, gesture):
		key = int(gesture.mainKeyName) - 1
		self.windowObjects()
		try:
			obj = self.audio.firstChild.firstChild.firstChild.firstChild.firstChild.children[key].firstChild
			message(obj.next.name)
			sleep(0.1)
			obj.setFocus()
			Thread(target=speak, args=(None, 0.2), daemon= True).start()
		except (AttributeError, IndexError):
			# Translators: Anuncia que no se han encontrado propiedades de audio
			message(_('Sin propiedades de audio'))

	@script(
		category=category,
		# Translators: Descripción del elemento en el diálogo gestos de entrada
		description= _('Verbaliza el tiempo  grabado'),
		gesture="kb:control+shift+r"
	)
	def script_statusRecord(self, gesture):
		self.windowObjects()
		try:
			timeRecord = self.status.children[6].name
			message(timeRecord)
		except AttributeError:
			pass

	@script(
		category=category,
		# Translators: Descripción del elemento en el diálogo gestos de entrada
		description= _('Verbaliza el tiempo transmitido'),
		gesture="kb:control+shift+t"
	)
	def script_statusTransmission(self, gesture):
		self.windowObjects()
		try:
			timeRecord = self.status.children[4].name
			message(timeRecord)
		except AttributeError:
			pass

	@script(
		category=category,
		# Translators: Descripción del elemento en el diálogo gestos de entrada
		description= _('Enfoca el panel de botones si es posible'),
		gesture="kb:control+tab"
	)
	def script_buttonsFocus(self, gesture):
		try:
			self.fg.lastChild.firstChild.firstChild.setFocus()
		except (AttributeError, IndexError):
			pass
