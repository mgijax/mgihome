
#
# This module contains the definitions of the DataSet and TextFileDataSet
#   classes.
# It also defines functions that operate on DataSet's (these would likely
#   be class methods if this were in Java.)


#import ignoreDeprecation
#import sys
#import os
import string

DEBUG = 0

#
# Global functions that operate on DataSets and records of DataSets
#

def printDuplicateIDs(rcdlist, dupsDict):
    # don't think this is used anymore ??

    for fn in dupsDict.keys():
	print 
	d = dupsDict[fn]
	if len(d.keys()) == 0:
	    print "no duplicates for %s" % fn
	else:
	    for value in d.keys():
		print "%s--> %s: keys %s" % (fn, value, d[value][0:4]),
		if len(d[value]) > 4:
		    print "%d lines total" % len(d[value]),
		print
		for key in d[value][0:4]:

		    if rcdlist[key].has_key("_linenumber"):
			print "    line %s:" % rcdlist[key]["_linenumber"]
		    else:
			print "    key  %s:" % key

		    for f in dupsDict.keys():
			if rcdlist[key][f] == None:
			    print "        %s->None" % (f)
			else:
			    print "        %s->'%s'" % (f, rcdlist[key][f])

    return
# end printduplicateIDs() ----------------------------------

def joinOnEq (joinname,	# the name for the DataSet created by the join
	  ds1,		# 1st DataSet to join
	  ds2,		# 2nd DataSet
	  field1,	# field in ds1 to join on (on equality)
	  field2,	# field in ds2 to join on
	  ds1Fields,	# list of fields from ds1 to return in the join
	  new1Fields,	# list of the new names of those ds1 fields in the join
	  ds2Fields,	# list of fields from ds2 to return in the join
	  new2Fields	# list of the new names of those ds2 fields in the join
    ):
# Purpose: join DataSets ds1 and ds2 for records whose
#		ds1.field1 = ds2.field2
# Returns: return a new DataSet
# Assumes: both datasets have an index for field1 and field2 respectively.
#	   ds1Fields are a subset of ds1's fields.
#	   ds2Fields are a subset of ds2's fields.
#	   new1Fields has same length as ds1Fields
#	   new2Fields has same length as ds2Fields
#	   new1Fields and new2Fields do not share any names between them
# Effects: 
# Throws : 
    newFieldNames = new1Fields + new2Fields
    
    newDS = DataSet( joinname, newFieldNames)

    for rcd1 in ds1.getRecords():
	value = rcd1[ field1]
	for rcd2 in ds2.indexLookup( field2, value):
	    newRcd = {}
	    copyfields( newRcd, new1Fields, rcd1, ds1Fields)
	    copyfields( newRcd, new2Fields, rcd2, ds2Fields)
	    newDS.addRecord( newRcd)
    
    return newDS
# end joinOnEq() ----------------------------------

def simpleJoinOnEq (joinname, ds1, ds2, field1, field2
    ):
# Purpose: join DataSets ds1 and ds2 for records whose
#		ds1.field1 = ds2.field2.
#		Fields for the join are all the fields from ds1 (w/ "1"
#		concatenated on front) and all fields from ds2 (w/ "2"
#		concatenated on front)
# Returns: return a new DataSet
# Assumes: both datasets have an index for field1 and field2 respectively
# Effects: 
# Throws : 
    newFieldNames1 = []
    newFieldNames2 = []
    for fn in ds1.getFieldNames():
	newFieldNames1.append( "1" + fn)
    for fn in ds2.getFieldNames():
	newFieldNames2.append( "2" + fn)
    
    return joinOnEq(joinname, ds1, ds2, field1, field2,	\
		    ds1.getFieldNames(),		\
		    newFieldNames1,			\
		    ds2.getFieldNames(),		\
		    newFieldNames2)

# end simpleJoinOnEq() ----------------------------------

def copyfields (rcd1,		# record to copy to
		fieldNames1,	# list of fieldnames from rcd1 to copy into
		rcd2,		# record to copy from
		fieldNames2	# list of fieldnames form rcd2 to copy from
    ):
# Purpose: copy fields in rcd2 to rcd1
# Returns: 
# Assumes: len(fieldNames1) == len(fieldNames2)
# Effects: 
# Throws : 
    for i in range(len(fieldNames1)):
        rcd1[ fieldNames1[i]] = rcd2[ fieldNames2[i]]
    
# end copyfields() ----------------------------------

