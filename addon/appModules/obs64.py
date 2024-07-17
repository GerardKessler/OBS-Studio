# -*- coding: utf-8 -*-
# Copyright (C) 2024 Gerardo Kessler <gera.ar@yahoo.com>
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
	if speech.getState().speechMode != speech.SpeechMode.talk: return
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
		for control in reversed(self.controls.firstChild.firstChild.children):
			if not hasattr(control, 'UIAAutomationId'): continue
			if control.UIAAutomationId == id:
				mute(0.5, control.name)
				control.doAction()
				return False
		return True

	def windowObjects(self):
		if not self.fg: self.fg = api.getForegroundObject()
		for child in self.fg.children:
			if not hasattr(child, 'UIAAutomationId'): continue
			if child.UIAAutomationId == 'OBSBasic.controlsDock': self.controls = child
			elif child.UIAAutomationId == 'OBSBasic.sourcesDock': self.sources = child
			elif child.UIAAutomationId == 'OBSBasic.mixerDock': self.audio = child
			elif child.UIAAutomationId == 'OBSBasic.statusbar': self.status = child

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
		if self.pressControl('OBSBasic.controlsDock.OBSBasicControls.controlsFrame.streamButton'):
			message(self.notFound)

	@script(
		category=category,
		#Translators: Descripción del elemento en el diálogo gestos de entrada
		description= _('Pulsa el botón Iniciar grabación'),
		gesture="kb:control+r"
	)
	def script_grabacion(self, gesture):
		if self.pressControl('OBSBasic.controlsDock.OBSBasicControls.controlsFrame.recordButton'):
			message(self.notFound)

	@script(
		category=category,
		# Translators: Descripción del elemento en el diálogo gestos de entrada
		description= _('Pulsa el botón ajustes'),
		gesture="kb:control+a"
	)
	def script_ajustes(self, gesture):
		if self.pressControl('OBSBasic.controlsDock.OBSBasicControls.controlsFrame.settingsButton'):
			message(self.notFound)

	@script(
		category=category,
		# Translators: Descripción del elemento en el diálogo gestos de entrada
		description= _('Pulsa el botón pausar grabación'),
		gesture="kb:control+p"
	)
	def script_pausar(self, gesture):
		if self.pressControl('OBSBasic.controlsDock.OBSBasicControls.controlsFrame.pauseRecordButton'):
			# Translators: Mensaje sobre ninguna grabación en curso
			message(_('Ninguna grabación en curso'))

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
			message(self.status.lastChild.getChild(3).lastChild.name)
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
			message(self.status.lastChild.getChild(2).lastChild.name)
		except AttributeError:
			pass
