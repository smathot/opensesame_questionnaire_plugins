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

class text_screen(item.item):

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

		self.item_type = "text_screen"
		self.description = "Presents a simple text screen"

		self.question = "Put your text here"
		self.accept_text = "Next"

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

	def run(self):

		"""Run the item"""

		# Initialize the item
		self.set_item_onset()

		# Create the app
		self.app = gui.Desktop(item=self)
		self.app.connect(gui.QUIT, self.app.quit, None)

		pad = 0 # The maximum line length, used to pad the options

		# Create an HTML document for the content
		doc = html.HTML("")
		for l in self.experiment.unsanitize(self.get("question")).split("\n"):
			doc.add(gui.Label(l))
			pad = max(pad, len(l))
			doc.br(0)

		# Create a 2-column table, start with the HTML on the first row
		c = gui.Table()
		c.tr()
		c.td(doc, align=-1)

		c.tr()
		e = gui.Button(self.get("accept_text"))
		e.connect(gui.CLICK, self.app.quit, None)		
		c.td(e, align=-1, height=32, valign=1)

		self.app.run(c)
		
		# Return success
		return True

class qttext_screen(text_screen, qtplugin.qtplugin):

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
		text_screen.__init__(self, name, experiment, string)
		qtplugin.qtplugin.__init__(self, __file__)

	def init_edit_widget(self):

		"""Build the edit controls"""

		self.lock = True

		# Pass the word on to the parent
		qtplugin.qtplugin.init_edit_widget(self, False)

		# Content editor
		self.add_line_edit_control("accept_text", "Text on next button", tooltip = "The text that appears on the next button")
		self.add_editor_control("question", "Text", tooltip = "The text")

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

