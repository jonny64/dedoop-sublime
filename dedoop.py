import sublime, sublime_plugin, os, os.path, hashlib
from difflib import SequenceMatcher

class FindDuplicateCodeCommand(sublime_plugin.TextCommand):
	"""
	seeks and shows all duplicate fragments across current project files
	"""

	def run(self, edit): 
		
		self.results = self.view.window().new_file()
		self.results.set_name('Duplicate code in project')
		self.results.set_scratch(True)
		self.edit = edit

		self.append("\nSearhing for duplicate lines\n")
		
		idx = LineIndex(file_extension='py')
		for folder in sublime.active_window().folders():
			idx.index(folder)
		
		dict = idx.get_overlaps()
		for key in dict.keys():
			overlap = dict[key]

			if (overlap['size'] < 2) or (len(overlap['files']) < 2):
				continue
			
			self.append('\n\n' + str(overlap['size']) + ' lines are common across')
			self.append('\n'.join(overlap['files']))
			self.append('\n\nlines are:\n' + '\n'.join(overlap['lines']))

			self.append('\n--------------------------------------------------------\n')

		self.results.show(0)

	def append(self, text):
		self.results.run_command("insert_snippet", {"contents": text + "\n"})

class LineIndex:
	"""
	helper index for duplicate text blocks across files
	"""
	def __init__(self, file_extension='py'):
		self.file_extension = file_extension
		self.files = []
		self.match_index = {}
		self.comparer = \
			SequenceMatcher(lambda ignored_characters: ignored_characters in " \t\n")
		
		
	def index(self, dirname):
		for root, dirs, files in os.walk(dirname):
			for fname in files:
				if fname.endswith('.' + self.file_extension):
					self.files.append(os.path.join(root, fname))
		
		for i in range(0, len(self.files)):
			for j in range(i, len(self.files)):
				self.compare(self.files[i], self.files[j])
	
	def compare(self, file1, file2):
		with open(file1) as file: 
 			with open(file2) as another_file:

 				text1 = file.readlines()
 				text2 = another_file.readlines()

 				self.comparer.set_seqs(text1, text2)
 				for match in self.comparer.get_matching_blocks():
 					
 					if match.size == 0:
	 					continue

					overlap_lines = text1[match.a:match.size]
 					 					
 					overlap_sha = hashlib.md5(';'.join(overlap_lines)).hexdigest()
 					overlap = self.match_index.get(overlap_sha, {'files': set(), 'lines':[]})
 					overlap['files'].add(file1)
 					overlap['files'].add(file2)
 					overlap['lines'] = overlap_lines
 					overlap['size'] = match.size
 					self.match_index[overlap_sha] = overlap

 	def get_overlaps(self):
 		return self.match_index
	