def dupsDictToKeys (dupsDict	# a dups dict, see getDupsDict below
    ):
# Purpose: take a dupsDict and return the set of keys for all dup rcds
# Returns: list of keys in dupsDict
    keys = []

    for fieldname in dupsDict.keys():
	for value in dupsDict[fieldname].keys():
	    for key in dupsDict[fieldname][value]:
		keys.append(key)
    
    return keys
# end dupsDictToKeys() ----------------------------------

#
# CLASSES
#
class DataSet:

    def __init__ (self,
	name,		# printable name of this DataSet
	fieldnames	# list of field names in this DataSet
	):
    # Purpose: constructor
    # Returns: nothing
	self.name = name
	self.fieldnames = fieldnames[:]
	self.records   = {}	# dict of rcds. Dict keys are record keys
	self.nextkey   = 0
	self.indexes   = {}	# dict w/ fieldname -> dict w/ value->
				#  list of rcd keys
	self.sortField = None	# name of the field to use for sorting in
				#  self.printRecords()
				# =None means printRecords() won't sort.
	self.cmpFunc   = None	# name of an optional function to call to
				#  compare two values from self.sortField
				#  for sorting in printRecords()
				# =None means, just use the Python built-in
				#   comparison operators (< > ==)

    # end __init__() class DataSet ------------------------------


    def selectSubset (self,
	name,			# name of the new DataSet to hold the subset
	rcdKeys			# list of keys from this (self) DataSet to
				#  to copy the rcds from to the new DataSet
				# =None means copy all rcds
        ):
    # Purpose: select a subset of the DataSet records and copy them to a new
    #		DataSet.
    # Returns: returns a new DataSet object w/ just the specified records.
    # Assumes: nothing
    # Effects: For the rcds copied to the new DataSet, the _rcdkey values
    #		will be copied from the old DataSet
    #	       No indexes are defined or copied for the new DataSet

	newds = DataSet(name, self.getFieldNames())

	if rcdKeys == None:
	    rcdKeys = self.records.keys()

	for rcdKey in rcdKeys:
	    rcd = self.records[rcdKey]
	    newRcd = rcd.copy()
	    newds.records[rcdKey] = newRcd
	
	newds.nextkey = self.nextkey	# start off key generation
	
	return newds
    # end selectSubset() ----------------------------------

    def addRecord (self,
	rcd		# dict whose keys are the fieldnames
        ):
    # Purpose: add 'rcd' to the data set
    # Returns: returns the key of the new rcd
    # Assumes: 
    # Effects: generates a new key
	
        key = self.newKey()
	self.records[key] = rcd
	self.records[key]['_rcdkey'] = key	# add key as an attr
	self.updateIndexesForNewRecord( key)
	return key
    # end addRecord() ----------------------------------

    def deleteRecords (self,
	keys	# list of keys to delete
        ):
    # Purpose: delete a list of records specified by a list of keys
        
	for key in keys:
	    self.deleteRecord(key)
    # end deleteRecords() ----------------------------------

    def deleteRecord (self,
	key	# delete the record at this key
        ):
    # Purpose: 
        if self.records.has_key( key):
	    self.updateIndexesForDeletedRecord(key)
	    del self.records[key]
    # end deleteRecord() ----------------------------------
    
    def newKey (self):
    # Purpose: return the next key to use for this dataset
    # Returns: int
    # Assumes: 
    # Effects: increments self.nextkey
    # Throws : %%
        key = self.nextkey
	self.nextkey = self.nextkey +1
	return key
    # end newKey() ----------------------------------

    def addField (self,
	fieldname,	# new field to add
	value		# default value to assign to each existing rcd
        ):
    # Purpose: add a new field to each record
	self.fieldnames.append(fieldname)
        for rcd in self.getRecords():
	    rcd[ fieldname] = value
    # end addField() ----------------------------------

    def getRecordByKey (self,
	key
	):
    # Purpose: return a single record given its key
        return self.records[key]
    # end getRecordByKey() ----------------------------------

    def getRecords (self):
    # Purpose: return the list of records
        return self.records.values()
    # end getRecords() ----------------------------------

    def getRecordsByKeys (self,
	keys		# list of record keys
	):
    # Purpose: return the list of records for the specified keys
	rcds = []
	for k in keys:
	    rcds.append(self.records[k])

        return rcds
    # end getRecordsByKeys() ----------------------------------

    def getValues (self, fieldname):
    # Purpose: return the list of distinct values for 'fieldname' in this
    #	       DataSet
    # Assumes: there is an index for 'fieldname'
        return self.indexes[fieldname].keys()
    # end getValues() ----------------------------------

    def getFieldNames (self):
    # Purpose: return the list of fieldnames
        return self.fieldnames
    # end getFieldNames() ----------------------------------
    
    def buildIndexes (self,
	fieldnames	# list of field names to build indexes for
	):
    # Purpose: build indexes for the specified fieldnames, throwing away
    #		any existing indexes (if any)
    # Returns: nothing

	self.indexes = {}
	for fn in fieldnames:
	    self.addIndex(fn)

    # end buildIndexes() ----------------------------------

    def addIndexes (self,
	fieldnames	# list fieldnames to add indexes for
        ):
    # Purpose: (re)build indexes for a list of fieldnames
    #		(don't touch other indexes)
        for fn in fieldnames:
	    self.addIndex(fn)
    # end addIndexes() ----------------------------------
    
    def addIndex (self,
	fieldname	# field name to add index for
        ):
    # Purpose: (re)build an index for the specified fieldname
    #		(don't touch other indexes)

	self.indexes[fieldname] = {}
	for key in self.records.keys():
	    self.updateIndexForNewRecord( fieldname,key)
    # end addIndex() ----------------------------------
    
    def updateIndexesForNewRecord (self,
        key
        ):
    # Purpose:  update all existing indexes for the specified record key
	for fn in self.indexes.keys():
	    self.updateIndexForNewRecord( fn,key)
    # end updateIndexesForNewRecord() ----------------------------------

    def updateIndexForNewRecord (self,
	fieldname,	# fieldname for the index
	key		# the rcd key
        ):
    # Purpose: update the index for 'fieldname' for the new record whose
    #		key is 'key'
        rcd = self.records[key]
	value = rcd[ fieldname]
	if value != None:
	    if self.indexes[fieldname].has_key( value):
		# add key to list
		self.indexes[fieldname][value].append( key)
	    else:
		# start list
		self.indexes[fieldname][value] = [ key]

    # end updateIndexForNewRecord() ----------------------------------

    def updateIndexesForDeletedRecord (self,
        key
        ):
    # Purpose: 
	for fn in self.indexes.keys():
	    self.updateIndexForDeletedRecord( fn,key)
    # end updateIndexesForDeletedRecord() ----------------------------------
    
    def updateIndexForDeletedRecord (self,
	fieldname,
	key
        ):
    # Purpose: %%
        rcd = self.records[key]
	value = rcd[ fieldname]
	if value != None:
	    if self.indexes[fieldname].has_key( value):
		self.indexes[fieldname][value].remove( key)
		if len(self.indexes[fieldname][value]) == 0: #last one
		    del self.indexes[fieldname][value]

    # end updateIndexForDeletedRecord() ----------------------------------
    
    def indexLookup (self,
	 fieldname,
	 value
        ):
    # Purpose: return list of records whose fieldname = value
    # Returns: %%
    # Assumes: we have an index on fieldname
    # Effects: 
    # Throws : 
	listOfRcds = []
	if self.indexes[ fieldname].has_key( value):
	    for key in self.indexes[ fieldname][value]:
		listOfRcds.append( self.records[key])
	
	return listOfRcds
    # end indexLookup() ----------------------------------
    
    def getKeysForDups (self,
	fieldname,	# field to look for dup values in
	omitFirst=0	# =1 means in the list of keys returned
		    	#   omit the key of the 1st rcd for each value
        ):
    # Purpose: return list of keys of records that have duplicate
    #		values for 'fieldname'
    #		- potentially omitting 1st rcd for each value
    # Returns: see purpose
    # Assumes: there is an index on 'fieldname'
    # Example: if you want to delete all rcds w/ duplicate values in "ID" field
    #		    ds.deleteRecords( ds.getKeysForDups("ID"))
    #
    # 	       if you want to delete all rcds w/ duplicate values in "ID" field
    #	       EXCEPT the first rcd w/ each value:
    #		    ds.deleteRecords( ds.getKeysForDups("ID", omitFirst=1))

        keys = []
	dups = self.getDupsDict( [fieldname])
	for value in dups[fieldname].keys():
	    if omitFirst:
		keys = keys + dups[fieldname][value][1:]
	    else:
		keys = keys + dups[fieldname][value]
	
	return keys
    # end getKeysForDups() ----------------------------------
    
    def getDupsDict (self,
	fieldnames	# list of fieldnames to report dups for
        ):
    # Purpose: return a data structure containing all records with
    #		duplicate values for the specified fieldnames.
    # Returns: dict[fieldname] -> dict [value] -> list of rcd keys
    #		with 'value' for that 'fieldname'
    # Assumes: we have indexes on all the fields in fieldnames
	finaldict = {}
	for fn in fieldnames:
	    finaldict[fn] = {}
	    for value in self.indexes[fn].keys():
		if len( self.indexes[fn][value]) > 1:
		    finaldict[fn][value] = self.indexes[fn][value][:]

	return finaldict
    # end getDupsDict() ----------------------------------

    def sortFunc(self,k1,k2):
    # Purpose: sort comparison function for comparing two records, given their
    #	       keys: k1, k2
    # Returns: -1, 0, or 1 based on the record comparison
    # Assumes: self.sortField is set to the name of the field to compare
    #	       (at the moment) assumes ascending order
    #	       self.cmpFunc is None or is bound to a function that takes
    #		  two values from self.sortField and returns -1, 0, or 1
    # Effects: Compares the self.sortField for the specified rcds.
    #	       if self.cmpFunc is not None, then it calls cmpFunc(val1, val2)
    #		 to do the comparison
    #	       if self.cmpFunc IS None, then we just use the Python built-in
    #		 <, >, == comparison operators for the values.

	v1 = self.records[k1][self.sortField]
	v2 = self.records[k2][self.sortField]
	if self.cmpFunc != None:
	    return self.cmpFunc(v1, v2)
	else: 
	    if v1 < v2:
		return -1
	    elif v1 > v2:
		return 1
	    else:
		return 0
    # end sortFunc() -----------------------------------

    def printRecords (self,
	fp,			# open output file to write to
	fieldnames,		# list of fields to print
	keys = None,		# optional list of keys
	delim = '\t',		# optional record delim string
	sortField = None,	# optional field to sort by
	cmpFunc = None,		# optional cmp function for
				#   comparing 2 values in sortField
        ):
    # Purpose: print
        if keys == None:	# no key list specfied
	    keys = self.records.keys()	# print all records
	
	if sortField != None:		# have a sort field
	    self.sortField = sortField	# fieldname used by self.sortFunc
	    self.cmpFunc   = cmpFunc
	    keys = keys[:]
	    keys.sort(self.sortFunc)
	else:
	    self.sortField = None
	    self.cmpFunc   = None
	
	for key in keys:
	    for fn in fieldnames[:-1]:
		value = self.records[ key][ fn]
		if value == None:
		    value = ''
		fp.write("%s%s" % (value, delim))
	    
	    value = self.records[ key][ fieldnames[-1]]	# last field
	    if value == None:
		value = ''
	    fp.write( "%s\n" % value)

    # end printRecords() ----------------------------------

    def printHeaders (self,
	 fp,		# open output file to write to
	 fieldnames,
	 delim = '\t'
        ):
    # Purpose: %%
        for fn in fieldnames[:-1]:
	    fp.write( fn + delim)
	
	fp.write( fieldnames[-1] + '\n')
    # end printHeaders() ----------------------------------

    def getName (self):
    # Purpose: return the name (string)
        return self.name
    # end getName() ----------------------------------
    
    def setName (self,
	 name
        ):
    # Purpose: set the name (string)
        self.name = name
    # end setName() ----------------------------------
    
    def getNumRecords (self):
    # Purpose: return the number of records in the DataSet (int)
        return len(self.records)
    # end getNumRecords() ----------------------------------
    
