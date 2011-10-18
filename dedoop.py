import sublime, sublime_plugin, os, os.path, re, hashlib

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
		
		self.append('\n\n' + unicode(len(idx.get_chunks())))

		for chunk in idx.get_common_chunks():
			#self.append('\n\n' + chunk.get_text())
			self.append('\n\n' + unicode(chunk.get_files()))

		for chunk in idx.get_chunks():
			if len(chunk.files) > 1:
				self.append('\n\n' + unicode(chunk.files))
		

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
		self.unique_chunk_index = {}
		
		
	def index(self, dirname):
		for root, dirs, files in os.walk(dirname):
			for fname in files:
				if fname.endswith('.' + self.file_extension):
					self.files.append(os.path.join(root, fname))
		
		for file in self.files:
			self.index_file(file)
	
	def index_file(self, file_path):
		
		with open(file_path, 'r') as file: 
			text = file.readlines()

			for line in text:
				line = line.decode('cp1251')
				
				if line.startswith(self.comment_char):
					continue
				
				line = re.sub('\s+', ' ', line)
				
				chunk = Chunk(line, file_path)

				if chunk in self.unique_chunk_index:
					self.unique_chunk_index[chunk.get_hash()].add_file(file_path)
				else:
					self.unique_chunk_index[chunk.get_hash()] = chunk

 	def get_chunks(self):
 		return self.unique_chunk_index.values()

	"""naive, second-pass way to find common sequences"""
 	def get_common_chunks(self, min_lines = 2):
 		
 		common_chunks = set()

		for file in self.files:
			common_chunks.update(self.get_file_common_chunks(file, min_lines))
		
		return common_chunks

	def get_file_common_chunks(self, file_path, min_lines):

		large_chunks = []

		with open(file_path, 'r') as file: 
			text = file.readlines()

			started_chunk = Chunk(length=0)

			for line in text:
				line = line.decode('cp1251')
				
				if line.startswith(self.comment_char):
					continue
				
				line = re.sub('\s+', ' ', line)
				
				chunk = Chunk(line)
				chunk = self.unique_chunk_index[chunk.get_hash()]

				if len(chunk.files) > 1:
					sublime.status_message(unicode(chunk.files))

				if len(chunk.files) < 2:
					if started_chunk.length >= min_lines:
						large_chunks.append(started_chunk)

					started_chunk = Chunk(length=0)
					continue
				
				started_chunk = started_chunk.merge(chunk)
		
		if len (large_chunks) > 1:
			sublime.status_message(unicode(large_chunks))

		return large_chunks
	
class Chunk:
	"""
	Unique piece of code (currently its just a hash of one line)
	"""
	def __init__(self, text = '', file_path = '', length = 1):
		
		self.text = text
		self.files = set([file_path])
		self.length = length

	def __hash__(self):
		return self.get_hash()

	def get_files(self):
		return self.files
	
	def get_hash(self):
		# TODO: if 32 bits not enough use something fast and large instead
		# like MurmurHash http://pypi.python.org/pypi/smhasher
		return self.text.__hash__()
		#return hashlib.md5(self.line.encode()).hexdigest()

	def get_text(self):
		return self.text

	def add_file(self, file_path):
		self.files.add(file_path)
	
	def merge(self, another_chunk):

		merge_result = Chunk(self.text + another_chunk.text)
		merge_result.length = self.length + another_chunk.length
		if len(self.files) == 0:
			merge_result.files = another_chunk.files
		else:
			merge_result.files = self.files.intersection(another_chunk.files)
		
		return merge_result

