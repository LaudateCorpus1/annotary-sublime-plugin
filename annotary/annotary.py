import sublime
import sublime_plugin
from sublime import Region
import _thread
import os
from json import loads
from subprocess import Popen, PIPE
from cgi import escape
import re
from os.path import join



# region.redish region.orangish region.yellowish region.bluish region.greenish 

ANNOTATION_KEYS = ["ano_key_1", "ano_key_2", "ano_key_3", "ano_key_4", "ano_key_5", "ano_key_6"]
VIOLATION_KEYS = ["vio_key_1", "vio_key_2", "vio_key_3", "vio_key_4", "vio_key_5", "vio_key_6"]

# Map regions to popup messages
annotation_glob = {}
violation_glob = {}

text_command_point = None
def show_error_message(view, msg):
	view.show_popup("<h3 style='color:red;'>" + msg + "</h3>", sublime.HIDE_ON_MOUSE_MOVE_AWAY, text_command_point, max_width=600, max_height=100)

def replace_regex_with_whitespace(regex, code):
    matches = re.finditer(regex, code, flags=re.DOTALL)
    match = next(matches, None)
    while match:
        to_rpl = match.group()
        rpl = " " * len(to_rpl)
        nwls = re.finditer(r'\r\n|\n|\r', to_rpl)
        nwl = next(nwls, None)
        while nwl:
            rpl = rpl[:nwl.start()] + nwl.group() + rpl[nwl.end():]
            nwl = next(nwls, None)
        code = code[:match.start()] + rpl + code[match.end():]
        match = next(matches, None)
    return code

def replace_comments_with_whitespace(code):
    code = replace_regex_with_whitespace(re.escape('/*') + r'(.*?)' + re.escape('*/'), code)
    code = replace_regex_with_whitespace(re.escape('//') + '(.*?)(\r\n|\n|\r)', code)
    return code


def call_mythril(filename, contract_name=None, config=None):
	cmd = ["myth", "-n", filename]
	if contract_name:
		cmd.extend(["-cn", contract_name ])
	if config:
		cmd.extend(["-cf", config ])
	print(cmd)
	p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
	output, err = p.communicate()
	rc = p.returncode
	print(err.decode("utf-8") )
	print(output.decode("utf-8") )

	output_dict = loads(output.decode("utf-8"))
	return output_dict

def call_mythril_multiple(file_contract_map):
	for filename, contract_names in file_contract_map.items():
		pass



def get_display_colors(level):
	if level == "vsingle":
		return ("region.redish","style='color:#e10000'", 6)
	elif level == "vchain":
		return ("region.orangish","style='color:#ff5500'", 5)
	elif level == "vdepth":
		return ("region.yellowish","style='color:#ffd400'", 4)
	elif level == "holds":
		return ("region.bluish","style='color:#1E90FF'", 3)
	elif level == "hsingle":
		return ("region.greenish","style='color:#32CD32'", 2)
	elif level == "unchecked":
		return ("region.blackish","style='color:#111111'", 1)

def clear_annotations(view):
	for ANO_KEY in ANNOTATION_KEYS:
		view.erase_regions(ANO_KEY)

def clear_violations(view):
	for VIO_KEY in VIOLATION_KEYS:
		view.erase_regions(VIO_KEY)

def clear_views(view):
	clear_annotations(view)
	clear_violations(view)

def get_all_annotations(view):
	regions = []
	for ANO_KEY in ANNOTATION_KEYS:
		regions.extend(view.get_regions(ANO_KEY))
	return regions

def get_all_violations(view):
	regions = []
	for VIO_KEY in VIOLATION_KEYS:
		regions.extend(view.get_regions(VIO_KEY))
	return regions
	
	