# End class DataSet ------------------------------------------------------

class TextFileDataSet (DataSet):

    def __init__ (self,
	name,
	filename,
	fieldnames,	# list of fields in the file (in order)
	numheaderlines,	# number of header lines at top of file to skip
	delim='\t'	# the field delimiter
	):
    # Purpose: constructor

	DataSet.__init__(self,name,fieldnames)
	self.filename  = filename
	self.numheaderlines = numheaderlines
	self.delim     = delim

    # end __init__() class TextFileDataSet ------------------------------

    def readRecords (self):
    # Purpose: read the records from the file, if not already read
    # Returns: nothing
    # Assumes: self.records is an empty dictionary ??

	print "opening file %s" % self.filename
	fp = open( self.filename, 'r')
	numRcds = 0		# number of records added

	for i in range(self.numheaderlines):	# skip header lines
	    line = fp.readline()

	linenumber = self.numheaderlines +1
	line = fp.readline()
	while (line != ""):
	    rcd = self.parseLine( line)
	    rcd["_linenumber"] = linenumber
	    rcd = self.processRecord( rcd)
	    if (rcd != None):
		self.addRecord( rcd)
		numRcds = numRcds +1

	    line = fp.readline()
	    linenumber = linenumber +1
	
	fp.close()
	print "   %s lines read (%s header lines), %s records added" \
	    % (linenumber-1, self.numheaderlines, numRcds)

	self.doneReading()

        return
    # end readRecords() ----------------------------------

    def parseLine (self, line
        ):
    # Purpose: parse the currently read 'line'
    # Returns: dictionary representing the line
	global DEBUG
	rcd = {}	# empty dictionary

        fieldvalues = string.split( line, self.delim)
	if DEBUG:
	    print fieldvalues

	while len(fieldvalues[-1]) != 0 and ( \
		fieldvalues[-1][-1] == "\n" or fieldvalues[-1][-1] == "\r"):
	    # last field has '\n' or '\r'
	    fieldvalues[-1] = fieldvalues[-1][0:-1]	# remove it

	for fieldname in self.fieldnames:
	    if (len(fieldvalues) > 0):
		value = fieldvalues[0]
		if value == '':		# value is empty string
		    value = None	# not sure this makes sense in all cases
		del fieldvalues[0]
	    else:
	        value = None
	    #print "fieldname '%s' getting value '%s'" % (fieldname, value)
	    rcd[fieldname] = value
	return rcd
	
    # end parseLine() ----------------------------------

    def processRecord (self, rcd
        ):
    # Purpose: abstract method for subclasses to do any processing for
    #		an individual record before it is added to the rcd list
    # Returns: the updated (or unchanged) rcd. Return None if you do not
    #		want to include the rcd in the rcd list.
        return rcd
    # end processRecord() ----------------------------------

    def doneReading(self):
    # Purpose: abstract method for subclasses to do any post processing
    #		after all lines of the file have been read
	return
    # end doneReading() ------------------------------
    
