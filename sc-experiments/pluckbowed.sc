
SynthDef(\pluckbow, { |drive_in = 0, 
					drive_point = 0.5, 
					noise_ratio = 0.01, 
					pitch_in = 300, 
					damping = 0.1, 
					refl = 0.90, 
					driver_smoothing = 0.99, 
					auto = 0, 
					pan = 0.5, 
					live = 1
							| 
		
		var fb,inp;
		var dl1,dl2,dr1,dr2,total_d_len,d_len1,d_len2,amp,mfac,slope,lev,tf,enveloped,output;
				
		//1. lev needs to be a value between 0 and 1, when it is constantly 0.2 we get flute like sounds.
		//2. we try to scale drive_in (for example slider values, or mouse-x), in such a way that the derivative
		//of this value (for example mouse speed) can be something like 0.2. Smoothing helps in getting blown and bow sounds
		
		lev = Slope.kr((drive_in * 0.00001)); 
		lev = Integrator.kr(lev, driver_smoothing);
		lev = lev + auto;
		//lev = 0.2; //constant driving, very cool flute like
		
		tf = 0.5 + lev;  //wavetable shape param: higher value -> steeper slope -> pluck  0.001
		
		total_d_len = pitch_in.reciprocal - ControlRate.ir.reciprocal; //correction for controlrate block delay
		d_len1 = drive_point * (total_d_len/2); //two times this one
		d_len2 = (1 - drive_point) * (total_d_len/2); //and two times this one
		
		//audio
		fb = LocalIn.ar(1) * refl;
		//#pitch_anal,hf = Pitch.kr(fb,pitch_in,pitch_in*0.9,pitch_in*1.1); //variables not dynamically settable!!
				
		//our input is a dc offset + noise + whatever was fed back
		inp = K2A.ar((1 - noise_ratio) * lev) + WhiteNoise.ar(noise_ratio * lev);
				
		dl1 = DelayC.ar(fb  , 100.reciprocal , d_len1, 1); //should be relative to pitch
		
		//"varying wavetable" func : y = p - 10^(-3 + 6*p) * x ,  makes it a pluck or a bow
		amp = Amplitude.kr(dl1); //table lookup x -> multiply y with inp 
		slope = pow(8,(-2 + 4 * tf));		
		mfac = tf - amp*slope;
		mfac = mfac.max(0);
		
		
		dl2 = DelayC.ar(dl1 + (inp * mfac), 100.reciprocal , d_len2, 1);  
		enveloped = EnvGen.kr( Env.asr(0.005,0.9,0.05), live, doneAction:2) * Clip.ar(dl2, -0.95 , 0.95); //to avoid ticks on instrument start and stop
		output = enveloped;
		
		
		Out.ar(1, output * pan); //out		
		Out.ar(0, output * (1 - pan)); //out
		
		dr2 = DelayC.ar( LPF.ar(dl2,damping*15000), 100.reciprocal , d_len2, 1); //relative to pitch
		dr1 = DelayC.ar(dr2 - (inp * mfac), 100.reciprocal , d_len1, 1);		
	
		
		LocalOut.ar(dr1); //feedback into dl1
		
	}).writeDefFile();   //writeDefFile("/Users/lodewijk/dev/colours/svn/video-to-sound/sc/"); //writeDefFile("/Users/lodewijk/dev/colours/svn/video-to-sound/sc");


a = Synth("pluckbow", ["auto",0.05,"pitch_in",200,"refl",0.95]);
a.set("live",0);
a = Synth("pluckbow");

a = Synth("pluckbow", ["auto",0.2,"pitch_in",800,"refl",0.99,"damping",0.9]);

Server.local.options.blockSize_(16);  //scsynth -z 16
Server.local.options.blockSize;


//mooi damping 0.8
//refl refl 0.995

