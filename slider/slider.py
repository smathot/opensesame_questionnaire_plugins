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
from openexp.canvas import canvas
from openexp.mouse import mouse
import os.path
import math
import sys
from PyQt4 import QtGui, QtCore

path = os.path.join(os.path.dirname(os.path.split(__file__)[0]), "multiple_choice")
sys.path.append(path)
from pgu import gui, html

class slider(item.item):

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

		self.item_type = "slider"
		self.description = "Presents a question and slider"

		self.question = "Put your question here"
		self.accept_text = "Click to accept"
		self.slider_width = 800
		self.slider_heigth = 10
		self.txt_colour = 'white'
		self.sf_colour = 'red'
		self.fg_colour = 'white'
		self.bg_colour = 'black'

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
		self.sri = self.time()
		self.experiment.set("slider_percent", None)
		my_canvas = canvas(self.experiment)
		my_mouse = mouse(self.experiment, timeout=20)


		# Create the app
		while True:

			# Slider dimensions
			slider_w = self.slider_width
			slider_h = self.slider_heigth
			slider_x = self.get("width")/2-slider_w/2
			slider_y = self.get("height")/2-slider_h/2
			
			# Determine the slider fill based on the mouse position
			pos, time = my_mouse.get_pos()
			x, y = pos
			slider_fill = min(slider_w, max(0, x-slider_x))

			my_canvas.set_bgcolor(self.get("bg_colour"))
			my_canvas.clear()
			# Draw the text 
			my_canvas.text(self.get("question"), y=slider_y-100, color=self.get("txt_colour"))
			my_canvas.text(self.get("accept_text"), y=slider_y+slider_h+50, color=self.get("txt_colour"))
			# Draw the slider frame
			my_canvas.set_fgcolor(self.get("fg_colour"))
			my_canvas.rect(slider_x-1, slider_y-1, slider_w+2, slider_h+2)
			# Draw the slider fill
			my_canvas.rect(slider_x, slider_y, slider_fill, slider_h, fill=True, color=self.get("sf_colour"))
			# Draw the canvas
			my_canvas.show()

			# Poll the mouse for buttonclicks
			button, position, timestamp = my_mouse.get_click(timeout = 20)
			if button != None:
				break

			slider_percent = 100.0*slider_fill/slider_w

		# Set the response and response time
		self.experiment.set("slider_percent", slider_percent)

		# Return success
		return True

class qtslider(slider, qtplugin.qtplugin):

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
		slider.__init__(self, name, experiment, string)
		qtplugin.qtplugin.__init__(self, __file__)

	def init_edit_widget(self):

		"""Build the edit controls"""

		self.lock = True

		# Pass the word on to the parent
		qtplugin.qtplugin.init_edit_widget(self, False)

		# Content editor
		self.add_spinbox_control("slider_width", "Slider width", 10, 1000, tooltip = "The width of the text area")
		self.add_spinbox_control("slider_heigth", "Slider height", 0, 100, tooltip = "The height of the text area")		
		self.add_color_edit_control("txt_colour", "Text colour", tooltip = "Expecting a colorname (e.g., 'blue') or an HTML color (e.g., '#0000FF')")
		self.add_color_edit_control("fg_colour", "Foreground colour", tooltip = "Expecting a colorname (e.g., 'blue') or an HTML color (e.g., '#0000FF')")
		self.add_color_edit_control("sf_colour", "Slider filling colour", tooltip = "Expecting a colorname (e.g., 'blue') or an HTML color (e.g., '#0000FF')")
		self.add_color_edit_control("bg_colour", "Background colour", tooltip = "Expecting a colorname (e.g., 'blue') or an HTML color (e.g., '#0000FF')")
		self.add_line_edit_control("accept_text", "Text underneath the slider", tooltip = "The text that appears below slider")
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

