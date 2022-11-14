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
import controlTypes
import addonHandler

# Lína de traducción
addonHandler.initTranslation()

# Función para romper la cadena de verbalización y callar al sintetizador durante el tiempo especificado
def mute(time, msg= False):
	if msg:
		message(msg)
		sleep(0.1)
	Thread(target=killSpeak, args=(time,), daemon= True).start()

def killSpeak(time):
	if speech.getState().speechMode == speech.SpeechMode.off: return
	speech.setSpeechMode(speech.SpeechMode.off)
	sleep(time)
	speech.setSpeechMode(speech.SpeechMode.talk)

class AppModule(appModuleHandler.AppModule):

	category = "OBS Studio"

	def __init__(self, *args, **kwargs):
		super(AppModule, self).__init__(*args, **kwargs)
		self.fg = None
		self.controls = None
		self.sources = None
		self.audio = None
		self.status = None
		self.recordButton = None
		self.appsKey = KeyboardInputGesture.fromName("applications")
		self.downArrow = KeyboardInputGesture.fromName("downArrow")
		# Translators: Mensaje de no encontrado
		self.notFound = _('Elemento no encontrado')

	def pressControl(self, id):
		if not self.controls: self.windowObjects()
		for control in reversed(self.controls.firstChild.children):
			try:
				if control.UIAAutomationId == id:
					mute(0.5, control.name)
					control.doAction()
					if control.UIAAutomationId == 'OBSBasic.controlsDock.controlsDockContents.recordButton':
						self.recordButton = control
					return False
			except (IndexError, AttributeError):
				pass
		return True

	def windowObjects(self):
		if not self.fg:
			self.fg = api.getForegroundObject()
		for child in self.fg.children:
			try:
				if child.UIAAutomationId == 'OBSBasic.controlsDock':
					self.controls = child
				elif child.UIAAutomationId == 'OBSBasic.sourcesDock':
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
			# Translators: Mensaje de la opción mostrar ggrabaciones
			mute(0.1, _('Mostrar Grabaciones'))
			KeyboardInputGesture.fromName("alt+f").send()
			mute(0.2)
			KeyboardInputGesture.fromName("enter").send()
		except:
			pass

	@script(
		category=category,
		# Translators: Descripción del elemento en el diálogo gestos de entrada
		description= _('Pulsa el botón Iniciar transmisión'),
		gesture="kb:control+t"
	)
	def script_transmision(self, gesture):
		if self.pressControl('OBSBasic.controlsDock.controlsDockContents.streamButton'):
			message(self.notFound)

	@script(
		category=category,
		#Translators: Descripción del elemento en el diálogo gestos de entrada
		description= _('Pulsa el botón Iniciar grabación'),
		gesture="kb:control+r"
	)
	def script_grabacion(self, gesture):
		if self.pressControl('OBSBasic.controlsDock.controlsDockContents.recordButton'):
			message(self.notFound)

	@script(
		category=category,
		# Translators: Descripción del elemento en el diálogo gestos de entrada
		description= _('Pulsa el botón ajustes'),
		gesture="kb:control+a"
	)
	def script_ajustes(self, gesture):
		if self.pressControl('OBSBasic.controlsDock.controlsDockContents.settingsButton'):
			message(self.notFound)

	@script(
		category=category,
		# Translators: Descripción del elemento en el diálogo gestos de entrada
		description= _('Pulsa el botón pausar grabación'),
		gesture="kb:control+p"
	)
	def script_pausar(self, gesture):
		if not self.recordButton or controlTypes.State.CHECKED not in self.recordButton.states:
			# Translators: Mensaje sobre ninguna grabación en curso
			message(_('Ninguna grabación en curso'))
		else:
			try:
				pause_button = self.controls.firstChild.lastChild
				if pause_button.role == controlTypes.Role.CHECKBOX and pause_button.UIAAutomationId == '':
					pause_button.doAction()
					mute(0.5, pause_button.name)
				else:
					message(self.notFound)
			except:
				pass

	@script(gestures=[f"kb:control+{i}" for i in range(1, 10)])
	def script_fuente(self, gesture):
		x = int(gesture.mainKeyName) - 1
		if not self.audio: self.windowObjects()
		try:
			obj = self.sources.firstChild.firstChild.firstChild.children[x]
			api.moveMouseToNVDAObject(obj)
			mute(0.2, obj.name)
			winUser.mouse_event(winUser.MOUSEEVENTF_LEFTDOWN,0,0,None,None)
			winUser.mouse_event(winUser.MOUSEEVENTF_LEFTUP,0,0,None,None)
			mute(0.3)
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
		if not self.sources: self.windowObjects()
		add = self.sources.firstChild.firstChild.firstChild.next.firstChild
		mute(0.1, add.name)
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
		if not self.audio: self.windowObjects()
		try:
			obj = self.audio.firstChild.firstChild.firstChild.firstChild.firstChild.firstChild.children[key].firstChild
			mute(0.1, obj.next.name)
			obj.setFocus()
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
		if not self.status: self.windowObjects()
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
		if not self.status: self.windowObjects()
		try:
			timeRecord = self.status.children[4].name
			message(timeRecord)
		except AttributeError:
			pass
