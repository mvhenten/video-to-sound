(
	SynthDef.new("color", {arg out = 0, hue = 0.5, sat = 0.5, val = 0.5,amp = 0.2, gate = 1, panning = 0.5;
		var freq, sound, vol, env, pan, note;
		
		note = 50 + (hue * 12);
		
		panning = (panning * 2) - 1;
		// for experiments
		// val = MouseX.kr( 40, 3500, \linear ); //linexp( val, 0, 1, 500, 17000);
		val = linexp( val, 0, 1, 40, 3500 );
		//amp = linexp( amp, 0, 1, 0, 1);
	
		freq = note.midicps;
		sound = CombC.ar( BLowPass.ar(WhiteNoise.ar(0.5), val, 0.2), 1/freq,1/freq/2, sat );
		vol = Amplitude.kr( sound, 10, 10 );
		env = EnvGen.kr(Env.adsr(1, 0.1, 0.9, 0.5, 0.5), gate, doneAction: 2);
		pan = Pan2.ar( sound, panning) * env;

		//pan / ( vol / amp  );
		//pan * amp;

		Out.ar( out, pan / (vol / amp) );		
	}).writeDefFile;//.send(s);.writeDefFile
)

a = Synth.new("color");
a.set(\gate, 0);
a.set(\gate, 1);

(
~window = Window ("Slider");
4.do{ |i| 
	var slide;
	slide = Slider(~window, Rect(20, 25 * i, 150, 20));
	slide.action={ |slider|
		var param;
		
		
		
		i.switch(
			0, { param = "hue" },
			1, { param = "sat" },
			2, { param = "val" },
			3, { param = "amp" }
		);
		i.postln;
		param.postln;
		slider.value.postln;
		 
		s.sendMsg("/n_set",a.nodeID, param, slider.value);
		//msg.inspect; 
		//msg.postln;
	};
};
~window.front;
)

a = Synth.new("saw");

(
SynthDef.new("saw", {arg out = 0, hue = 0.5, sat = 0.5, val = 0.5,amp = 0.2, gate = 1, pan = 0.5;
		var freq, sound, vol, env, panner, note, detune, pnote;

		note = round( 62 + (hue * 12));

		pan  = (pan * 2) - 1;
		//sat = MouseY.kr(1, 800, \exponential);
		sat  = Lag.kr( linexp( sat, 0, 1, 2000, 1), 0.2);
		val  = Lag.kr( linexp( val, 0, 1, 1000, 4000 ), 0.2);
		
		
		detune =  #[-0.1, -0.07, -0.03, 0, 0.03, 0.07, 0.1];//Array.fill( 8, {arg index; (index*0.1)-(0.5)});
         //detune = #[-0.05, 0, 0.04];
        sound = RHPF.ar(RLPF.ar(
            Mix.ar( Array.fill( detune.size, {arg i;
            	  freq = Lag.kr((note+detune.at(i)).midicps, 0.3);
                Saw.ar(freq);
            })),
            val, 0.05
        ), sat);

		vol = Amplitude.kr( sound, 10, 10 );
		env = EnvGen.kr(Env.adsr(1, 0.1, 0.9, 0.5, 0.5), gate, doneAction: 2);
		panner = Pan2.ar( sound, pan) * env;

		Out.ar( out, panner / (vol / amp) );
	}).send(s);//.writeDefFile();
)

play{
	var freq = 0;
	var	note = 62;
	var detune =  #[-0.1, -0.07, -0.03, 0, 0.03, 0.07, 0.1];
	var val = 0.5;
    var sound = RLPF.ar(
        Mix.ar( Array.fill( detune.size, {arg i;
        	  //freq = Lag.kr((note+detune.at(i)).midicps, 0.3);
            Saw.ar((note + detune.at(i)).midicps);
        })),
        val, 0.05
    );
}

Array.fill( 10, {arg index; (index*0.1)-(0.5)});


