1. DESCRIPTION

	This Sublime 2 plugin finds duplicate code across project

	just proof of concept, use it at your own risk

	works fine for simple case 
	(https://github.com/jquery/jquery, 16k lines project, threshold minimum 30 common lines)

2. INSTALLATION

	place dedoop.py to your User packages folder

	add hotkey to your platform .sublime-keymap file (via Preferences - Key Bindings - User), like this:

	{ "keys": ["ctrl+alt+d"], "command": "find_duplicate_code",  
		"args":{"min_lines": 30, "encoding": "utf-8", "file_extension": "js", "comment_char" : "//"}} 

3. USAGE

	use hotkey to generate report for opened project