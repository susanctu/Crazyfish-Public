import re

BLOCK_TAG_START = '{%'
BLOCK_TAG_END = '%}'

tag_re = (re.compile('(%s.*?%s)' % 
		 (re.escape(BLOCK_TAG_START), re.escape(BLOCK_TAG_END))))

name_extract_re = (re.compile('%s\W*block\W+([^\W]+)\W*?%s' % 
		 		  (re.escape(BLOCK_TAG_START), re.escape(BLOCK_TAG_END))))

endblock_re = (re.compile('%s\W*endblock\W*?%s' % 
		      (re.escape(BLOCK_TAG_START), re.escape(BLOCK_TAG_END))))

JS_FORMAT = '$(\"%s\" ).on(\"%s\", function() { window.location = \"%s\"});'
class TagError(Exception):
    pass

def tokenize(template_string):
    """
    Return a list of tokens from a given template_string.

    Taken from the Django template code.
    """
    in_tag = False
    result = []
    for bit in tag_re.split(template_string):
        if bit:
            result.append((bit, in_tag))
        in_tag = not in_tag
    return result

def is_start_tag(token):
	print token
	match = name_extract_re.search(token)
	if match:
		return True
	else:
		return False

def get_block_name(token):
	match = name_extract_re.search(token)
	if match:
		return match.group(1)
	else:
		raise TagError('Failed to extract block name from %s' % token)

def is_end_tag(token):
	match = endblock_re.search(token)
	if match:
		return True
	else:
		return False

def generate_page(template, new_page, block_content, flow_info=None):
	"""
	TODO
	"""
	output = open(new_page, 'w')
	src = open(template, 'r')
	tokens = tokenize(src.read())
	src.close()
	tag_depth = 0 # start counting whenever we enter a block that is supposed to be replaced
	in_repl_block = False
	repl_block = None
	for token, is_tag in tokens:
		# print token
		# print is_tag
		if not is_tag and not repl_block:
			output.write(token)
		elif not is_tag: # but in a block that should be replaced
			pass
		elif is_tag and repl_block: 
			# so this could be an unreferenced start tag
			if is_start_tag(token):
				if get_block_name(token) in block_content:
					raise TagError('Cannot replace nested blocks.')
				else:
					tag_depth += 1
			else: # or an endtag
				tag_depth -= 1
				assert(tag_depth >= 0)
				if tag_depth == 0:
					# write the replacement text
					output.write(block_content[repl_block])
					repl_block = None
		else: # is_tag and not repl_block
			if is_start_tag(token):
				if get_block_name(token) in block_content:
					repl_block = get_block_name(token)
					tag_depth += 1	
	if flow_info: # TODO (susanctu): this works but SHOULD go before the last html tag
		output.write('<script src=\"https://code.jquery.com/jquery.js\"></script>')
		output.write('<script>')
		for class_or_id in flow_info.keys():
			output.write(JS_FORMAT % (class_or_id, 
				                     flow_info[class_or_id][0], 
				                     flow_info[class_or_id][1]))
		output.write('</script>')
	output.close()			

def main():
	f = open('config.py', 'r')
	exec(f);
	
	for new_page, src_info in PAGES.items():	
		if new_page in FLOWS:
			generate_page(src_info[0], new_page, src_info[1], FLOWS[new_page])
		else:
			print 'WARNING: no FLOW found'
			generate_page(src_info[0], new_page, src_info[1])

if __name__ == "__main__":
	main()