# End class TextFileDataSet -------------------------------------------------


class DataSetBucketizer:
# IS:   an object that knows how to "bucketize" two DataSets
#
# HAS:  %%
#
# DOES: %%

    def __init__ (self,
	ds1,		# 1st DataSet
	fieldNames1,	# names of fields in ds1 to match
			#  against fields in ds2
	ds2,		# 2nd DataSet
	fieldNames2	# parallel to fieldNames1
	):
    # Purpose: constructor
    # Returns: nothing
    # Assumes: 'fieldNames1' are valid fieldnames for ds1 and have indexes.
    #	       'fieldNames2' are valid fieldnames for ds2 and have indexes.
    #	       len(fieldNames1) == len(fieldNames2)
    # Effects: see Purpose
    # Throws : %%

	self.ds1         = ds1
	self.fieldNames1 = fieldNames1
	self.ds2         = ds2
	self.fieldNames2 = fieldNames2
	self.key1Hash  = {}	# dict mapping each ds1 rcd key to the
				#  BucketItem containing that ds1 rcd
	self.key2Hash  = {}	# dict mapping each ds2 rcd key to the
				#  BucketItem containing that ds2 rcd

				# self.bucketItems is the current set of
				#   all unmerged BucketItems implemented
				#  as a dictionary.
	self.bucketItems = {}	# dict mapping BucketItem Id to BucketItem
	self.idCounter	 = 0	# counter for assigning BucketItem Ids

	self.b0_1	= []	# list of ds2 rcd keys in the 0:1 bucket
	self.b1_0	= []	# list of ds1 rcd keys in the 1:0 bucket
	self.b1_1	= []	# list of (ds1,ds2) rcd key pairs in the 1:1
				#  bucket
	self.b1_n	= []	# list of (ds1 key, [ds2 keys]) pairs
				#   in the 1:n bucket
	self.bn_1	= []	# list of ([ds1 keys], ds2 key) pairs
				#   in the n:1 bucket
	self.bn_m	= []	# list of ([ds1 keys], [ds2 keys]) in the
				#      n:m bucket

    # end __init__() class DataSetBucketizer ------------------------------
    
    def run (self):
    # Purpose: run the bucketizing algorithm, create the buckets
    # Returns: %%
    # Assumes: %%
    # Effects: %%
    # Throws : %%
	
	# initialize BucketItems (one for each ds1 node and ds2 node)
	# and the keyHash

	for rcd1 in self.ds1.getRecords():
	    rcd1Key = rcd1["_rcdkey"]
	    self.key1Hash[ rcd1Key] = self.getNewBucketItem([rcd1Key], [])
		
	for rcd2 in self.ds2.getRecords():
	    rcd2Key = rcd2["_rcdkey"]
	    self.key2Hash[ rcd2Key] = self.getNewBucketItem([], [rcd2Key])

	# iterate through the field arrays, looking for rcds to associate
	for i in range( len(self.fieldNames1)):	# for each fieldname 1/2 pair
	    fn1 = self.fieldNames1[i]
	    fn2 = self.fieldNames2[i]

	    for val in self.ds1.getValues(fn1):	# for each value in ds1
		rcds2 = self.ds2.indexLookup(fn2, val)
		if len(rcds2) > 0:		# that value is in ds2 too
		    rcds1 = self.ds1.indexLookup(fn1, val)
		    for r1 in rcds1:		# for each pair
			for r2 in rcds2:	#  (r1,r2) w/ this value

			    rcd1Key = r1["_rcdkey"]
			    rcd2Key = r2["_rcdkey"]
			    #print "k1=%s k2=%s" % (rcd1Key, rcd2Key)
			    # merge BucketItems containing r1 and r2
			    r1BucketItem = self.key1Hash[ rcd1Key]
			    r2BucketItem = self.key2Hash[ rcd2Key]
			    self.mergeBucketItems( r1BucketItem, r2BucketItem )

			    #self.key1Hash[ 4].printBI()
			    #self.key2Hash[ 5].printBI()
			    #self.key2Hash[ 6].printBI()

	
	# iterate through all the BucketItems to populate the "buckets"

	#self.key2Hash[ 5].printBI()
	#self.key2Hash[ 6].printBI()
	#print
	#for bi in self.bucketItems.values():
	#    bi.printBI()
	
	self.partitionBuckets()
        
    # end run() ----------------------------------
    
    def getNewBucketItem(self,
	rcds1,		# list of rcds from ds1 to put into this BucketItem
	rcds2		# list of rcds from ds2 to put into this BucketItem
	):
    # Purpose: instantiates a new BucketItem
    # Returns: returns the new BucketItem
    # Assumes: 
    # Effects: adds the new BucketItem to our set of BucketItems
    # Throws : 
	bi = BucketItem(self.idCounter, rcds1, rcds2)
	self.bucketItems[ self.idCounter] = bi

	self.idCounter = self.idCounter +1

	return bi

    # end getNewBucketItem() ----------------------------------------

    def mergeBucketItems(self,
	bi1,	# BucketItem
	bi2	# BucketItem
	):
    # Purpose: merge the two BucketItems into one and return the result
    # Returns: merged BucketItem
    # Assumes: 
    # Effects: merges bi2 into bi1 and deletes bi2 from the BucketItem set
    #	       Also updates self.key[12]Hash's for each node in the merged BI.
	
	if bi1 != bi2: 	# distinct BucketItems, merge them
	    for k1 in bi2.getDs1Nodes():	# for each Ds1Node in bi2
		self.key1Hash[k1] = bi1		#  update its dictentry
						#  to point to merged BI

	    for k2 in bi2.getDs2Nodes():	# for each Ds2Node in bi2
		self.key2Hash[k2] = bi1		#  update its dictentry
						#  to point to merged BI

	    bi1.merge(bi2)			# merge bi2 into bi1
	    del self.bucketItems[ bi2.id]	# remove bi2 from cur set

	return bi1
    # end mergeBucketItems() ----------------------------------------
    	
    def partitionBuckets(self):
    # Purpose: partition all the BucketItems into the 1:0, 0:1, 1:1, 1:n
    #	   n:1 and n:m buckets.
    # Returns: nothing

	for bi in self.bucketItems.values():
	    ds1Count = len(bi.getDs1Nodes())
	    ds2Count = len(bi.getDs2Nodes())
	    if   ds1Count == 1 and ds2Count == 0:	# 1:0
		self.b1_0.append(bi.getDs1Nodes()[0])
	    elif ds1Count == 0 and ds2Count == 1:	# 0:1
		self.b0_1.append(bi.getDs2Nodes()[0])
	    elif ds1Count == 1 and ds2Count == 1:	# 1:1
		self.b1_1.append( \
			(bi.getDs1Nodes()[0],bi.getDs2Nodes()[0]))
	    elif ds1Count == 1 and ds2Count >  1:	# 1:n
		self.b1_n.append( \
			(bi.getDs1Nodes()[0],bi.getDs2Nodes()))
	    elif ds1Count >  1 and ds2Count == 1:	# n:1
		self.bn_1.append( \
			(bi.getDs1Nodes(),bi.getDs2Nodes()[0]))
	    elif ds1Count >  1 and ds2Count >  1:	# n:m
		self.bn_m.append( \
			(bi.getDs1Nodes(),bi.getDs2Nodes()))

    # end partitionBuckets() ----------------------------------------
    	
    def get1_0(self):
    # Purpose: return the 1:0 bucket
    # Returns: list of ds1 record keys from 1:0 BucketItems

	return self.b1_0

    # end get1_0() ----------------------------------------
    
    def get0_1(self):
    # Purpose: return the 0:1 bucket
    # Returns: list of ds2 record keys from 0:1 BucketItems

	return self.b0_1

    # end get0_1() ----------------------------------------
    	
    def get1_1(self):
    # Purpose: return the 1:1 bucket
    # Returns: list of ds1, ds2 record key pairs from 1:1 BucketItems

	return self.b1_1

    # end get1_1() ----------------------------------------
    	
    def get1_n(self):
    # Purpose: return the 1:n bucket
    # Returns: list of (ds1 record key, [ds2 keys]) from 1:n BucketItems

	return self.b1_n

    # end get1_n() ----------------------------------------
    	
    def getn_1(self):
    # Purpose: return the n:1 bucket
    # Returns: list of ([ds1 keys], ds2 key) from n:1 BucketItems

	return self.bn_1

    # end getn_1() ----------------------------------------
    	
    def getn_m(self):
    # Purpose: return the n:m bucket
    # Returns: list of ([ds1 keys], [ds2 keys]) from n:m BucketItems

	return self.bn_m

    # end getn_m() ----------------------------------------
    
