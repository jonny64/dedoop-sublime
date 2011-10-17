import sublime, sublime_plugin, os, os.path, re, codecs, hashlib

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
		
		idx = LineIndex(file_extension='pm')
		for folder in sublime.active_window().folders():
			idx.index(folder)
		
		self.append('\n\n' + str(len(idx.get_chunks())))

		for chunk in idx.get_chunks():
			#self.append('\n\n' + str(chunk.get_hash()))
			#self.append('\n' + str(chunk.get_text()))
			#self.append('\n' + str(chunk.get_files()))
			
			if len(chunk.get_files()) > 1:
				self.append('\n\n' + str(chunk.get_files()))

		self.results.show(0)

	def append(self, text):
		self.results.run_command("insert_snippet", {"contents": text + "\n"})

class LineIndex:
	"""
	helper index for duplicate text blocks across files
	"""
	def __init__(self, file_extension='py', comment_char='#'):
		self.file_extension = file_extension
		self.comment_char = comment_char
		self.files = []
		self.chunk_index = {}
		
		
	def index(self, dirname):
		for root, dirs, files in os.walk(dirname):
			for fname in files:
				if fname.endswith('.' + self.file_extension):
					self.files.append(os.path.join(root, fname))
		
		for file in self.files:
			self.index_file(file)
	
	def index_file(self, file_path):
		
		with codecs.open(file_path, 'r', 'cp1251') as file: 
			text = file.readlines()
			for line in text:
				if line.startswith(self.comment_char):
					continue
				line = re.sub('\s+', ' ', line)
				
				chunk = Chunk(line, file_path)
				
				known_chunk = self.chunk_index.get(chunk.get_hash(), chunk)
				known_chunk.add_file(file_path)
				self.chunk_index[chunk.get_hash()] = chunk

 	def get_chunks(self):
 		return self.chunk_index.values()
	
class Chunk:
	"""
	Unique piece of code (currently its just a hash of one line)
	"""
	def __init__(self, line, file_path):
		self.text = line
		self.files = set([file_path])

		# TODO: if 32 bits not enough use something fast and large instead
		# like MurmurHash http://pypi.python.org/pypi/smhasher
		self.hashsum = line.__hash__()
		#self.hashsum = hashlib.md5(line).hexdigest()
		
	
	def get_files(self):
		return self.files
	
	def get_hash(self):
		return self.hashsum

	def get_text(self):
		return self.text

	def add_file(self, file_path):
		self.files.add(file_path)
