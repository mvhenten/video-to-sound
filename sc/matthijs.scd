(
	SynthDef.new("color", {arg out = 0, hue = 0.5, sat = 0.5, val = 0.5,amp = 0.2, gate = 1, panning = 0.5;
		var freq, sound, vol, env, pan, note;
		
		note = 50 + (hue * 8);
		
		panning = (panning * 2) - 1;
		// for experiments
		// val = MouseX.kr( 40, 3500, \linear ); //linexp( val, 0, 1, 500, 17000);
		val = linexp( val, 0, 1, 40, 3500 );
		//amp = linexp( amp, 0, 1, 0, 1);
	
		freq = note.midicps;
		sound = CombL.ar( BPF.ar(WhiteNoise.ar(0.5), val, 0.2), 1/freq,1/freq/2, sat );
		vol = Amplitude.kr( sound, 10, 10 );
		env = EnvGen.kr(Env.adsr(1, 0.1, 0.9, 0.5, 0.5), gate, doneAction: 2);
		pan = Pan2.ar( sound, panning) * env;

		//pan / ( vol / amp  );
		//pan * amp;

		Out.ar( out, pan / (vol / amp) );		
	}).writeDefFile;//.send(s);.writeDefFile
)

Env.adsr(1, 0.5, 0.5, 0.5).plot

0.01.cos
0.1.cos
0.9.cos
0.99.cos

0.01.log2
10.log2
1.log2
2.log2

log10(10)/3


linexp( 0.05, 0.0, 1.0, 0.001, 1.0).cos;
linexp( 0.1, 0.0, 1.0, 0.001, 1.0).cos;
linexp( 0.15, 0.0, 1.0, 0.001, 1.0);
linexp( 0.25, 0.0, 1.0, 0.001, 1.0);
linexp( 0.30, 0.0, 1.0, 0.001, 1.0);
linexp( 0.40, 0.0, 1.0, 0.001, 1.0);
linexp( 0.50, 0.0, 1.0, 0.001, 1.0);
linexp( 0.70, 0.0, 1.0, 0.001, 1.0);
linexp( 0.80, 0.0, 1.0, 0.001, 1.0);
linexp( 0.99, 0.0, 1.0, 0.001, 1.0).cos;
log10(2)

linexp( 10, 0, 1, 40, 17000);

c = Synth.new("color");

c.set( \hue, 0.06);
c.set( \note, 59);
c.set( \val, 0.74);
c.set( \val, 0.1);
c.set( \sat, 0.1);
c.set( \sat, 0.2);
c.set( \sat, 0.3);
c.set( \sat, 0.4);

c.set( \sat, 0.6);
c.set( \sat, 0.9);

c.set( \panning, 0.9);



b = Synth.new("color");
b.set( \note, 55);
b.set( \val, 0.5);
b.set( \val, 0.1);
b.set( \sat, 0.35);
b.set( \sat, 0.6);
b.set( \panning, 0.9);


a = Synth.new("color");
a.set( \note, 40 );
a.set( \val, 0.5);
a.set( \val, 0.1);
a.set( \sat, 0.3);


a.set( \amp, 0.5 );
a.set( \amp, 0.01 );
a.set( \amp, 0.05 );
a.set( \amp, 0.1 );
a.set( \amp, 0.2 );
a.set( \amp, 0.2 );
a.set( \amp, 0.2 );
a.set( \amp, 0.2 );
a.set( \amp, 0.23 );
a.set( \amp, 0.26 );
a.set( \amp, 0.3 );
a.set( \amp, 0.36 );
a.set( \amp, 0.9 );
a.set( \amp, 0.5 );
a.set( \sat, 0.1);
a.set( \panning, 0.1);

a.set( \gate, 0 );
a.set( \gate, 1 );
