from math import log , ceil
#~ import repinf
import random
import numpy as np
import pylab
from collections import defaultdict

from politicas import *
	
class CacheAsociativa_NWays(object):
	
	def __init__(self, memory=range(2**4), cacheSize=8, nWays=2,  nSets=2, cacheAlg=FIFO):
		# memory: array de enteros
		# cacheSize: Tamano de la cache en bytes
		# nWays: cantidad de Ways
		# nSets: cantidad de sets
		# cacheAlg: algoritmo de desalojo
		
		self.memory  = memory
		self.memorySize= len(self.memory)
		self.nWays = nWays
		self.cacheSize= cacheSize
		self.nSets = nSets
		self.cacheAlg = cacheAlg	
		self.sizeSet= self.cacheSize / (self.nWays * self.nSets)
		# stepChange va a guardar en que paso la accedi por ultima vez
		# stepFirstUse va a guardar el step en que lo cree
		self.ways = [ [{'valid':False,'tag': None,'stepChange':-1 ,'stepFirstUse':-1} for ii in range(self.nSets)] for i in range(self.nWays)]
		self.log = []
		self.step=-1
		
		
		# Calculo cantidad de bits para cada campo
		self.nbits_tag = int(ceil(log(ceil(float(self.memorySize) / (self.sizeSet*self.nSets)),2)))
		self.nbits_set = int(ceil(log(self.nSets,2)))
		self.nbits_index= int(ceil(log(self.sizeSet,2)))
		self.nbits_total= self.nbits_index + self.nbits_set  + self.nbits_tag
	
	def _nextStep(self):
		self.step+=1
		return self.step
	
	def getFields(self, address):
		f = self._getFields(address)
		return 'tag: ' + str(f['tag']) + ' set: ' + str(f['set']) + ' index: ' + str(f['index'])
		
	def _getFields(self,address):
		# dada una direccion obtengo a que tag, set e indice corresponde
		assert(self.memorySize > address) #, "address out of range:" + address + ". Memory size:" + self.memorySize
		adress_base2 = ("".join(["0" for i in range(self.nbits_total)])+str(bin(address)[2:]))[-self.nbits_total:]
		
		d_tag= int(adress_base2[:self.nbits_tag],2)
		try: d_set= int(adress_base2[self.nbits_tag:self.nbits_tag+self.nbits_set],2)
		except: d_set=0 # TODO: chequear q este bien esto
		d_index= int(adress_base2[self.nbits_tag+self.nbits_set:],2)
		return {'tag':d_tag,'set':d_set,'index':d_index}
	
	def _fields2Memory(self,tag,set,index):
		binary=("".join(["0" for i in range(self.nbits_total)])+"{0:b}".format(tag))[-self.nbits_tag:]
		binary+=("".join(["0" for i in range(self.nbits_total)])+"{0:b}".format(set))[-self.nbits_set:]
		binary+=("".join(["0" for i in range(self.nbits_total)])+"{0:b}".format(index))[-self.nbits_index:]
		return int(binary,2)
		
	def get_to_plot(self,way=0,set=0):
		t= dict(self.ways[way][set])
		return t
	
	
	def fetch(self, address):
		values_per_field = self._getFields(address)
		newStep = self._nextStep()
		
		# Tengo que revisar si esta guardado en la cache, para eso recorro cada via
		for wi,way in enumerate(self.ways):
			d = way[  values_per_field['set'] ] # Dic con keys: stepChange y tag
			
			if d['tag']== values_per_field['tag']: # Hit!
				
				# Actualizo el tiempo en que fue usado
				self.ways[wi][values_per_field['set'] ]['stepChange']=newStep
				
				# Obtengo el dato de la linea de cache
				dato = self.ways[wi][values_per_field['set']]['mem'][values_per_field['index']]
				
				# Pongo el pedido en el log
				self.appenToLog(address, True, wi, newStep)
								
				return "0x%X" %(dato)
		
		# Si estoy aca es porque no esta en la cache lo que quiero, 
		# uso el algoritmo de desalojo para decidir que via uso
		way2Use= self.cacheAlg(self.ways, values_per_field['tag'], values_per_field['set'])
		self.ways[way2Use][values_per_field['set'] ]['stepFirstUse']=newStep
		self.ways[way2Use][values_per_field['set'] ]['stepChange']=newStep
		self.ways[way2Use][values_per_field['set'] ]['tag']=values_per_field['tag']
		self.ways[way2Use][values_per_field['set'] ]['address_req']=address
		self.ways[way2Use][values_per_field['set'] ]['address']=[ int(self.sizeSet*int(address/self.sizeSet))+i for i in range(self.sizeSet)]
		self.ways[way2Use][values_per_field['set'] ]['mem']=[self.memory[a] for a in self.ways[way2Use][values_per_field['set'] ]['address']]
		self.ways[way2Use][values_per_field['set'] ]['valid']=True
		self.appenToLog(address, False, way2Use, newStep)
		
		# Obtengo el dato de la linea de cache
		dato = self.ways[way2Use][values_per_field['set']]['mem'][values_per_field['index']]
				
		return "0x%X" %(dato)

	def fetchFrom(self, fileName):
		# read memory access list
		access_list = np.array(open(fileName).read().split("\n")) # parse file
		access_list = access_list[access_list != '']  # remove empty elems
		access_list = [int(addr, 16) for addr in access_list] # convert from str to hex
		
		# Hago un fetch de cada direccion de memoria definida en la lista
		for addr in access_list:
			self.fetch(addr)
	
	def appenToLog(self, address, hit, line, newStep):
		self.log.append( {'address':address, 'hit':hit, 'line':line, 'step':newStep})

	def getLineRange(self, nWay, nSet):
		return self.ways[nWay][nSet]['address']

	def info(self):
		# Funcion para printear la cache
		res =""
		res+='Cantidad bits para Tags: '+str(self.nbits_tag)+"\n"
		res+='Cantidad bits para Set: '+str(self.nbits_set)+"\n"
		res+='Cantidad bits para Indice: '+str(self.nbits_index)+"\n"
		res+='Cantidad ways: '+str(self.nWays)+"\n"
		res+='Tamano de cada sets: '+str(self.sizeSet)+"\n"
		res+='Cantidad sets: '+str(self.nSets)+"\n"
		res+='Algoritmo de sustitucion: '+str(self.cacheAlg.func_name)+"\n"
		res+="\n"
		print res

	def __str__(self):
		res ="> Step:"+str(self.step)+"\n"
		
		res+="  "
		for wi in range(self.nWays):
			res+="----------------------------------------"
		res += '\n'
			
		res += '|'
		for wi in range(self.nWays):
			res+='\t\tWay:'+str(wi)+"\t\t\t |"
		res+='\n'
		
		#~ res+='|(tag - stepFirstUse - stepChange)\n'
		for si in range(self.nSets):
			res += '|'
			for way in self.ways:
				if way[si]['tag']==None: res+='\t\tInvalido\t\t |'
				else: 
					res+="\t  Tag:"+str(way[si]['tag'])
					res+=" First:"+str(way[si]['stepFirstUse'])
					res+=" Change:"+str(way[si]['stepChange'])+"\t |"
			res+='\n'
			
		res+="  "
		for wi in range(self.nWays):
			res+="----------------------------------------"
		res += '\n'
		
		res+="Hit rate:"
		if self.step != -1:
			res+=str(self.hitRate())
		else:
			res+='-'
		
		return res				

	def hitRate(self):
		return (np.array([ dict['hit'] for dict in self.log ])==True).mean()

	def infoCache(self,way=0,set=0):
		t= dict(self.ways[way][set])
		print "Dir. pedida","	",t['address_req']
		print "Valido","		",t['valid']
		print "Tag","		",t['tag']
		print "Step 1st use","	",t['stepFirstUse']
		print "Step change","	",t['stepChange']
		print "Linea (Dir. Memoria y contenido):"
		for i in xrange(len(t['address'])):
			print "| 0x%X	" % (int(t['address'][i])),
		print "|"
		for i in xrange(len(t['mem'])):
			print "| %d	" % (t['mem'][i]),
		print "|"


	def mostrarLog(self):
		for c in self.log:
			print '|	Step: %d	|	%s	|	Linea: %d	|	Direccion: %d	|' % (c['step'],'Hit'if c['hit'] else 'Miss',c['line'],c['address'])
		
