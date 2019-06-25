from cache import *
import numpy as np
import pylab

# Correspondencia directa, vario distintas lineas y guardo la hit rate
# para cada configuracion usando la secuencia de fetchs definida en
# benchmark.list
dom = [1,2,4]
res = []
for l in dom:
    ca = CacheCorrespondenciaDirecta(memory=range(0, 2**16),
    cacheSize=128, nLines=l)
    ca.fetchFrom('benchmark.list')
    res.append(  ca.hitRate() )
    print "Lineas:", l, "HitRate:", ca.hitRate()

# res tiene los distintos valores de hit rates para cada configuracion
# uso pylab para plotear
pylab.plot(dom,res,'.-',lw=2,label='CacheCorrespondenciaDirecta - FIFO')
pylab.xticks(size=16)
pylab.yticks(size=16)
pylab.xlim([0,np.max(dom)])
pylab.xlabel('Lineas',size=16)
pylab.ylabel('Hit Rate',size=16)
pylab.title('Cache Correspondencia Directa',size=16)
pylab.show()
