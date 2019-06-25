import random

# Ejemplo de implementacion de FIFO
def FIFO(ways, addr_tag, addr_set):
	# Me fijo si alguna de las vias esta vacia, en ese caso devuelvo cual
	way_i=0
	for way in ways:
		if way[addr_set]['valid']==False: 
			return way_i
		way_i+=1
	
	# Si estoy aca es que ninguna esta vacia, tengo que desalojar alguna
	# segun la politica FIFO, es decir tengo que sacar aquella que haya
	# sido ingresada primero, para eso chequeo tengo que devolver la que
	# tenga el stepFirstUse mas viejo (numericamente menor)
	menor_step = ways[0][addr_set]['stepFirstUse']
	way_menor_step=0
	i=0
	for way in ways:
		if way[addr_set]['stepFirstUse'] < menor_step:
			# Encontre el minimo, actualizo
			menor_step=way[addr_set]['stepFirstUse']
			way_menor_step=i
		i+=1
	return way_menor_step
	
# Esta es gratis...
def RANDOM(ways, addr_tag, addr_set):
	# Busco si hay alguna vacia y devuelvo esa si corresponde
	try: return [ way[addr_set]['tag'] for way in ways].index(None)
	except:
		# Estan todas ocupadas, devuelvo cualquiera
		return random.randint(0,len(ways) - 1)
	

# Implementame por favor!
def LRU(ways, addr_tag, addr_set):
	while True:
		print 'Implementame che!!!! (soy LRU)'
		time.sleep(2)
	
# Implementame por favor! (si queres...)
def MRU(ways, addr_tag, addr_set):
	while True:
		print 'Implementame che (si tenes ganas...) !!!! (soy LRU)'
		time.sleep(2)
