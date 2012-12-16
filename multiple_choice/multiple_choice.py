"""
This file is part of opensesame.

opensesame is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

opensesame is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with opensesame.  If not, see <http://www.gnu.org/licenses/>.
"""


from libopensesame import item, exceptions
from libqtopensesame import qtplugin
from openexp.mouse import mouse
import os.path
import math
import sys
from PyQt4 import QtGui, QtCore

path = os.path.join(os.path.dirname(os.path.split(__file__)[0]), "multiple_choice")
sys.path.append(path)
from pgu import gui, html

class multiple_choice(item.item):

	"""Basic functionality of the plug-in"""

	def __init__(self, name, experiment, string = None):

		"""
		Constructor

		Arguments:
		name -- name of the item
		experiment -- the experiment

		Keyword arguments:
		string -- definitional string (default = None)
		"""

		global path

		self.item_type = "multiple_choice"
		self.description = "Presents a multiple choice form"

		self.question = "Put your question here"
		self.choices = "Yes;Maybe;No"
		self.accept_text = "Accept"
		self.allow_multiple = "no"
		self.orientation = "vertical"
		self.accept_on_click = "no"
		self.allow_empty = "no"

		# Pass the word on to the parent
		item.item.__init__(self, name, experiment, string)

		# These lines makes sure that the icons and help file are recognized by
		# OpenSesame. Copy-paste these lines at the end of your plugin's constructor
		self.experiment.resources["%s.png" % self.item_type] = os.path.join(os.path.split(__file__)[0], "%s.png" % self.item_type)
		self.experiment.resources["%s_large.png" % self.item_type] = os.path.join(os.path.split(__file__)[0], "%s_large.png" % self.item_type)
		self.experiment.resources["%s.html" % self.item_type] = os.path.join(path, "questionnaire_plugins.html")
		self.experiment.resources["mouse_cursor.png"] = os.path.join(path, "mouse_cursor.png")

	def prepare(self):

		"""Prepare the item"""

		if self.get("mouse_backend") != "legacy" or self.get("canvas_backend") != "legacy":
			raise exceptions.runtime_error("Sorry, the questionnaire plug-ins only support the legacy back-end!")

		# Pass the word on to the parent
		item.item.prepare(self)

		#generic_response.generic_response.prepare(self)
		return True

	def set_response(self, response):

		"""
		Set the response and response_time

		Arguments:
		response -- the response
		"""

		# Sanitize unicode. Due to a bug in usanitize() we need to convert it
		# to a QString first.
		response = self.experiment.usanitize(unicode(QtCore.QString(response)))

		# The response time if based on the first selection
		if self.get("response_time") == "None":
			self.experiment.set("response_time", self.time() - self.sri)

		# If only a single response is allowed, simply set the response
		if self.get("allow_multiple") == "no":
			self.experiment.set("response", response)

		# If multiple responses are allowed, handle selection and deselection
		# by storing the response in a semicolon-separated list
		else:
			resp = str(self.get("response")).split(";")
			if resp == ["None"]:
				resp = [response]
			elif response not in resp:
				resp.append(response)
			else:
				resp.remove(response)
			if len(resp) == 0:
				resp = ["None"]
			self.experiment.set("response", ";".join(resp))

		# Optionally quit the app right away
		if self.get("accept_on_click") == "yes":
			self.app.quit()

	def run(self):

		"""Run the item"""

		# Initialize the item
		self.set_item_onset()
		self.sri = self.time()
		self.experiment.set("response", None)
		self.experiment.set("response_time", None)

		# Create the app
		self.app = gui.Desktop(item=self)
		self.app.connect(gui.QUIT, self.app.quit, None)

		# Create a list of choices
		choices = []
		for choice in self.get("choices").split(";"):
			choices.append(self.experiment.unsanitize(choice))

		pad = 0 # The maximum line length, used to pad the options

		# Create an HTML document for the content
		doc = html.HTML("")
		for l in self.experiment.unsanitize(self.get("question")).split("\n"):
			doc.add(gui.Label(l))
			pad = max(pad, len(l))
			doc.br(0)

		# Determine the colspan
		if self.get("orientation") == "vertical":
			span = 2
		else:
			span = len(choices)

		# Create a 2-column table, start with the HTML on the first row
		c = gui.Table()
		c.tr()
		c.td(doc, colspan=span, align=-1)

		# A group for the responses
		group = gui.Group()

		if self.get("orientation") == "vertical":

			# In the vertical orientation each choice is in a row
			for option in choices:
				l = gui.Label(option.ljust(pad))
				if self.get("allow_multiple") == "no":
					r = gui.Radio(group, value=option)
				else:
					r = gui.Checkbox(group, value=option)
				r.connect(gui.CLICK, self.set_response, option)
				c.tr()
				c.td(r, align=-1, width=32, height=32)
				c.td(l, align=-1, height=32)

		else:

			# In the horizontal orientation each choise is in a column
			# First a row with labels
			c.tr()
			for option in choices:
				l = gui.Label(option)
				c.td(l, align=-1, height=32)

			# Next a row with response buttons
			c.tr()
			for option in choices:
				if self.get("allow_multiple") == "no":
					r = gui.Radio(group, value=option)
				else:
					r = gui.Checkbox(group, value=option)
				r.connect(gui.CLICK, self.set_response, option)
				c.td(r, align=-1, width=32, height=32)


		# Add the accept button, if necessary
		if self.get("accept_on_click") == "no":
			c.tr()
			e = gui.Button(self.get("accept_text"))
			e.connect(gui.CLICK, self.app.quit, None)
			c.td(e, colspan=span, align=-1, height=32, valign=1)

		# Keep running the app until a response has been received
		while True:
			self.app.run(c)
			if self.get("response") != "None" or self.get("allow_empty") == "yes":
				break

		# Return success
		return True

