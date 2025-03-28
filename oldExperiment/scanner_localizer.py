#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PNI - Skyra or Prisma:
This demo illustrates using hardware.emulator.launchScan() to either start a
real scan, or emulate sync pulses. Emulation is to allow debugging script timing
offline, without requiring a scanner (or a hardware sync pulse generator). 

Visual Localizer Code - The Brain Development Lab
JKY Aug 2021
"""



from __future__ import absolute_import, division, print_function

from builtins import str
from builtins import range
from psychopy import visual, event, core, gui
from psychopy.hardware.emulator import launchScan
from psychopy.hardware import keyboard


# settings for launchScan:
MR_settings = {
    'TR': 2.000,     # duration (sec) per whole-brain volume
    'volumes': 5,    # number of whole-brain 3D volumes per scanning run
    'sync': 'equal', # character to use as the sync timing event; assumed to come at start of a volume
    'skip': 0,       # number of volumes lacking a sync pulse at start of scan (for T1 stabilization)
    'sound': True    # in test mode: play a tone as a reminder of scanner noise
    }
infoDlg = gui.DlgFromDict(MR_settings, title='fMRI parameters', order=['TR', 'volumes'])
if not infoDlg.OK:
    core.quit()

# Run & Number of Stimulus Selection
selectDlg = gui.Dlg(title="Experiment Parameters")
selectDlg.addText('Stimuli Parameters')
selectDlg.addField('Number of Stimuli per Block:')
selectDlg.addField('Run:', choices=["1", "2", "3","4"])
selectDlg.addField('Subject ID:')
ok_data = selectDlg.show()  # show dialog and wait for OK or Cancel
if selectDlg.OK:  # or if ok_data is not None
    print(ok_data)
else:
    print('user cancelled')
    

# Run selection
if selectDlg.data[1] == '1':
    run = 1
elif selectDlg.data[1] == '2':
    run = 2
elif selectDlg.data[1] == '3':
    run = 3
elif selectDlg.data[1] == '4':
    run = 4

# Set stimPerRun for the audiolocalizer using input from the dialogue box
stimPerRun = int(selectDlg.data[0])

# Setup for Button Box - Keyboard Input
key_resp = keyboard.Keyboard()
key_resp.keys = []
key_resp.rt = []
_key_resp_allKeys = []

dataDir = '/Users/gomezlab/Desktop/localizer/logfiles/'
filename = str(selectDlg.data[2])
log_filename = dataDir + filename + '_loc_logfile_run' + str(run) + '.log'

def log_msg(msg, filename=log_filename):
    print(msg)
    with open(filename, 'a') as f:
        f.write(msg + '\n')

win0 = visual.Window(fullscr=False, screen = 0)
globalClock = core.Clock()

# summary of run timing, for each key press:
output = u'vol    onset key\n'
for i in range(-1 * MR_settings['skip'], 0):
    output += u'%d prescan skip (no sync)\n' % i

counter = visual.TextStim(win0, height=.05, pos=(0, 0), color=win0.rgb + 0.5)
output += u"  0    0.000 sync  [Start of scanning run, vol 0]\n"

win = visual.Window([1920, 1080], units = 'pix', screen = 1)
if run == 1:
    message = visual.TextStim(win, text='Starting Run 1. Fixate on the central dot. Remember to press a button when an image repeats itself.')
    message.autoDraw = True
    win.flip()
elif run == 2:
    message = visual.TextStim(win, text='Starting Run 2. Fixate on the central dot. Remember to press a button when an image repeats itself.')
    message.autoDraw = True
    win.flip()
elif run == 3:
    message = visual.TextStim(win, text='Starting Run 3.Fixate on the central dot. Remember to press a button when an image repeats itself.')
    message.autoDraw = True
    win.flip()
elif run == 4:
    message = visual.TextStim(win, text='Almost done! Starting Run 4. Fixate on the central dot. Remember to press a button when an image repeats itself.')
    message.autoDraw = True
    win.flip()    

# launch: operator selects Scan or Test (emulate); see API documentation
vol = launchScan(win0, MR_settings, globalClock=globalClock)
#counter.setText(u"%d volumes\n%.3f seconds" % (0, 0.0))
#counter.draw()
waiting = visual.TextStim(win0, height=.05, pos=(0, 0), color=win0.rgb + 0.5, text = 'Experiment will start when scanner sends equals sign.')
waiting.draw()
win0.flip()



#core.wait(3.0)

duration = MR_settings['volumes'] * MR_settings['TR']
# note: globalClock has been reset to 0.0 by launchScan()
while globalClock.getTime() < duration:
    allKeys = event.getKeys()
    for key in allKeys:
        if key == MR_settings['sync']:
            onset = globalClock.getTime()
            
            # do your experiment code at this point if you want it sync'd to the TR
            ### Start of experiment code ###
            ################################################################################################################
            # This script runs a visual localizer with 2back task in psychopy. The localizer is made of 4 runs with 6 conditions
            # + a baseline. Each condition is presented 7 times (7 blocks) in a run. Within each block (4 Hz/4sec), 8 visual
            # stimuli from that category are presented for 0.5 seconds each. In total, each run is 196 seconds
            # has 49 blocks, and includes an 8 second countdown (3 min 24 sec per run + waiting for scanner time). Each run outputs  
            # a logfile with the time (from experiment start) a button was pressed. Code must be run 4 times - don't forget to change the run #! 
            #
            # Conditions: 0=baseline, 1=face, 2=hand, 3=word, 4=house 5=foot, 6=car
            ################################################################################################################
            # Import modules we'll need for the experiment
            from psychopy import visual, event, core, prefs
            import pandas as pd
            import os
            import glob
            from psychopy.hardware import keyboard
            
            
            ## LOCALIZER CODE
            # Functions used for this script:
            def play_stimuli(condition):
                ''' This function takes creates a block by taking the first n stimuli in the condition list and 
                playing each stimulus for 1 second each. Then, it deletes the n stimuli so that the next time that 
                condition shows up in a run, it starts with the next n stimuli. n is defined by stimPerRun and is
                the number of stimuli you want presented in a block.'''

                # First n stimuli in the block
                stimuli = condition[0:stimPerRun]
                # print(stimuli)
                for i in range(0,len(stimuli)):
                    start = globalClock.getTime()
                    # Select stimulus
                    stimulus = stimuli[i]
                    # Initialize fixation point
                    fixation = visual.Circle(win=win,radius = 5,pos=(0,0), lineColor='red', lineColorSpace='rgb',fillColor='red', fillColorSpace='rgb')
                    # Present image
                    stim = visual.ImageStim(win, image=stimulus, size=[768,768])
                    stim.draw()
                    fixation.draw()
                    win.flip()
                    # Check for keys during the image presentation
                    duration = 0.5
                    end = start + duration
                    _key_resp_allKeys = []
                    
                    while globalClock.getTime() < end:
                        theseKeys = key_resp.getKeys(keyList=['1', '2', '3','4'], waitRelease=False) #button box inputs
                        _key_resp_allKeys.extend(theseKeys)
                        if len(_key_resp_allKeys):
                            key_resp.keys = _key_resp_allKeys[-1].name  # just the last key pressed
                            key_resp.rt = _key_resp_allKeys[-1].rt
                            print(key_resp.keys) # tells you what key was pressed
                            # Store key press duration from start in log file
                            log_msg(str(key_resp.rt))
                            # Set key response back to null
                            _key_resp_allKeys = []
                    # Remove the played stimuli
                    condition.remove(stimuli[i])
                               

            def execute_run(run, c1, c2, c3, c4, c5, c6):
                ''' This function loads the specific run and the corresponding conditions and presents the stimuli
                for the appropriate blocks using play_stimuli '''
                for block in blocks_runs[run]:
                    if block == 0: #baseline
                        print('baseline')
                        win.flip()
                        # Keep fixation point on gray screen
                        fixation = visual.Circle(win=win,radius = 5,pos=(0,0), lineColor='red', lineColorSpace='rgb',fillColor='red', fillColorSpace='rgb')
                        fixation.draw()
                        win.flip()
                        core.wait(4.0) 
                        win.flip()
                    elif block== 1: #face
                        play_stimuli(c1)
                    elif block== 2: #hand
                        play_stimuli(c2)
                    elif block== 3: #word
                        play_stimuli(c3)
                    elif block== 4: #house
                        play_stimuli(c4)
                    elif block== 5: #foot
                        play_stimuli(c5)
                    elif block == 6: #car
                        play_stimuli(c6)
                    
                        
            def countdown():
                ''' This function displays a countdown from 8 to 1 on the screen '''
                win.flip()
                message = visual.TextStim(win, text = '8')
                message.autoDraw = True
                win.flip()
                core.wait(1.0)
                message.text = '7'
                win.flip()
                core.wait(1.0)
                message.text = '6'
                win.flip()
                core.wait(1.0)
                message.text = '5'
                win.flip()
                core.wait(1.0)
                message.text = '4'
                win.flip()
                core.wait(1.0)
                message.text = '3'
                win.flip()    
                core.wait(1.0)            
                message.text = '2'
                win.flip()
                core.wait(1.0)
                message.text = '1'
                win.flip()
                core.wait(1.0)
                message.text = ' '
                win.flip()

            # CD to the correct directory
            os.chdir('/Users/gomezlab/Desktop/localizer/shined')

            # Load in experiment parfile/outline
            blocks_runs = pd.read_csv('~/Desktop/localizer/blocks_runs.csv')

            # How many stimuli should be played per run?
            # stimPerRun = 8  #This should be selected in the window at the start of the experiment

            # Load conditions
            # This CSV has columns for each run-condition combinations. 
            conditions = pd.read_csv('~/Desktop/localizer/2back_half_conditions.csv')

            #The lines below turn these columns into lists we can access in our script.
            #Run 1 Conditions
            r1c1=conditions.r1c1.to_list()
            r1c2=conditions.r1c2.to_list()
            r1c3=conditions.r1c3.to_list()
            r1c4=conditions.r1c4.to_list()
            r1c5=conditions.r1c5.to_list()
            r1c6=conditions.r1c6.to_list()
            #Run 2 Conditions
            r2c1=conditions.r2c1.to_list()
            r2c2=conditions.r2c2.to_list()
            r2c3=conditions.r2c3.to_list()
            r2c4=conditions.r2c4.to_list()
            r2c5=conditions.r2c5.to_list()
            r2c6=conditions.r2c6.to_list()
            #Run 3 Condtions
            r3c1=conditions.r3c1.to_list()
            r3c2=conditions.r3c2.to_list()
            r3c3=conditions.r3c3.to_list()
            r3c4=conditions.r3c4.to_list()
            r3c5=conditions.r3c5.to_list()
            r3c6=conditions.r3c6.to_list()
            #Run 3 Condtions
            r4c1=conditions.r4c1.to_list()
            r4c2=conditions.r4c2.to_list()
            r4c3=conditions.r4c3.to_list()
            r4c4=conditions.r4c4.to_list()
            r4c5=conditions.r4c5.to_list()
            r4c6=conditions.r4c6.to_list()

            # All set up. Time to run the experiment!!!
            # Open a window (window opened at the beginning; screen = 0 is your computer, screen = 1 is the monitor)
#            win = visual.Window([1920, 1080], units = 'pix', screen = 1)
            ## To quit at any time: press command + q. This can be changed in File/Preferences/Key Bindings

            # Execute run picked at the beginning of the scan
            if run == 1:
                # Run 1
                message.text = ' ' # clears the text
                win.flip() 
                countdown()
                execute_run('run1', r1c1,r1c2,r1c3,r1c4,r1c5,r1c6)
            elif run == 2:
                # Run 2
                message.text = ' '
                win.flip() 
                countdown()
                execute_run('run2', r2c1,r2c2,r2c3,r2c4,r2c5,r2c6)
            elif run ==3:
                # Run 3
                message.text = ' '
                win.flip() 
                countdown()
                execute_run('run3', r3c1,r3c2,r3c3,r3c4,r3c5,r3c6)
            elif run ==4:
                # Run 4
                message.text = ' '
                win.flip() 
                countdown()
                execute_run('run4', r4c1,r4c2,r4c3,r4c4,r4c5,r4c6)
                
            win.flip()
            message.text = 'Run finished!:) Please wait...'
            message.autoDraw = True
            win.flip()
            core.wait(5.0)      
            win.close()
            core.quit()

            ### End of experiment code #######################################################

            # for demo just display a counter & time, updated at the start of each TR
            counter.setText(u"%d volumes\n%.3f seconds" % (vol, onset))
            output += u"%3d  %7.3f sync\n" % (vol, onset)
            counter.draw()
            win.flip()
            vol += 1
        else:
            # handle keys (many fiber-optic buttons become key-board key-presses)
            output += u"%3d  %7.3f %s\n" % (vol-1, globalClock.getTime(), str(key))
            if key == 'escape':
                output += u'user cancel, '
                break

t = globalClock.getTime()
win.flip() 

output += u"End of scan (vol 0..%d = %d of %s). Total duration = %7.3f sec" % (vol - 1, vol, MR_settings['volumes'], t)
print(output)

win.close()
core.quit()

