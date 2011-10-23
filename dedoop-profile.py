import sublime, sublime_plugin, cProfile, pstats

class ProfileDedoopCommand(sublime_plugin.TextCommand):

	def run(self, edit):
		"""
		Helper command to find bottlenecks: dump perfomance-related information to console
		"""

		cProfile.runctx(
			'self.view.run_command("find_duplicate_code", \
				{"min_lines": 20, "file_extension": "pm", "comment_char" : "#"})',
			{'self' : self},
			{},
			'dedoop_profile'
		);
		stats = pstats.Stats('dedoop_profile')
		stats.sort_stats('cumulative')
		stats.print_stats('dedoop.py:')