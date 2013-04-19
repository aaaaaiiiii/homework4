'''
Artificial Intelligence
Homework 4 Part 7
Oren Shoham, Sayer Rippey, Peter Fogg
'''

import sys
import os
import operator
import math
import uuid
import subprocess

'''
Tree Class (used to build decision tree)
Each Tree stores an attribute or a classification (never both), and a dictionary of child Trees
'''
class Tree():
	'''
	Constructor
	'''
	def __init__(self, attribute = None, classification = None):
		self.attribute = attribute
		self.classification = classification
		self.children = {}
		self.iden = str(uuid.uuid4().int)

		if self.attribute is not None:
			if self.attribute[0].isdigit():
				self.attribute = '_' + self.attribute
		if self.classification is not None:
			if self.classification[0].isdigit():
				self.classification = '_' + self.classification
	
	def is_leaf(self):
		return not self.children

	'''
	Add a child as the value of a dictionary entry whose key is the value of the attribute that was split on to lead to this node of the Tree
	'''
	def add_child(self, child, value):
		if value[0].isdigit():
			value = '_' + value
		self.children[value] = child

	def graphviz_nodes(self):
       		'''
        	Returns all the nodes of the tree in dot format, i.e.,
        
        	node_name [label=foo]
        	'''
		s = ''
		if self.classification is not None:
			s = '%s [label=%s]\n' % (self.iden, self.classification)
		else:
			s = '%s [label=%s]\n' % (self.iden, self.attribute)
		if not self.is_leaf():
			for value in self.children:
				s += self.children[value].graphviz_nodes()
        	return s

	def graphviz_edges(self):
        	'''
        	Returns all the edges of the tree in dot format, i.e.,
        	
        	node_name -> other_node [label=foo]
        	'''
        	s = ''
		if not self.is_leaf():
			for value in self.children:
				s += '%s -> %s [label=%s] \n' % (self.iden, self.children[value].iden, value)
				s += self.children[value].graphviz_edges()
        	return s

	def __unicode__(self):
		return self.preorder()

def to_graphviz(tree):
    'Returns the dot represention of this tree. Nothing too fancy.'
    s = 'digraph {\n'
    s += tree.graphviz_nodes()
    s += tree.graphviz_edges()
    s += '\n}'
    return s


'''
ID3 Algorithm
'''
def id3(attributes, training_set, classifier):
	'Determines whether every dictionary in list_of_dicts has the same value for key'
	def same_value(list_of_dicts, key):
		value = list_of_dicts[0][key]
		for dictionary in list_of_dicts[1:]:
			if dictionary[key] != value:
				return False
		return True

	'Determines the most common value in list_of_dicts for key'
	def majority_value(list_of_dicts, key):
		value_freqs = {}
		for dictionary in list_of_dicts:
			if dictionary[key] in value_freqs:
				value_freqs[dictionary[key]] = value_freqs[dictionary[key]] + 1
			else:
				value_freqs[dictionary[key]] = 1
		return max(value_freqs.iteritems(), key = operator.itemgetter(1))[0]

	'Chooses the attribute with the largest info gain.'
	def choose_best_attribute(dataset, atts):
		'Computes the entropy of a set of examples'
		def entropy(s):
			proportions = {i: 0.0 for i in atts[classifier]}
			retval = 0.0
			for val in atts[classifier]:
				for ex in s:
					if ex[classifier] == val:
						proportions[val] += 1.0
				if len(s) == 0:
					proportions[val] = 0.0
				else:
					proportions[val] /= len(s)
				if proportions[val] != 0:
					retval += proportions[val] * math.log(proportions[val], 2)
			return -1 * retval
		
		'Computes the Rem of a set of examples split on an attribute'
		def rem(att, s):
			retval = 0.0
			for val in atts[att]:
				s_val = []
				for ex in s:
					if ex[att] == val:
						s_val.append(ex)
				retval += (float(len(s_val)) / len(s)) * entropy(s_val)
			return retval

		'Computes the Info Gain of a set of examples split on an attribute'
		def info_gain(att, s):
			return entropy(s) - rem(att, s)
		
		info_gains = {}
		for att in atts:
			if att != classifier:
				info_gains[att] = info_gain(att, dataset)
		
		return max(info_gains.iteritems(), key = operator.itemgetter(1))[0] # Return the attribute with the largest info gain
	
	if not training_set: # If there are no training examples left, make a FAIL node
		return Tree(classification = 'FAIL')
	elif same_value(training_set, classifier): # If all examples have the same classification, make a node with that classification
		return Tree(classification = training_set[0][classifier])
	elif not attributes or len(attributes) == 1: # If there are no attributes left or only the classifier is left, make a node with the majority classification
		return Tree(classification = majority_value(training_set, classifier))
	else:
		best_attribute = choose_best_attribute(training_set, attributes) # choose the attribute with the highest info gain
		tree = Tree(attribute = best_attribute) # make a node with the best attribute
		for value in attributes[best_attribute]: # split on best attribute and run ID3 on each subset
			subset = []
			for example in training_set:
				if example[best_attribute] == value:
						subset.append(example)
			sub_attributes = attributes.copy()
			del sub_attributes[best_attribute]
			subtree = id3(sub_attributes, subset, classifier)
			tree.add_child(subtree, value)
		return tree

def main():
	args = sys.argv[1:]
	if len(args) == 0:
		sys.exit("You must supply an input filename as a command-line argument.")
	
	filename = args[0]
	f = open(filename)
	fields = f.readline().strip().split('\t') # the attributes
	classifier = fields[len(fields)-1] # the classifier attribute
	attributes = {a: set() for a in fields} # attributes as keys whose values are sets containing the possible values that each attribute can take on
	examples = [] # the data set
	for line in f:
		data = line.strip().split('\t')
		example = {}
		for i in range(len(data)):
			example[fields[i]] = data[i] # set the current example's attributes
			attributes[fields[i]].add(data[i]) # get the set of values that each attribute can take on
		examples.append(example)
	f.close()

	graph = to_graphviz(id3(attributes, examples, classifier))
	filename = filename[:-3] + 'dot'
	g = open(filename, 'w')
	g.write(graph)
	g.close()

	output_filename = filename[:-3] + 'pdf'
	subprocess.call(["dot", "-Tpdf", filename, "-o", output_filename])
	if(sys.platform == 'win32'):
		os.system("start "+ output_filename)
	elif(sys.platform == 'darwin'):
		os.system("open " + output_filename)
	elif(sys.platform == 'linux2'):
		os.system("xdg-open " + output_filename)

if __name__ == '__main__':
    main()
