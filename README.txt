1. DESCRIPTION

	this plugin finds duplicate code across project
	just proof of concept, use it at your own risk
	works fine for simple case 
	(https://github.com/do-/eludia/, 10k lines project, threshold minimum 30 common lines)

2. INSTALLATION

	place dedoop.py to your User packages folder

	change filter via file_extension option (see dedoop.py, defaults to python files)

	add hotkey to your platform .sublime-keymap file, like this:

	{ "keys": ["ctrl+alt+d"], "command": "find_duplicate_code",  
		"arguments":{"min_lines": 30, "encoding": "utf-8", "file_extenstion": "py", "comment_char" : "#"}} 


3. USAGE

	use hotkey to generate report in a new tab for you project