class qtmultiple_choice(multiple_choice, qtplugin.qtplugin):

	"""The GUI aspect of the plugin"""

	def __init__(self, name, experiment, string = None):

		"""
		Constructor

		Arguments:
		name -- name of the item
		experiment -- the experiment

		Keyword arguments:
		string -- definitional string (default = None)
		"""

		# Pass the word on to the parents
		multiple_choice.__init__(self, name, experiment, string)
		qtplugin.qtplugin.__init__(self, __file__)

	def init_edit_widget(self):

		"""Build the edit controls"""

		self.lock = True

		# Pass the word on to the parent
		qtplugin.qtplugin.init_edit_widget(self, False)

		# Content editor
		self.add_line_edit_control("choices", "Available choices (separate by ';')", tooltip = "A list of possible choices")
		self.add_line_edit_control("accept_text", "Text on accept button", tooltip = "The text that appears on the accept button")
		self.add_combobox_control("allow_multiple", "Allow multiple responses", ["yes", "no"], tooltip = "Indicates whether multiple simultaneous responses are allowed")
		self.add_combobox_control("allow_empty", "Allow empty response", ["yes", "no"], tooltip = "Indicates whether an empty response is allowed")
		self.add_combobox_control("accept_on_click", "Accept on click", ["yes", "no"], tooltip = "Indicates if the answer should be accepted right away or if the accept button should be shown")
		self.add_combobox_control("orientation", "Orientation", ["horizontal", "vertical"], tooltip = "Indicates the orientation of the responses")
		self.add_editor_control("question", "Question", tooltip = "The question that you want to ask")

		self.lock = False

	def apply_edit_changes(self):

		"""Apply changes to the controls"""

		if not qtplugin.qtplugin.apply_edit_changes(self, False) or self.lock:
			return
		self.experiment.main_window.refresh(self.name)

	def edit_widget(self):

		"""Refresh the controls"""

		self.lock = True
		qtplugin.qtplugin.edit_widget(self)
		self.lock = False
		return self._edit_widget

