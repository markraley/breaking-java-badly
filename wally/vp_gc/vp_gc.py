from vp_gc.persist import *

def version_check(ver):
	if (ver < 1 or ver > 1):
		return False
	else:
		return True

def get_high_version():
	return 1

def get_low_version():
	return 1

def init_reorder_map(rmap, ver, seed):
	pass

def write_str(ctx, payload):
    ctx.encoder.writeString(payload) # amf3

def write_int(ctx, payload):
    ctx.encoder.writeInteger(payload) # amf3

def write_Header(ctx, payload):
	write_int(ctx, payload.version)
	write_str(ctx, payload.tag)

def write_GC(ctx, payload):
	write_int(ctx, payload.start_ms)
	write_int(ctx, payload.duration_ms)
	write_int(ctx, payload.tenured_start_kb)
	write_int(ctx, payload.tenured_end_kb)
	write_int(ctx, payload.perm_start_kb)
	write_int(ctx, payload.perm_end_kb)
	write_int(ctx, payload.paused)

def write_LogContents(ctx, payload):
	count = len(payload.entries)
	write_int(ctx, count)
	i = 0
	while (i < count):
		write_GC(ctx, payload.entries[i])
		i = i + 1

def read_str(ctx):
   t = ctx.decoder.readInteger() # amf3
   assert(t == 6)
   return ctx.decoder.readString()

def read_int(ctx):
   t = ctx.decoder.readInteger() # amf3
   assert(t == 4)
   return ctx.decoder.readInteger()

def read_Header(ctx):
	payload = Header()
	payload.version = read_int(ctx)
	payload.tag = read_str(ctx)
	return payload

def read_GC(ctx):
	payload = GC()
	payload.start_ms = read_int(ctx)
	payload.duration_ms = read_int(ctx)
	payload.tenured_start_kb = read_int(ctx)
	payload.tenured_end_kb = read_int(ctx)
	payload.perm_start_kb = read_int(ctx)
	payload.perm_end_kb = read_int(ctx)
	payload.paused = read_int(ctx)
	return payload

def read_LogContents(ctx):
	payload = LogContents()
	payload.entries = []
	count = read_int(ctx)
	i = 0
	while (i < count):
		t = read_GC(ctx)
		payload.entries.append(t)
		i = i + 1
	return payload