# End class DataSetBucketizer ------------------------------------------------

    
class BucketItem:
# IS:   a BucketItem is a connected component from the bipartite graph
#	of nodes from DataSets ds1 and ds2 that are being bucketized
#
# HAS:  Two "sets" - one set of nodes representing the rcds from ds1
#	 and one set of nodes representing the rcds from ds2.
#
# DOES: merge two BucketItems and return the merged one.

    def __init__ (self,
	id,		# BucketItem ID
	rcds1,		# list of rcds from ds1 to put into this BucketItem
	rcds2		# list of rcds from ds2 to put into this BucketItem
	):
    # Purpose: constructor
    # Returns: nothing
    # Assumes: 
    # Effects: see Purpose
    # Throws : %%

	self.ds1Nodes = {}	# dict whose keys are the nodes from ds1
	self.ds2Nodes = {}	# dict whose keys are the nodes from ds2
	self.id	      = id
	for r in rcds1:
	    self.ds1Nodes[r] = 1
	for r in rcds2:
	    self.ds2Nodes[r] = 1

    # end __init__() class BucketItem ------------------------------
    
    def merge (self,
	biToMerge		# BucketItem to merge into this one (self)
        ):
    # Purpose: merges BucketItem 'biToMerge' into self
    # Returns: self, the merged BucketItem
    # Assumes: %%
    # Effects: %%
    # Throws : %%

	if self != biToMerge:	# is this how you test for object inequality?
	    for r in biToMerge.ds1Nodes.keys():
		self.ds1Nodes[r] = 1
	    for r in biToMerge.ds2Nodes.keys():
		self.ds2Nodes[r] = 1
	return self

    # end merge() ----------------------------------
    
    def getDs1Nodes (self):
    # Purpose: return the list of nodes from ds1 in this BucketItem
    # Returns: list of nodes

        return self.ds1Nodes.keys()
    # end getDs1Nodes() ----------------------------------
    
    def getDs2Nodes (self):
    # Purpose: return the list of nodes from ds2 in this BucketItem
    # Returns: list of nodes

        return self.ds2Nodes.keys()
    # end getDs2Nodes() ----------------------------------

    def printBI(self):
    # Purpose: print the BucketItem (for debugging purposes)
	print self.ds1Nodes.keys(), self.ds2Nodes.keys()
    # end printBI() --------------------------------------
    
    