class AnnotationHover(sublime_plugin.ViewEventListener):

	def on_pre_save(self):
		clear_violations(self.view)
		clear_annotations(self.view)

	def on_show_violations(self, link):

		clear_violations(self.view)

		regions = get_all_annotations(self.view)

		point = int(link)
		# Todo Get point or region from link
		for region in regions:
			if region.contains(point):
				# From the region, get the annotation and the associated violations, display a new region for each violation and save info in the violations map for popup display
				self.shown_annotation = annotation_glob[self.view.file_name()][str(region)]

				violations_by_severity = {}

				violation_glob[self.view.file_name()] = {}

				for violation in self.shown_annotation['violations']:
					pos, length = violation["pos"], violation["length"]
					region = Region(pos, pos + length)
					if not (str(region) in violation_glob[self.view.file_name()] and violation_glob[self.view.file_name()][str(region)]):
						violation_glob[self.view.file_name()][str(region)] = []

					violation_glob[self.view.file_name()][str(region)].append(violation)

					color_reg, _, lvl_nr = get_display_colors(violation['level'])

					if not "vio_key_" + str(lvl_nr) in violations_by_severity:
						violations_by_severity["vio_key_" + str(lvl_nr)] = { "regions": [region], "color": color_reg, "mark": "bookmark", "style": sublime.DRAW_NO_OUTLINE }
					else:
						violations_by_severity["vio_key_" + str(lvl_nr)]["regions"].append(region)

				for lvl_key, lvl_regions in violations_by_severity.items():
					self.view.add_regions(lvl_key, lvl_regions["regions"], lvl_regions["color"], lvl_regions["mark"], lvl_regions["style"])




	def clear_violations(self, link):
		for VIO_KEY in VIOLATION_KEYS:
			self.view.erase_regions(VIO_KEY)
		self.shown_annotation = None

	def on_post_text_command(self, command_name, args):
		if args and 'event' in args:
			event = args['event']
			if 'x' in event and 'y' in event:
				global text_command_point
				text_command_point = self.view.window_to_text((event['x'], event['y']))



	def on_hover(self, point, hover_zone):
		regions = get_all_annotations(self.view)
		for region in regions:
			if region.contains(point):
				shown_violations = get_all_violations(self.view)
				if not shown_violations or len(shown_violations) < 1:
					self.shown_annotation = None

				# Todo From the region, check if it associates to an annotation, take that and format a message
				annotation = annotation_glob[self.view.file_name()][str(region)]
				a_msg, on_navigate, _ = self.format_ano_to_html(annotation, self.shown_annotation and self.shown_annotation == annotation, point)
				self.view.show_popup(a_msg, sublime.HIDE_ON_MOUSE_MOVE_AWAY, point, max_width=600, max_height=400, on_navigate=on_navigate)

		regions = get_all_violations(self.view)

		vio_msg = ""
		for region in regions:
			if region.contains(point):
				violations = violation_glob[self.view.file_name()][str(region)]
				for violation in violations:
					v_msg, _ = self.format_vio_to_html(violation, point)
					vio_msg += v_msg
		if len(vio_msg)>0:
			self.view.show_popup(vio_msg, sublime.HIDE_ON_MOUSE_MOVE_AWAY, point, max_width=600, max_height=400)
				# Todo From the region, check if it associates to the violation of an annotation, take that and format a message

	def format_vio_to_html(self, violation, point):
		colors = get_display_colors(violation['level'])
		html_text = "<h2 " + colors[1] + ">" + escape("Annotation violation") + "</h2>"
		html_text += "<p><span " + colors[1] + ">" + violation['level'] + ": </span><i>" + escape(violation['lvl_description']) + "</i></p>"
		html_text += "<p><span " + colors[1] + ">Description:</span>" + escape(violation['vio_description']) + "</p>"
		if "code" in violation and len(violation['code']):
			html_text += "<p><span " + colors[1] + ">Code: </span><i>" + escape(violation['code']) + "</i></p>"



		html_text += "<p><span " + colors[1] + ">Transaction depth:</span> " + str(violation['transaction_depth']) + "</p>"

		if "note" in violation and violation['note'] and len(violation["note"]):
			html_text += "<p><span " + colors[1] + ">Note: </span><i>" + escape(violation['note']) + "</i></p>"


		html_text += "<p><span " + colors[1] + ">Transaction signatures:</span> " + " -> ".join([("constructor" if not function['name'] and function['isConstructor'] else ("function" if not function['name'] else "") ) 
			+ function['signature'] for function in violation["chained_functions"]])+ "</p>"


		return html_text, "vio_key_" + str(colors[2])

	def format_ano_to_html(self, annotation, are_v_shown, point):
		colors = get_display_colors(annotation['level'])
		html_text = "<h2 " + colors[1] + ">" + escape(annotation['title']) + "</h2>"
		html_text += "<p><span " + colors[1] + ">Severity:</span><i>" + escape(annotation['lvl_description']) + "</i></p>"
		html_text += "<p><span " + colors[1] + ">Description:</span>  " +escape(annotation['ano_description']) + "</p>"
		on_navigate = None
		if annotation['violations'] and len(annotation['violations']) > 0:
			# html_text = "<p>" + annotation['vio_description'] + "</h2>"
			html_text += "<p><span " + colors[1] + ">Number of violations:</span> " + str(len(annotation['violations'])) + "<p>"

			if not are_v_shown:
				on_navigate = lambda link: AnnotationHover.on_show_violations(self, link)
				v_text = "Show violations"
			else:
				on_navigate = lambda link: AnnotationHover.clear_violations(self, link)
				v_text = "Hide violations"
			html_text += "<h3><a " + colors[1] + " href='" + str(point) + "'>" + v_text+ "</a></h3>"

		return html_text, on_navigate, "ano_key_" + str(colors[2])


	def set_hover_regions(self, regions):
		self.regions = regions

