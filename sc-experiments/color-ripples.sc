/**
    not sure what's happening but nice for later at night
*/

(
	SynthDef.new("color", {arg out = 0, amp = 1, gate = 1, note = 13, panning = 0.5, vib = 5;
        var sin, env, pan, adsr, vibrato, freq;
        
        //        amp = amp * 2;

        // octave -1, midi note 48 is a "c"
		freq = ( note + 47 ).midicps;	

        // soft virbrato by passing an lfo trough an envelop genrator
        // vibrato faces in trough Env ( attack time 1 second )
        vibrato = SinOsc.ar(vib, 0, 3) * EnvGen.kr(Env.adsr(2, 0.1, 2, 3, -1));        
        freq = freq + vibrato;

    	adsr = EnvGen.ar(Env.adsr( 0, 0.1, 1, 3, 0.5, -4), gate, doneAction: 2);        // generate simple sine wave
        
        // Can do the same with SinOsc, change amp tho
        sin = RLPF.ar(SinOsc.ar([freq,freq],0.1), XLine.kr(8000,400,5), 0.05);
        //sin = RLPF.ar(Saw.ar([freq,freq],0.1), XLine.kr(8000,400,5), 0.05);

        // This adds reverb.
        // change 16 to something higher to make it more "wet"
        //4.do({ sin = AllpassC.ar(sin, 0.02, { Rand(0.001,0.04) }.dup, 3)});

        // scale panning to a -1 .. 1 range
		panning = (panning * 2) - 1;

		// Balance is a stereo mixer, in goes two channels
		pan = Balance2.ar( sin[0], sin[1], panning, 0.1 );

		Out.ar( out, pan * amp );	
	}).send(s);
)

Server.local.options.memSize = 80096;

a = Synth(\color);	

// do re mi
a.set(\note, 1);
a.set(\note, 2);
a.set(\note, 3);
a.set(\note, 4);
a.set(\note, 5);
a.set(\note, 7);
a.set(\note, 9);

// octave higher
a.set(\note, 13); //1
a.set(\note, 14); //2
a.set(\note, 15); //3
a.set(\note, 16); //4
a.set(\note, 17); //5
a.set(\note, 18); //6
a.set(\note, 19); //7
a.set(\note, 20); //8
a.set(\note, 21); //9
a.set(\note, 22); //10
a.set(\note, 23); //11
a.set(\note, 24); //12
a.set(\note, 25); //13
a.set(\note, 13+7);

// switch off and fade out
a.set(\gate, 0);
// full volume
a.set(\amp, 0.1);