# End class BucketItem ------------------------------------------------------


class BucketizerReporter:
# IS:   an object that formats and writes out buckets from a DataSetBucketizer.
#
# HAS:  a DataSetBucketizer (that presumably has be "run")
#
# DOES: outputs buckets to specified output files.
#
# Can imagine expanding this class to define options for how to format various
# bucket outputs (which fields to display, delimiter char, etc.). Perhaps in
# the future...

    def __init__ (self,
	bucketizer	# an already "run" bucketizer
	):
    # Purpose: constructor
    # Returns: nothing
    # Assumes: nothing
    # Effects: see Purpose
    # Throws : nothing

	self.bucketizer = bucketizer

    # end __init__() class BucketizerReporter ------------------------------

    def write_1_0(self,
	fp		# open output filepointer to write to
	):
    # Purpose: write the 1_0 bucket to fp
    # Assumes: associated DataSetBucketizer has been "run"

	keys = []	# list of keys of records to print
	for key in self.bucketizer.get1_0():
	    keys.append(key)

	ds = self.bucketizer.ds1
	ds.printRecords(fp, ds.getFieldNames, keys)

    # end write_1_0() ----------------------------------------
    
    def write_0_1(self,
	fp		# open output filepointer to write to
	):
    # Purpose: write the 0_1 bucket to fp
    # Assumes: associated DataSetBucketizer has been "run"

	keys = []	# list of keys of records to print
	for key in self.bucketizer.get0_1():
	    keys.append(key)

	ds = self.bucketizer.ds2
	ds.printRecords(fp, ds.getFieldNames(), keys)

    # end write_0_1() ----------------------------------------
    	
    def write_1_1(self,
	fp		# open output filepointer to write to
	):
    # Purpose: write the 1_1 bucket to fp
    # Assumes: associated DataSetBucketizer has been "run"
	
	ds1 = self.bucketizer.ds1
	ds2 = self.bucketizer.ds2

	for (k1,k2) in self.bucketizer.get1_1():
	    fp.write("[ 1-1 BucketItem\n")
	    ds1.printRecords(fp, ds1.getFieldNames(), [k1])
	    fp.write("----\n")
	    ds2.printRecords(fp, ds2.getFieldNames(), [k2])
	    fp.write("]\n")

    # end write_1_1() ----------------------------------------
    	
    def write_1_n(self,
	fp		# open output filepointer to write to
	):
    # Purpose: write the 1_n bucket to fp
    # Assumes: associated DataSetBucketizer has been "run"

	ds1 = self.bucketizer.ds1
	ds2 = self.bucketizer.ds2

	for (k1,keys2) in self.bucketizer.get1_n():
	    fp.write("[ 1-n BucketItem\n")
	    ds1.printRecords(fp, ds1.getFieldNames(), [k1])
	    fp.write("----\n")
	    ds2.printRecords(fp, ds2.getFieldNames(), keys2)
	    fp.write("]\n")

    # end write_1_n() ----------------------------------------
    	
    def write_n_1(self,
	fp		# open output filepointer to write to
	):
    # Purpose: write the n_1 bucket to fp
    # Assumes: associated DataSetBucketizer has been "run"

	ds1 = self.bucketizer.ds1
	ds2 = self.bucketizer.ds2

	for (keys1,k2) in self.bucketizer.getn_1():
	    fp.write("[ n-1 BucketItem\n")
	    ds1.printRecords(fp, ds1.getFieldNames(), keys1)
	    fp.write("----\n")
	    ds2.printRecords(fp, ds2.getFieldNames(), [k2])
	    fp.write("]\n")


    # end write_n_1() ----------------------------------------
    	
    def write_n_m(self,
	fp		# open output filepointer to write to
	):
    # Purpose: write the n_m bucket to fp
    # Assumes: associated DataSetBucketizer has been "run"

	ds1 = self.bucketizer.ds1
	ds2 = self.bucketizer.ds2

	for (keys1,keys2) in self.bucketizer.getn_m():
	    fp.write("[ n-m BucketItem\n")
	    ds1.printRecords(fp, ds1.getFieldNames(), keys1)
	    fp.write("----\n")
	    ds2.printRecords(fp, ds2.getFieldNames(), keys2)
	    fp.write("]\n")

    # end write_n_m() ----------------------------------------
# end class BucketizerReporter
