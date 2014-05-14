(
	SynthDef.new("color", {arg out = 0, hue = 0.5, midinote = 1, sat = 0.5, val = 0.5, amp = 0.2, gate = 1, panning = 0.5;
		var freq, sound, vol, env, pan, note;
		
        // 1 + 50 == a c note?
		note = midinote + 50;
		
        // why is this? rounding errors?
		panning = (panning * 2) - 1;
		
		// not exactly sure what val is doing
		// maye bind it to a y coordinate?
		// val = MouseX.kr( 40, 3500, \linear ); //linexp( val, 0, 1, 500, 17000);
		val = linexp( val, 0, 1, 40, 3500 );
	
		freq = note.midicps;
		sound = CombC.ar( BLowPass.ar(WhiteNoise.ar(0.5), val, 0.2), 1/freq,1/freq/2, sat );
		vol = Amplitude.kr( sound, 10, 10 );
		env = EnvGen.kr(Env.adsr(0.2, 0.1, 0.9, 0.5,amp), gate, doneAction: 2);

        // pan is multiplied with enveloped
        // this prevents clicks partially
		pan = Pan2.ar( sound, panning) * env;

		Out.ar( out, pan );		
	}).send(s);//.writeDefFile
)

a = Synth(\color);	

//debugging statments.
// execute per line
a.set(\midinote,1);
a.set(\midinote,2);
a.set(\midinote,3);
a.set(\midinote,6);
a.set(\midinote,8);

a.set(\hue,0.0);
a.set(\sat,1);

a.set(\amp,0.0);
a.set(\amp,0.5);
a.set(\panning,0.5);


a.set(\y,0.5);
a.set(\gate,0);
