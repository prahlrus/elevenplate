#! /usr/bin/python

import argparse
import io
import re
import random

class GrammarParseError(Exception):
	def __init__(self, msg):
		self.msg = msg

# argument whatsits
parser = argparse.ArgumentParser()
parser.add_argument('infile', help='grammar file to be parsed')
args = parser.parse_args()

empty_or_comment = re.compile(r"\s*(#.*)?$")
tablehead = re.compile(r";;\s*(?P<tabname>\w+)(\s+(?P<columns>[1-9]\d*))?\s*(#.*)?$")
garbage = re.compile(r";;.*$")

"""
	modes:
	0 - main list mode, puts everything in the start state table
	1 - simple table mode, puts each line in a named simple table
	2 - complex table mode:
			splits each line on the & character
			checks to make sure the number of columns is correct
			puts the list of columns into a named complex table
"""

mode = 0
line_no = 0
columns = 0

start = []
db = {}
current_table = None

with open(args.infile) as infile:
	for line in infile:
		line_no += 1

		# ignore comments
		line = line.split('#')[0].strip()
		if len(line) == 0:
			continue

		# check to see if a new table is beginning
		m = tablehead.match(line)
		if m is not None:
			# start making a new table, keep track of it by its name under db
			current_table = list()
			db[m.group('tabname')] = current_table
			if m.group('columns') is not None:
				columns = int(m.group('columns'))
				mode = 2
			else:
				columns = 0
				mode = 1
			continue
		# throw a hissy fit if the line starts with two semicolons but is garbage
		if garbage.match(line):
			raise GrammarParseError('At line ' + str(line_no) + ": line begins with ';;' but fails to parse as table name.")
	
		# handle a non-table-heading line
		if mode == 0:
			start.append(line)
		elif mode == 1:
			current_table.append(line)
		elif mode == 2:
			cols = line.split('&')
			if len(cols) == columns:
				current_table.append(cols)
			else:
				raise GrammarParseError('At line ' + str(line_no) + ': expected ' + str(columns) + ' columns, but read: ' + str(cols) + '.')

ex_rex = re.compile(r"\[((?P<new>!)|(?P<soft>\?))?(?P<tab>\w+)(\.(?P<attr>\d+))?\]")

"""
	What follows is a random expander of a context-sensitive grammar.
	
	Every time a [table] is referenced in the string being expanded, it is replaced with:
	 - (the appropriate column of) a random line from the table if it is not in the context
	 - the (appropriate column of) the line returned by a previous query
	
	Table references can be modified:
	 - [!table] does not check the context and always selects a random line but does not 
	 change the context
	 - [?table] checks the context but does not change it if there is no line loaded
"""

def expand(s,context):	
	replacements = []
	for m in re.finditer(ex_rex,s):
		tab, attr = m.group('tab'), m.group('attr')
		new, soft = m.group('new') is not None, m.group('soft') is not None
		
		# check the context unless a new reference is desired
		if tab not in context or new:	
			repline = query(tab)
		else:
			repline = context[tab]
		
		if attr is not None:
			rep = repline[int(attr)]
		else:
			rep = repline
		
		# keep the newly generated context around, unless new or soft
		if tab not in context and not (new or soft):
			context[tab] = repline
		
		replacements.append([m.start(),m.end(),rep])

	# nothing more to be done
	if len(replacements) == 0:
		return s

	new_s = ""
	pos = 0
	for start,end,rep in replacements:
		if start > pos:
			new_s += s[pos:start]
		new_s += rep
		pos = end
	if pos < len(s):
		new_s += s[pos:len(s)]
	return expand(new_s,context)

def query(tab):
	table = db[tab]
	return table[random.randint(0,len(table)-1)]

print expand(start[random.randint(0,len(start)-1)],dict())