class AnnotaryLintCommand(sublime_plugin.TextCommand):

	def run(self, edit):
		clear_views(self.view)

		try:
			_thread.start_new_thread( AnnotaryLintCommand.run_async, (self, edit, AnnotaryLintCommand.run_annotary , AnnotaryLintCommand.mark_annotations) )
		except:
			print("Could not execute the annotary analysis in a separated thread")


	def run_async(self, edit, to_execute, callback):
		annotations_map = to_execute(self, edit)

		callback(self, edit, annotations_map)

	def run_annotary(self, edit):
		if not self.view.is_dirty():
			self.view.window().status_message("Annotary...")

			view_content = self.view.substr(sublime.Region(0, self.view.size()))

			comment_free_content = replace_comments_with_whitespace(view_content)

			index = max([m.start() for m in re.finditer(r'contract\s+', comment_free_content) if m.start() <= text_command_point])
			print(comment_free_content[index:])
			match = re.search(r'contract\s+(?P<cname>[^\s{]+)', comment_free_content[index:])


			plugin_path = join(sublime.packages_path(), "annotary")
			config = plugin_path + "/config"
			try:
				res = call_mythril(self.view.file_name(), match.group(1), config)
			except ValueError:
				show_error_message(self.view, "JSON answer of annotary backend could not be propperly decoded")
			self.view.window().status_message("Annotary: ok")
			return res
		else:
			show_error_message(self.view, "Save the current file before running Annotary.")
			return {}

	def mark_annotations(self, edit, annotations_map):

		# Todo check view consistency

		if self.view.file_name() not in annotation_glob:
			annotation_glob[self.view.file_name()] = {}


		annotations_by_severity = {}

		#for lvl_key in ANNOTATION_KEYS:
			#annotations_by_severity[lvl_key] = {}

		""" In here also set the values in the regions and violation_map for on hover over messages """
		for contract, annotations in annotations_map.items():
			for annotation in annotations:
				row, col = annotation['line'], annotation['col']
				# length = len(annotation['content'])
				# pos, length = self.view.text_point(row, col), annotation["length"]
				# start = self.view.text_point(row, col)
				pos, length = annotation["pos"], annotation["length"]
				region = Region(pos, pos + length)

				annotation_glob[self.view.file_name()][str(region)] = annotation

				color_reg, _, lvl_nr = get_display_colors(annotation['level'])
				print(color_reg)
				print(lvl_nr)
				# Todo I have to add all regions with different level under a different key
				if not "ano_key_" + str(lvl_nr) in annotations_by_severity:
					annotations_by_severity["ano_key_" + str(lvl_nr)] = { "regions": [region], "color": color_reg, "mark": "dot", "style": sublime.DRAW_NO_OUTLINE }
				else:
					annotations_by_severity["ano_key_" + str(lvl_nr)]["regions"].append(region)

		for lvl_key, lvl_regions in annotations_by_severity.items():
			print(" ".join([str(lvl_key), str(lvl_regions["regions"]), str(lvl_regions["color"]), str(lvl_regions["mark"]), str(lvl_regions["style"])]))
			self.view.add_regions(lvl_key, lvl_regions["regions"], lvl_regions["color"], lvl_regions["mark"], lvl_regions["style"])


class AnnotaryCleanCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		clear_views(self.view)

class AnnotaryOpenConfig(sublime_plugin.TextCommand):
	def run(self, edit):
		plugin_path = join(sublime.packages_path(), "annotary")
		self.view.window().open_file(plugin_path + "/config")
