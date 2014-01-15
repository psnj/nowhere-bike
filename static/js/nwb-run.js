function nice_interval(secs, with_hours) {
    var hour = Math.floor(secs / 3600);
    var left = secs - (hour * 3600)
    var min = Math.floor(left / 60);
    var sec = left - (min * 60);

    var ch = ( hour < 10 ? "0" : "" ) + hour;
    var cm = ( min < 10 ? "0" : "" ) + min;
    var cs = ( sec < 10 ? "0" : "" ) + sec;
    if (with_hours || hour) {
	return ch + ":" + cm + ":" + cs;
    } else {
	return cm + ":" + cs;
    }
}

function seconds_since(s) {
    return Math.round((now() - s)/1000);
}

var total_elapsed_clock = new Stopwatch();
var pause_clock = new Stopwatch();
var running = false;
var active_stage = null;
var active_stage_ix = -1;
var stages = new Array();

function update_clocks() {
    total_elapsed_clock.tick();
    pause_clock.tick();
    $("#active").html(total_elapsed_clock.elapsed_strtime('disp_hours') + '/' + total_elapsed_clock.remaining_strtime('disp_hours'));
    $("#waste").html(pause_clock.elapsed_strtime('disp_hours'));
    if (active_stage) {
	active_stage.clock.ctick();
	v = $(".stepclock", active_stage.pane);
	v.html(active_stage.clock.remaining_strtime());
    }
}

function now() {
    return new Date().getTime();
}

// A stopwatch.
function Stopwatch() {
    this.accum = 0;
    this.mark = null;
    this.running = false;
    this.start = function() {
	if (!this.running) {
	    this.mark = now();
	    this.running = true;
	}
    }
    this.stop = function() {
	if (this.running) {
	    this.tick();
	    this.running = false;
	}
    }
    this.tick = function() {
	if (this.running) {
	    this.accum += seconds_since(this.mark);
	    this.mark = now();
	}
    }
    this.elapsed_seconds = function() {
	return this.accum;
    }
    this.elapsed_strtime = function(hours) {
	return nice_interval(this.accum, hours);
    }
}

// Like a stopwatch, but also has a duration, so it can count down as
// well.
function Countdown(duration) {
    this.duration = duration;
    this.remaining_seconds = function() {
	return this.duration - this.accum;
    }
    this.remaining_strtime = function(hours) {
	return nice_interval(this.remaining_seconds(), hours);
    }
    this.alarms = new Array();
    this.add_alarm = function(t_minus, fn) {
	this.alarms.push({when: t_minus, callback: fn});
    }
    this.ctick = function() {
	this.tick();
	for (i=0; i<this.alarms.length; i++) {
	    alarm = this.alarms[i];
	    if (!alarm) {
		continue;
	    }
	    if (this.accum >= alarm.when) {
		alarm.callback();
		this.alarms[i] = null;
	    }
	}
	// Shut down if over
	if (this.remaining_seconds() <= 0) {
	    this.running = false;
	}
    }
}

Countdown.prototype = new Stopwatch();

function run_toggle() {
    if (running) {
	$(".clock").css('background-color', 'red');
	total_elapsed_clock.stop();
	pause_clock.start();
	active_stage.clock.stop();
	running = false;
    } else {
	$(".clock").css('background-color', 'yellow');
	total_elapsed_clock.start();
	pause_clock.stop();
	if (active_stage) {
	    active_stage.clock.start();
	} else {
	    select_next_stage();
	}
	running = true;
    }
}

function create_workout(stage_defs) {
    total_dur = 0;
    for (i=0; i<stage_defs.length; i++) {
	sd = stage_defs[i];
	add_stage(sd.dur, sd.d1, sd.d2);
	total_dur += sd.dur;
    }
    total_elapsed_clock = new Countdown(total_dur);
}

function Stage(pane, clock) {
    this.pane = pane;
    this.clock = clock;
}

// Add another stage to the pending list
function add_stage(duration, inst1, inst2) {
    e = $('.stage_template').clone().appendTo('#stagelist');
    e.removeClass('stage_template');
    $(".stepclock", e).html(nice_interval(duration));
    $(".stepinst", e).html(inst1 + '<br><small>' + inst2 + '<small>');
    e.addClass('pending');
    var stage = new Stage(e, new Countdown(duration));
    stage.clock.add_alarm(duration, select_next_stage);
    stage.clock.add_alarm(duration-10, warn);
    stages.push(stage);
    return stage;
}

function warn() { 
    // Highlight the next one
    if (active_stage_ix+1 < stages.length) {
	stages[active_stage_ix+1].pane.addClass('warning');
    }
}

function select_next_stage() {
    // fade out the active stage if there is one
    if (active_stage) {
	active_stage.pane.fadeOut(10);
    }
    if (active_stage_ix < stages.length) {
	active_stage_ix++;
	active_stage = stages[active_stage_ix];
	active_stage.pane.removeClass('pending warning').addClass('current');
	active_stage.clock.start();
    } else {
	total_elapsed_clock.stop();
    }
}

function WS(dur, d1, d2) {
    this.dur = dur;
    this.d1 = d1;
    this.d2 = d2 || '';
}

$(function() {
    create_workout(program);
    window.setInterval("update_clocks()", 999);
    $("#active").click(run_toggle);
});