class CacheTotalmenteAsociativa(CacheAsociativa_NWays):
	
	def __init__(self,memory, cacheSize=8, nLines=2,cacheAlg=FIFO):
		super( CacheTotalmenteAsociativa, self).__init__(memory,cacheSize=cacheSize,nWays=nLines, nSets=1, cacheAlg=cacheAlg)
		
	def get_to_plot(self,line):
		return super(CacheTotalmenteAsociativa, self).get_to_plot(way=line,set=0)

	def getLineRange(self, line):
		return self.ways[line][0]['address']	

	def __str__(self):
		res ="  ----------------Step:"+str(self.step)
		res+="---------------\n"
		
		for way in self.ways:
			res+="|"
			if way[0]['tag']==None: res+='\t\tInvalido\t\t |'
			else: 
				res+="\t  Tag:"+str(way[0]['tag'])
				res+=" First:"+str(way[0]['stepFirstUse'])
				res+=" Change:"+str(way[0]['stepChange'])+"\t |"
			res+='\n'
		res+="  --------------------------------------\n"
		res+="Hit rate: "
		if self.step != -1:
			res+=str(self.hitRate())
		else:
			res+='-'
		return res

	def infoCache(self,line):
		print 'Linea %d:' %(line)
		return super(CacheTotalmenteAsociativa, self).infoCache(way=line,set=0)

class CacheCorrespondenciaDirecta(CacheAsociativa_NWays):
		
	def __init__(self,memory, cacheSize=8, nLines=2):
		super( CacheCorrespondenciaDirecta, self).__init__(memory,cacheSize=cacheSize, nWays=1, nSets=nLines, cacheAlg=FIFO)
		
	def get_to_plot(self,line):
		return super(CacheCorrespondenciaDirecta, self).get_to_plot(way=0,set=line)

	def appenToLog(self, address, hit, line, newStep):
		values_per_field = self._getFields(address)

		self.log.append( {'address':address, 'hit':hit, 'line':values_per_field['set'], 'step':newStep})

	def getLineRange(self, line):
		return self.ways[0][line]['address']

	def __str__(self):
		res ="  ----------------Step:"+str(self.step)
		res+="---------------\n"
		
		way = self.ways[0]
		for si in range(self.nSets):
			res+="|"
			if way[si]['tag']==None: res+='\t\tInvalido\t\t |'
			else: 
				res+="\t  Tag:"+str(way[si]['tag'])
				res+=" First:"+str(way[si]['stepFirstUse'])
				res+=" Change:"+str(way[si]['stepChange'])+"\t |"
			res+='\n'
		res+="  --------------------------------------\n"
		res+="Hit rate: "
		if self.step != -1:
			res+=str(self.hitRate())
		else:
			res+='-'
		return res					

	def infoCache(self,line):
		print 'Linea', str(line) +':'
		return super(CacheCorrespondenciaDirecta, self).infoCache(way=0,set=line)

	
