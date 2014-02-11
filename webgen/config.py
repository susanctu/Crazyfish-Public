PAGES = {'index1.html': ('index_template.html', {}),
	 'index2.html': ('index_template.html', {'central': '...for a tool that...'}),
         'index3.html': ('index_template.html', {'central': '...we\'re working on.', 'central2': 'central 2'}),
         'index4.html': ('index_template.html', {'ignore': 'don\'t ignore me!'})}

FLOWS = {'index1.html': {'.central': ('click', 'index2.html')},
		 'index2.html': {'.central': ('click', 'index3.html')},
		 'index3.html': {'.central': ('click', 'index1.html')}}



