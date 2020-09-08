import sys, getopt

__USAGE = sys.argv[0] + ' -q queue | -t topic'
def parse():
	options, _  = getopt.getopt(
		sys.argv[1:],                      # Arguments
		'q:t:h',                            # Short option definitions
		["queue=", "topic=", "help"]) # Long option definitions
	dest = ''
	for o, a in options:
		if o in ("-h", "--help"):
			print(__USAGE)
			sys.exit()
		elif o in ("-q", "--queueifile"):
			dest = '/queue/' + a
		elif o in ("-t", "--topic"):
			dest = '/topic/' + a
	if dest == '':
		raise SystemExit(__USAGE)
	return dest