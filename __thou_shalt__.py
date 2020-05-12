from time import sleep
import arcpy
from __force_restart__ import force_restart

# TODO: allow registry and state machien to track which commandments are skippable on a restart
# TODO: before forcing termination dump logfile

do_a_dry_run = False
issue_commandments_silently = False
reissue_commandments_interval_seconds = 3.0 #seconds
maximum_reissue_commandments_count = 200

# wrap arcpy function calls with error handeling
COMMANDMENT_NUMBER = 0
def thou_shalt(str_commandment_description, lambda_commandment, execute_on_dry_runs=False):
	'''Call a function repeatedly untill success
	After a number of failiures, simply restart the process and try again.
	I'm sure it will work this time, right?.
	
	str_commandment_description: string to print before attempting to execute function
	lambda_arcpy_commandment: lambda function to be called
	'''
	global COMMANDMENT_NUMBER
	try:
		COMMANDMENT_NUMBER += 1
		if not issue_commandments_silently:
			print "{:<3} THOU SHALT: {}".format(COMMANDMENT_NUMBER, str_commandment_description)
		if not do_a_dry_run or execute_on_dry_runs:
			return lambda_commandment()
		else:
			sleep(0.01)
	except arcpy.ExecuteError as e:
		print "ARCPY HATH FAILED! COMMANDMENT "+str(COMMANDMENT_NUMBER) + " BROKEN: "+str_commandment_description
		print e.message
		error_counter = 1
		flag_not_fulfilled = True
		while flag_not_fulfilled and error_counter<maximum_reissue_commandments_count:
			sleep(reissue_commandments_interval_seconds) # wait
			try:
				# try again
				lambda_commandment()
				# success
				print "arcpy hath repented."
				flag_not_fulfilled = False
			except:
				error_counter +=1
				if error_counter>10:
					print "ARCPY HATH FAILED! COMMANDMENT "+str(COMMANDMENT_NUMBER)+" BROKEN: "+str_commandment_description
					print e.message
				print "Retrying: "+str(error_counter)
				
		if flag_not_fulfilled:
			print "ARCPY, THINE FAILS ARE BEYOND MEASURE, THY SOUL WITHOUT REPENT, I STRIKE YEE DOWN AND UNLOAD YEE FROM MEMORY"
			print("quitting now")
			quit()
			#print "JUDGEMENT DAY IS UPON YEE, ALL SHALL NOW BE DESTROYED AND REBORN IN A NEW PROCESS / THREAD"
			#force_restart()

def thou_shalt_reset_commandment_number():
	global COMMANDMENT_NUMBER
	COMMANDMENT_NUMBER = 0
