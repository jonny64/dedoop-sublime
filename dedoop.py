import sublime, sublime_plugin, os, os.path, re, hashlib

class FindDuplicateCodeCommand(sublime_plugin.TextCommand):
	"""
	seeks and shows all duplicate fragments across current project files
	"""

	def run(self, edit, file_extension='js', encoding='utf-8', comment_char='//', min_lines=50): 
		
		self.results = self.view.window().new_file()
		self.results.set_name('Duplicate code in project')
		self.results.set_scratch(True)
		self.edit = edit

		self.append("\nSearching for duplicate lines in project folders:")
		project_folders = sublime.active_window().folders()
		if len(project_folders) == 0:
			self.append("\nProject does not contain any folder. Aborting")
			return
		
		# index files in project folders
		idx = LineIndex(
			file_extension = file_extension,
			encoding       = encoding,
			comment_char   = comment_char,
			min_lines      = min_lines
		)
		for folder in project_folders:
			self.append("\t{0}".format(folder))
			idx.index(folder)
		
		self.append(
			'\n{0} unique lines indexed ' \
				.format(len(idx.get_chunks()))
		)
		self.append('searching for text duplicates larger than {0} lines'.format(min_lines))

		# find common chunks, print report
		common_chunks = idx.get_common_chunks()
		if len(common_chunks) == 0:
			self.append("\nNothing found. Your project is probably ok")
			return

		for chunk in common_chunks:
			self.append('\n------------------------------------------------------------------')
			self.append(
				'{0} lines are common across following set of project files: ' \
					.format(chunk.length)
				)
			for file_path in chunk.get_files():
				self.append('\t{0}'.format(file_path))
			self.append(chunk.get_text())

		# scroll to top
		self.results.show(0)

	def append(self, text):
		self.results.run_command("insert_snippet", {"contents": text + "\n"})

class LineIndex:
	"""
	helper index for duplicate text blocks across files
	"""
	def __init__(self, file_extension, encoding, comment_char, min_lines):
		self.files = []
		self.unique_chunk_index = {}
		
		self.file_extension = file_extension
		self.encoding = encoding
		self.comment_char = comment_char
		self.min_lines = min_lines
		
	def index(self, dirname):
		for root, dirs, files in os.walk(dirname):
			for fname in files:
				if fname.endswith('.' + self.file_extension):
					self.files.append(os.path.join(root, fname))
		
		for file in self.files:
			self.index_file(file)
	
	"""
	first pass: hash every chunk (line) and find files where it exists
	TODO: use larger chunks
	"""
	def index_file(self, file_path):
		
		with open(file_path, 'r') as file: 
			text = file.readlines()

			for line in text:
				line = line.decode(self.encoding)
				
				if line.strip().startswith(self.comment_char):
					continue
				
				chunk = Chunk(line, file_path)

				if chunk.length == 0:
					continue
				
				if self.unique_chunk_index.has_key(chunk.get_hash()):
					self.unique_chunk_index[chunk.get_hash()].add_file(file_path)
				else:
					self.unique_chunk_index[chunk.get_hash()] = chunk

 	def get_chunks(self):
 		return self.unique_chunk_index.values()

	def get_common_chunks(self):
 		
 		common_chunks = set()

		for file in self.files:
			common_chunks.update(self.get_file_common_chunks(file, self.min_lines))
		
		return common_chunks

	"""
	yep, second pass 
	for given file returns text chunks which exist in more than one file
	"""
	def get_file_common_chunks(self, file_path, min_lines):

		large_chunks = []

		with open(file_path, 'r') as file: 
			text = file.readlines()

			started_chunk = Chunk(length=0)

			for line in text:
				line = line.decode(self.encoding)
				
				if line.strip().startswith(self.comment_char):
					continue
				
				chunk = Chunk(line)
				if chunk.length == 0:
					continue
				
				chunk.files = self.unique_chunk_index[chunk.get_hash()].files

				if len(chunk.files) < 2:
					if started_chunk.length >= min_lines and len(started_chunk.files) > 1:
						large_chunks.append(started_chunk)

					started_chunk = Chunk(length=0)
					continue
				
				started_chunk = started_chunk.merge(chunk)

		return large_chunks
	
class Chunk:
	"""
	Unique piece of code (currently its just a hash of one line)
	"""
	def __init__(self, text = '', file_path = '', length = 1):
		
		self.original_text = text
		self.text = re.sub('\s+', ' ', text.strip())
		self.files = set([file_path])

		if not self.text:
			self.length = 0
			return

		self.length = length

	def get_files(self):
		return self.files
	
	def get_text(self):
		return self.original_text

	def add_file(self, file_path):
		self.files.add(file_path)
	
	def merge(self, another_chunk):

		merge_result = Chunk(self.original_text + '\n' + another_chunk.original_text)
		merge_result.length = self.length + another_chunk.length
		if len(self.files) == 0:
			merge_result.files = another_chunk.files
		else:
			merge_result.files = self.files.intersection(another_chunk.files)
		
		return merge_result
	
	def get_hash(self):
		# TODO: if 32 bits not enough use something fast and large instead
		# like MurmurHash http://pypi.python.org/pypi/smhasher
		return self.text.__hash__()
			
	# hashable
	def __hash__(self):
		return self.get_hash()
	
	def __eq__(self, other):
		return self.get_hash() == other.get_hash()

