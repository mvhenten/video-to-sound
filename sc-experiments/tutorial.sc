(
SynthDef.new("example 5", {arg out = 0, freq, amp = 0.2, 
gate = 1, a, d, s, r;
var env, sin;
env = EnvGen.kr(Env.adsr(a, d, s, r, amp), gate, 
doneAction: 0);
sin = SinOsc.ar(freq, mul:env);
Out.ar(out, sin);
}).send(s);
)
a = Synth.new("example 5", [\freq, 440, \a, 0.2, \d, 0.1, \s, 0.9, \r, 0.5, \gate, 1]);
a.set(\gate, 0);
a.set(\freq, 330, \a, 0.2, \d, 0.1, \s, 0.9, \r, 0.5, \gate, 1);
a.set(\gate, 0);


dfsgdfsg



