import sc
import time
import random
import thread

print 'hello world........'
print __file__
# we need to tell python where the scserver application lives, this
# changes between platforms and systems. You might need to edit it.
# exedir = 'usr/local' # where does scsynth live?
# sc.start(exedir, verbose=1, spew=1 )

synths = {}

def onDone(msg):
        if msg[1] == "/b_alloc":
            for i in range(512):
                fl = (float(i) / 256) - 1
                if (fl < 0.0):
                    fl = 0
                if (fl > 0.5):
                    fl = 1 - fl
                server = sc.sc.server
                server.sendMsg('/b_set',10,i,fl)

#
# make a group, with the oscillator and some fx modifiers on envelope end the group will get deleted (doneAction 14) 
#
#
def makeSynth(id):
	freq = 440 + int(random.random() * 1000)
	msg = ['/s_new', 'EnvelopedSine', id, 0, 0, 'freq', freq, 'amp', 0.5, 'a', 0.01, 'd', 0.01, 's', 0.01, 'r', 0.9, 'gate', 1]
	#msg = ['/s_new', 'clar', id, 0, 0, 'buf', 10, 'x', 0.2, 'size', 0.4, 'y' , 0.8, 'hue', 0.9]
	
	server = sc.sc.server
	server.sendMsg(*msg);
	#['s_set', 'freq' , 800 sup]
	#synth = sc.Synth( "EnvelopedSine",id,0,0) #node id
	#synth.freq = 440 + int(random.random() * 1000) #to bad we cannot do this in one call, makes this lib usesless!
	#synth.amp = 0.5 #we do not even know if it is already there
	#synth.a = 0.01 #attack ms
	#synth.d = 0.01 #decay ms
	#synth.s = 0.5 #sustaion level
	#synth.r = 0.9 #release ms
	#print "attack"
	#synth.gate = 1	#start the envelope
	return id
	
def stopSynth(id):
	print "release"
	msg = ['n_set',id,'gate',0]
	#msg = ['n_set',id,'gate',0]
	msg = ['n_free',id]
	server.sendMsg(*msg);
	#synth.gate = 0 #release envelope, should free it after finish
	

sc.start( exedir='/Applications/SuperCollider', verbose=1, spew=1 )
server = sc.sc.server ###################
#sc.sc.synthdefpath = '/Users/lodewijk/dev/colours/svn/video-to-sound/sc'
server.sendMsg('/d_loadDir', '/Users/lodewijk/dev/colours/svn/video-to-sound/sc');
sc.register( '/done', onDone ) #
#send commands
#server.sendMsg('/b_alloc',10,512,1);

#wait till it really runs??
time.sleep(1)

c = 0

def bla():
     while True:
         time.sleep(0.01)

thread.start_new_thread(bla, ())

while(1): 
	i = int(20+random.random()*20) #random id
	c += 1
	if (c % 10) == 0:
	    print "quiet"
	    for s in synths:
	        print s
	        stopSynth(s)
	    time.sleep(1)
	    synths = {}
	
	print i
	try:
		synth = synths[i]
		print synth
		stopSynth(synth)
		#do something with it , stop it or change it 
		
		del synths[i]
		
	except KeyError:
		print "create synth " + str(i)
		synths[i] = makeSynth(i)
		
		
	#ids.insert(i,"bla")
	time.sleep(10 * random.random())
	#time.sleep(2)


   
#sine.free()
#sc.quit()

print 'seeya world! ...........'
