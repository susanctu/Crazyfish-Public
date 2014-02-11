import sys
import re
import argparse
import os.path

BLOCK_TAG_START = '{%'
BLOCK_TAG_END = '%}'

tag_re = (re.compile('(%s.*?%s)' % 
		 (re.escape(BLOCK_TAG_START), re.escape(BLOCK_TAG_END))))

name_extract_re = (re.compile('%s\W*block\W+([^\W]+)\W*?%s' % 
		 		  (re.escape(BLOCK_TAG_START), re.escape(BLOCK_TAG_END))))

endblock_re = (re.compile('%s\W*endblock\W*?%s' % 
		      (re.escape(BLOCK_TAG_START), re.escape(BLOCK_TAG_END))))

# for string formatting
JS_FORMAT = '$(\"%s\" ).on(\"%s\", function() { window.location = \"%s\"});'
MALFORMED_CONFIG_FORMAT = 'Mandatory definition of %s missing from config file.\n'

class TagError(Exception):
    pass

class ConfigError(Exception):
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
	"""
	Args:
        token: the path to the configuration file (string)
	"""
	match = name_extract_re.search(token)
	if match:
		return True
	else:
		return False

def get_block_name(token):
	"""
	Assumes that token is a start tag.

	Args:
        token: the path to the configuration file (string)
	"""
	match = name_extract_re.search(token)
	if match:
		return match.group(1)
	else:
		raise TagError('Failed to extract block name from %s' % token)

def is_end_tag(token):
	"""
	Args:
        token: the path to the configuration file (string)
	"""
	match = endblock_re.search(token)
	if match:
		return True
	else:
		return False

def generate_page(template, new_page, block_content, clobber=False, flow_info=None):
	"""
	Takes in the name of the template, the name of the page to be generated,
	a dictionary mapping block names to content they should be replaced with,
	and optional flow information (a map of classes/id's mapping to tuples 
	(event, page to redirect to)).
	"""
	
		
	if not clobber and os.path.isfile(new_page):
		raise Exception('%s already exists. (use --clobber to overwrite)' % new_page)
	else:
		output = open(new_page, 'w')
	
	# open the template and tokenize it
	src = open(template, 'r')
	tokens = tokenize(src.read())
	src.close()

	tag_depth = 0 # start counting whenever we enter a block that is supposed to be replaced
	# repl_block is the name of the block to replace, None means we're not in one
	repl_block = None 
	for token, is_tag in tokens:
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
				if tag_depth < 0:
					raise TagError('Found more endtags than start tags.')
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

def load_config(config_file):
	"""
	Opens config_file, which is executed as a python script. 
	(Not exactly safe, but since the user is running this on his/her own
	computer, we don't bother to do anything more secure.) Checks that the 
	config file defines PAGES and FLOWS. 

	PAGES should be defined as follows:

	PAGES = {'index1.html': ('index_template.html', {}),
	 	     'index2.html': ('index_template.html', 
	 	     	             {'central': 'replacement text'})}

	Each key in the PAGES dictionary is a 2-tuple containing the template to 
	generate the page from and dictinary mappng from block names to the text to 
	replace the current block contents with. 

	Blocks should be specified in templates as 

	{% block central %}
		contents of block, blah, blah, blah
	{% endblock %}

	where the block can be given any name without whitespace (here, the block
	is called 'central')

	Note that in the above example, index.html is just index_template with all
	block tags removed but their contents preserved (i.e., if you don't specify
	a block by name in PAGES but it exists in the template, the page will be 
	generated with just the tags stripped.)

	FLOWS should be defined as follows:

	FLOWS = {'index1.html': {'.central': ('click', 'index2.html')},
		 	 'index2.html': {'.central': ('click', 'index3.html')}}

	where each value in FLOWS is a dictionary mapping from classes/ids to
	2-tuples of jquery events and the page that we should navigate to 
	when the event happens on an element with that class/id.

	It is ok for FLOWS to be empty.

    Args:
        config_file: the path to the configuration file (string)

    Returns:
    	Tuple containing PAGES and FLOWS.
	"""
	f = open(config_file, 'r')
	exec(f);

	try:
		PAGES
	except NameError:
		sys.stderr.write(MALFORMED_CONFIG_FORMAT % 'PAGES')

	try:
		FLOWS
	except NameError:
		sys.stderr.write(MALFORMED_CONFIG_FORMAT % 'FLOWS')

	return (PAGES, FLOWS)



def main():
	# parse arguments
	parser = argparse.ArgumentParser()
	parser.add_argument(
		'config_file', help='a configfile to tell this tool what to generate')
	parser.add_argument('--clobber', '-c', 
		                action='store_true', 
		                help='ok to overwrite files')
	args = parser.parse_args()

	# load config
	PAGES, FLOWS = load_config(args.config_file)

	# generate each page specified in the config
	# with appropriate navigation between them
	for new_page, src_info in PAGES.items():
		if len(src_info) != 2:
			raise ConfigError(
				'Block name and replacement text tuple contains too many elements.')
		try: 
 			if new_page in FLOWS:
				generate_page(src_info[0], 
					          new_page, 
					          src_info[1], 
					          args.clobber, 
					          FLOWS[new_page])
			else:
				sys.stderr.write(
					'WARNING: No FLOWS found for nagivation away from %s\n' % new_page)
				generate_page(src_info[0], new_page, src_info[1], args.clobber)
		except Exception as e:
			print e
			raise ConfigError('Error generating %s, likely due to config error.'
			                   % new_page)

if __name__ == "__main__":
	main()
	
	