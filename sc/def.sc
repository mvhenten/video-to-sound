SynthDef(\flute, { arg out=0, gate=1, freq=440, amp=1.0, endReflection=0.5, jetReflection=0.5, jetRatio=0.32, noiseGain=0.15, vibFreq=5.925, vibGain=0.0, outputGain=1.0;
	var panner;
	
	//noiseGain = MouseY.kr(0, 1, \linear);
	
	var adsr = (amp*0.2) + EnvGen.ar(Env.adsr(0.005, 0.01, 1.1, 0.01), gate, doneAction: 2);
	var noise = WhiteNoise.ar( MouseY.kr(0, 1, \linear));
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
	
	panner = Pan2.ar( 0.3*boreDelay*outputGain, 0.5);
	
	Out.ar(out, BLowPass.ar( panner, MouseX.kr(100, 10000, \exponential ) ));
}).store;

a = Synth.new( "flute");
a.set(\freq, 200);
a.set(\freq, 100);
a.set(\freq, 300);
a.set(\noiseGain, 1);
a.set(\vibFreq, 1);
a.set(\vibFreq, 3);
a.set(\vibFreq, 5);
a.set(\vibFreq, 6);
a.set(\vibFreq, 10);
a.free;
{ Saw.ar(XLine.kr(40,4000,6),0.2) }.play;


{ RLPF.ar(Saw.ar([100,250],0.1), XLine.kr(8000,400,5), 0.05) }.play;

play{FreeVerb.ar(RLPF.ar(Saw.ar([440,440], SinOsc.ar(MouseY.kr(220, 440, \linear))), MouseX.kr(400, 10000,\exponential)), 0.6,0.2,0.2) ! 2};

{ SinOsc.ar(WhiteNoise.ar(100, 200)) * 0.1 }.play;
{ BPF.ar(WhiteNoise.ar(0.1.dup), MouseX.kr(40, 17000, 1), 0.2) }.play;
play{RLPF.ar(WhiteNoise.ar(0.3), MouseX.kr(400, 10000, \exponential)}
;
e= EnvGen.kr(Env.asr(0.01, amp, 0.05), gate, doneAction:2);

{ 
	var freq = 59.midicps;
	var sound = CombL.ar( BPF.ar(WhiteNoise.ar(0.1), MouseX.kr(40, 17000, 1), 0.2), 1/freq, 1/freq/2, MouseY.kr(0.01, 1.0, \linear) );
	var amp = Amplitude.kr( sound, 10, 10 );
	var env    = EnvGen.kr(Env.adsr(1, 0.1, 0.9, 0.5, 0.5), 1, doneAction: 0);

//	sound.plot(0.025);
	var pan = Pan2.ar( sound, 0.5) * env;

	pan / ( amp / 0.5  );
	
}.play;

SyntDef("color", {arg note, amp=0.5, pan=0.5, gate=1.0, val=0.5, sat=0.5
	var freq = note.midicps;
	var sound = CombL.ar( BPF.ar(WhiteNoise.ar(0.1), MouseX.kr(40, 17000, 1), 0.2), 1/freq, 1/freq/2, MouseY.kr(0.01, 1.0, \linear) );
	
	var follow = Amplitude.kr( sound, 10, 10 );
	var env    = EnvGen.kr(Env.adsr(1, 0.1, 0.9, 0.5, 0.5), gate, doneAction: 0);

//	sound.plot(0.025);
	var pan = Pan2.ar( sound, 0.5) * env;

	pan / ( follow / 0.5  );

}).send;

Env.adsr(0.4, 0.1, 0.9, 0.2).plot
{SinOsc( 440 )}.scope
Env.adsr(1, 0.1, 0.1, 1, 0.5).plot
[5, 6, 7, 6.5, 4.5, 3.5].plot("Some data")

SynthDef("help-Pan2", { Out.ar(0, Pan2.ar(PinkNoise.ar(0.4), FSinOsc.kr(2), 0.3)) }).play;

{SinOsc.ar(400+SinOsc.ar([10,100],0,[200,100]))}.plot(0.2)

play{
	var mul = MouseX.kr(0.1, 1.0, \linear);
	var osc = SinOsc.ar( 440.dup, 0, mul);	
	var amp = Amplitude.kr( osc, 1, 1 );
	
	var fac = amp/0.5;
	
//	var vol = amp / fac;
	//vol = fac;
	osc / fac;
	//SinOsc.ar( 440.dup, 0, vol);
//	osc * ( mul * mul.reciprocal );
//	osc
}


4.reciprocal
0.5.reciprocal
0.1.reciprocal


