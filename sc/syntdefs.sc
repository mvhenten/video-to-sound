SynthDef(\EnvelopedSine, { | out, freq = 440, gate = 1, a=0.1, d=0.1, s=0.5, r=0.5 | 
		var z, smooth;
		smooth = LPF.kr(MouseX.kr(300,1000),2); //portamento
		z = EnvGen.kr(Env.adsr, gate) * SinOsc.ar(smooth, 0, 0.1);
		Out.ar(out, z)
	}).play(s);

(	
SynthDef(\clar, { | y = 0.5, size = 0.5, gate = 1, hue 0.3, x=0.4 | 
		var amp, input, ab, ba, bell, p_diff, p_in, pitch, sound, noise_gate, p_m, shape;
		
   		
   		//shape = Env([1, 0, -0.7, 0, 1], [0.3, 0.1, 0.1, 0.3], [4, -4, 4, -4]).asSignal(512).asWavetable; //super ruig!
   		//shape = Env([0,0,0.7,0.7],[0.5,0.05,0.45],[0,0,0]).asSignal(512).asWavetable;
   		
   		//shape = Env([0,0,0.5,1.5,1.5],[0.5,0.01,0.41,0.09]).asSignal(512).asWavetable;
   		//shape = Env([0,0,0.6,0.4,0.4],[0.5,0.25,0.01,0.24]).asSignal(512).asWavetable;
   		shape = Env([0,0,0.5,2,2],[0.5,0.10,0.30,0.10],[5,5,-10,0]).asSignal(512).asWavetable;
   		
   		pitch = (round( linlin(y,0,1,60,96) , 1)).midicps;
		
		ba = DelayC.ar(InFeedback.ar(10, 1), 100.reciprocal , pitch.reciprocal, 1); //air that has returned 
		
		//size = linlin(size,0,1,0.15,1);			
		p_m = ((K2A.ar(size)) + (size * 0.05 * WhiteNoise.ar))  * EnvGen.ar(Env.cutoff(0.2, 1), gate);    //env sustains 1, release in 0.2
				
		p_diff = p_m - ba;
		
		p_in = Shaper.ar(shape.as(LocalBuf),p_diff,p_m);
		
		ab = DelayC.ar(p_in, 100.reciprocal , pitch.reciprocal, 1); //air at bell
		
		bell = LPF.ar(ab, linlin(hue,0,1,500,3000)); //bell reflection
		
		Out.ar(10, bell); //feedback
		
		sound = HPF.ar(bell,500); 
		 
		Out.ar(0, Pan2.ar(sound,linlin(x,0.2,0.8,1,-1),1) ); //out
	
	}).send(s);//.writeDefFile("/Users/lodewijk/dev/opencv2/svn/video-to-sound/sc/");
)
	
Env([0,0,0.3,2,2],[0.5,0.01,0.39,0.1]).asSignal(512).asWavetable.plot;
Env([0, 0, -0.7, 0, 1], [0.3, 0.1, 0.1, 0.3]).asSignal(512).asWavetable.plot;	
Env([0,0,0.5,0,0],[0.5,0.25,0.01,0.24]).asSignal(512).asWavetable.plot;
Env([0,0,0.5,2,2],[0.5,0.10,0.35,0.05],[5,5,-10,0]).asSignal(512).asWavetable.plot;	
Env([0,0,0.5,2,2],[0.5,0.10,0.30,0.10],[5,5,-10,0]).asSignal(512).asWavetable.plot;	
Env([0,0,0.5,0.5,0,0,1,1], [1,0.1,1,0.1,1,0.1,1],[3,3,3,-10,3,3,3,]).asSignal(512).asWavetable.plot;

SynthDef(\flute, { arg out=0, gate=1, freq=440, amp=1.0, endReflection=0.5, jetReflection=0.5, jetRatio=0.32, noiseGain=0.15, vibFreq=5.925, vibGain=0.0, outputGain=1.0;

	var adsr = (amp*0.2) + EnvGen.ar(Env.adsr(0.005, 0.01, 1.1, 0.01), gate, doneAction: 2);
	var noise = WhiteNoise.ar(noiseGain);
	var vibrato = SinOsc.ar(vibFreq, 0, vibGain);

	var delay = (freq*0.66666).reciprocal;
	var lastOut = LocalIn.ar(1);
	var breathPressure = adsr*Mix([1.0, noise, vibrato]);
	var filter = LeakDC.ar(OnePole.ar(lastOut.neg, 0.7));
	var pressureDiff = breathPressure - (jetReflection*filter);
	var jetDelay = DelayL.ar(pressureDiff, 0.025, delay*jetRatio);
	var jet = (jetDelay * (jetDelay.squared - 1.0)).clip2(1.0);
	var boreDelay = DelayL.ar(jet + (endReflection*filter), 0.05, delay);
	LocalOut.ar(boreDelay);
	Out.ar(out, 0.3*boreDelay*outputGain);
}.scope);


{ arg out=0, gate=1, freq=440, amp=1.0, endReflection=0.5, jetReflection=0.5, jetRatio=0.32, noiseGain=0.15, vibFreq=5.925, vibGain=0.0, outputGain=1.0;

	var adsr = (amp*0.2) + EnvGen.ar(Env.adsr(0.005, 0.01, 1.1, 0.01), gate, doneAction: 2);
	var noise = WhiteNoise.ar(noiseGain);
	var vibrato = SinOsc.ar(vibFreq, 0, vibGain);

	var delay = (freq*0.66666).reciprocal;
	var lastOut = LocalIn.ar(1);
	var breathPressure = adsr*Mix([1.0, noise, vibrato]);
	var filter = LeakDC.ar(OnePole.ar(lastOut.neg, 0.7));
	var pressureDiff = breathPressure - (jetReflection*filter);
	var jetDelay = DelayL.ar(pressureDiff, 0.025, delay*jetRatio);
	var jet = (jetDelay * (jetDelay.squared - 1.0)).clip2(1.0);
	var boreDelay = DelayL.ar(jet + (endReflection*filter), 0.05, delay);
	LocalOut.ar(boreDelay);
	Out.ar(out, 0.3*boreDelay*outputGain);
}.scope



	
a = Synth(\clar);	
a.scope;
a.inspect;
a.set(\x,0.5);
a.set(\size,0.4);
a.set(\hue,0.50);
a.set(\sat,0.50);

a.set(\y,0.5);
a.set(\gate,0);


(
~window = Window ("Slider");
4.do{ |i| 
	var slide;
	slide = Slider(~window, Rect(20, 25 * i, 150, 20));
	slide.action={ |slider|
		var param;
		
		
		
		i.switch(
			0, { param = "x" },
			1, { param = "y" },
			2, { param = "size" },
			3, { param = "hue" }
		);
		i.postln;
		param.postln;
		slider.value.postln;
		 
		s.sendMsg("/n_set",a.nodeID,param,slider.value);
		//msg.inspect; 
		//msg.postln;
	};
};
~window.front;
)


