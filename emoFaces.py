#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PNI - Skyra or Prisma:
This demo illustrates using hardware.emulator.launchScan() to either start a
real scan, or emulate sync pulses. Emulation is to allow debugging script timing
offline, without requiring a scanner (or a hardware sync pulse generator). 

Visual Localizer Code - The Brain Development Lab
JKY Aug 2021

EDH Nov 2024: Updated for 2024 psychoPy version + use on PC: 
*updated pathing for use on windows
*emulator no longer part of core so had to work around that:
*emulator needs to be manually installed via Tools->plugin manager->mri emulator
*added code to import installed plugins 
*user needs to make sure vlc media player is installed
*script now hardcoded to run in 'scan' mode, so it expects equal sign to start.
"""

from __future__ import absolute_import, division, print_function
import os 
import sys
import pandas as pd

from builtins import str
from builtins import range
from psychopy import visual, event, core, gui


# 2024 addition to fix bug in emulat1or 
#from psychopy import plugins
#plugins.activatePlugins()

# back to normal:
from psychopy.hardware.emulator import launchScan
from psychopy.hardware import keyboard


# settings for launchScan:
MR_settings = {
    'TR': 2.000,     # duration (sec) per whole-brain volume
    'volumes': 5,    # number of whole-brain 3D volumes per scanning run
    'sync': 'equal', # character to use as the sync timing event; assumed to come at start of a volume
    'skip': 0,       # number of volumes lacking a sync pulse at start of scan (for T1 stabilization)
#    'sound': True    # in test mode: play a tone as a reminder of scanner noise # Commented 2024
    }
infoDlg = gui.DlgFromDict(MR_settings, title='fMRI parameters', order=['TR', 'volumes'])
if not infoDlg.OK:
    core.quit()

# Run & Number of Stimulus Selection
selectDlg = gui.Dlg(title="Experiment Parameters")
selectDlg.addText('Stimuli Parameters')
selectDlg.addField('Number of Stimuli per Block:')
selectDlg.addField('Run:', choices=["1", "2", "3"])
selectDlg.addField('Subject ID:')
ok_data = selectDlg.show()  # show dialog and wait for OK or Cancel
if selectDlg.OK:  # or if ok_data is not None
    print(ok_data)
else:
    print('user cancelled')
    

# Run selection
run = int(selectDlg.data[1])

# Set stimPerRun for the audiolocalizer using input from the dialogue box
stimPerRun = 4

# Setup for Button Box - Keyboard Input
key_resp = keyboard.Keyboard()
key_resp.keys = []
key_resp.rt = []
_key_resp_allKeys = []

# save logFiles
dataDir='/Users/bingli/Desktop/logFiles'
filename = str(selectDlg.data[2])
#log_filename = f'{dataDir}/{filename}_loc_logfile_run_{run}.log'
log_filename = f'{dataDir}/{filename}_loc_logfile_run_{run}.csv'

def log_msg(msg, filename=log_filename):
    print(msg)
    with open(filename, 'a') as f:
        f.write(msg + '\n')

log_dict = {
    'Event Type': [], 
    'Event Value': [], 
}

win0 = visual.Window(fullscr=False, screen = 0)
globalClock = core.Clock()

# summary of run timing, for each key press:
output = u'vol    onset key\n'
for i in range(-1 * MR_settings['skip'], 0):
    output += u'%d prescan skip (no sync)\n' % i

counter = visual.TextStim(win0, height=.05, pos=(0, 0), color=win0.rgb + 0.5)
output += u"  0    0.000 sync  [Start of scanning run, vol 0]\n"

win = visual.Window([1920, 1080], units = 'pix', screen = 1, color='black', fullscr=True)
message = visual.TextStim(win, height=70,
                          text=f'Starting Run {run}. Fixate on the central dot at all time.')
message.autoDraw = True
win.flip()


# launch: operator selects Scan or Test (emulate); see API documentation
vol = launchScan(win0, MR_settings, globalClock=globalClock, mode='Scan') # Added mode param in 2024
#counter.setText(u"%d volumes\n%.3f seconds" % (0, 0.0))
#counter.draw()
waiting = visual.TextStim(win0, height=.05, pos=(0, 0), color=win0.rgb + 0.5, text = 'Experiment will start when scanner sends equals sign.')
waiting.draw()
win0.flip()


# CD to the correct directory
os.chdir('/Users/bingli/Documents/NEU502b_experiment/emoFaces_cropped/lumMatch')
conditions_df = pd.read_csv('/Users/bingli/Documents/NEU502b_experiment/conditions_runs.csv')
blocks_df = pd.read_csv('/Users/bingli/Documents/NEU502b_experiment/emoFaces_blocks.csv')
#Run 1 Conditions
blocks = []
for block_id in range(1,9):
    blocks.append(blocks_df[f'r{run}b{block_id}'].to_list())


#duration = MR_settings['volumes'] * MR_settings['TR']
duration = 60

# note: globalClock has been reset to 0.0 by launchScan()
while globalClock.getTime() < duration: # initially always true, wait 10 seconds for stim to come on
    allKeys = event.getKeys()
    for key in allKeys:
        if key == MR_settings['sync']:
            onset = globalClock.getTime()
            log_dict['Event Type'].append('Sync Time')
            log_dict['Event Value'].append(onset)
            
            # do your experiment code at this point if you want it sync'd to the TR
            ### Start of experiment code ###
            ################################################################################################################
            # This script runs a visual localizer with 2back task in psychopy. The localizer is made of 4 runs with 7 conditions
            # + a baseline. Each condition is presented 8 times (8 blocks) in a run. Within each block (4 Hz/4sec), 8 visual
            # stimuli from that category are presented for 0.5 seconds each. In total, each run is (196)--> 256! seconds
            # has (49)-->64! blocks, and includes an 8 second countdown (4 min 24 sec per run + 3 baseline blocks at end = 4 min 36 sec
            # + waiting for scanner time)--> . Each run outputs  
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
            def play_stimuli(blocks, cond, block_start_time, duration=2):
                ''' This function takes creates a block by taking the first n stimuli in the condition list and 
                playing each stimulus for 1 second each. Then, it deletes the n stimuli so that the next time that 
                condition shows up in a run, it starts with the next n stimuli. n is defined by stimPerRun and is
                the number of stimuli you want presented in a block.'''
                import random

                # First n stimuli in the block
                stimuli = blocks[:stimPerRun]

                # log_dict['Event Type'].append(f'Play Stim Block Start Time')
                # log_dict['Event Value'].append(block_start_time)
                # log_dict['Event Type'].append(f'Stim Duration')
                # log_dict['Event Value'].append(duration)

                # print(stimuli)
                for idx, stimulus in enumerate(stimuli):
                    log_dict['Event Type'].append(f'Stim {idx} Onset')
                    log_dict['Event Value'].append(globalClock.getTime())

                    expected_stim_end_time = block_start_time + (idx + 1) * duration
                    # log_dict['Event Type'].append(f'Stim {idx} Expected Completion')
                    # log_dict['Event Value'].append(expected_stim_end_time)

                    # Initialize fixation point
                    fixation = visual.Circle(win=win,radius = 5,pos=(0,-30), lineColor='red', lineColorSpace='rgb',fillColor='red', fillColorSpace='rgb')
                    # Present image
                    stim = visual.ImageStim(win, image=stimulus,pos=(0, -30))
                    # Present rectangle either in similar or different orientations
                    random_ori = random.randint(0, 3)
                    if cond == 1:
                        log_dict['Event Type'].append(f'Bar Orientation')
                        log_dict['Event Value'].append(float(random_ori))
                    if random_ori == 0:
                        rect1 = visual.Rect(win=win, ori=0, width=100,height=40, pos=(500, 400), lineColor='red', fillColor='red')
                        rect2 = visual.Rect(win=win, ori=90, width=100, height=40, pos=(-500, 400), lineColor='purple', fillColor='purple')
                    elif random_ori == 1:
                        rect1 = visual.Rect(win=win, ori=90, width=100,height=40, pos=(500, 400), lineColor='red', fillColor='red')
                        rect2 = visual.Rect(win=win, ori=0, width=100, height=40, pos=(-500, 400), lineColor='purple', fillColor='purple')
                    elif random_ori == 2:
                        rect1 = visual.Rect(win=win, ori=90, width=100,height=40, pos=(500, 400), lineColor='red', fillColor='red')
                        rect2 = visual.Rect(win=win, ori=90, width=100, height=40, pos=(-500, 400), lineColor='purple', fillColor='purple')
                    else:
                        rect1 = visual.Rect(win=win, ori=0, width=100,height=40, pos=(500, 400), lineColor='red', fillColor='red')
                        rect2 = visual.Rect(win=win, ori=0, width=100, height=40, pos=(-500, 400), lineColor='purple', fillColor='purple')
                    stim.draw()
                    fixation.draw()
                    # add rectangle 
                    rect1.draw()
                    rect2.draw()
                    win.flip()

                    # Check for keys during the image presentation
                    # end = start + duration
                    _key_resp_allKeys = []
                                        
                    while globalClock.getTime() < expected_stim_end_time:
                        theseKeys = key_resp.getKeys(keyList=['1', '2', '3','4'], waitRelease=False) #button box inputs
                        _key_resp_allKeys.extend(theseKeys)
                        if len(_key_resp_allKeys):
                            key_resp.keys = _key_resp_allKeys[-1].name  # just the last key pressed
                            key_resp.rt = _key_resp_allKeys[-1].rt

                            # Store key press duration from start in log file
                            log_dict['Event Type'].append(f'Button Pressed')
                            log_dict['Event Value'].append(float(key_resp.keys))

                            # Set key response back to null
                            _key_resp_allKeys = []
                        allKeys = event.getKeys()
                        if 'q' in allKeys:
                            log_df = pd.DataFrame(log_dict)
                            log_df.to_csv(log_filename)
                            sys.exit()

                    # log_dict['Event Type'].append(f'Stim {idx} Finished')
                    # log_dict['Event Value'].append(globalClock.getTime())
                               

            def execute_run(blocks, execute_run_start_time, stim_per_run, duration=2, instruction_time=3, baseline_time=2):
                ''' This function loads the specific run and the corresponding conditions and presents the stimuli
                for the appropriate blocks using play_stimuli '''

                block_length = instruction_time + baseline_time + stim_per_run * duration
                for idx, block in enumerate(blocks):
                    block_start_time = execute_run_start_time + idx * block_length * 2
                    # log_dict['Event Type'].append(f'Blockx2 {idx} Start')
                    # log_dict['Event Value'].append(block_start_time)
                    for cond in range(2):
                        instruction = visual.TextStim(
                            win, 
                            text="Attend Bars" if cond else "Attend Face", 
                            height=100, 
                            pos=(0, 0), 
                            color='white', 
                        )

                        # Draw instruction
                        instruction.draw()
                        win.flip()
                        # core.wait(instruction_time)
                        # log_dict['Event Type'].append(f'Instruction Start')
                        # log_dict['Event Value'].append(block_start_time + cond * block_length)
                        while globalClock.getTime() < block_start_time + cond * block_length + instruction_time:
                            allKeys = event.getKeys()
                            if 'q' in allKeys:
                                log_df = pd.DataFrame(log_dict)
                                log_df.to_csv(log_filename)
                                sys.exit()
                        win.flip()

                        # baseline period
                        fixation = visual.Circle(win=win,radius = 5,pos=(0,-30), lineColor='red', lineColorSpace='rgb',fillColor='red', fillColorSpace='rgb')
                        fixation.draw()
                        win.flip()
                        # core.wait(baseline_time)
                        # log_dict['Event Type'].append(f'Baseline Start')
                        # log_dict['Event Value'].append(block_start_time + cond * block_length + instruction_time)
                        while globalClock.getTime() < block_start_time + cond * block_length + instruction_time + baseline_time:
                            allKeys = event.getKeys()
                            if 'q' in allKeys:
                                log_df = pd.DataFrame(log_dict)
                                log_df.to_csv(log_filename)
                                sys.exit()
                        win.flip()

                        stimuli_start_time = block_start_time + cond * block_length + instruction_time + baseline_time
                        play_stimuli(block, cond, stimuli_start_time)

                        
            # def countdown(countdown_start, countdown_duration=8):
            #     ''' This function displays a countdown from 8 to 1 on the screen '''
            #     win.flip()
            #     for _ in range(countdown_duration):
            #         message = visual.TextStim(win, text = f'{_}')
            #         message.autoDraw = True
            #         win.flip()
            #         while globalClock.getTime() < countdown_start + _:
            #             pass
            #     message.text = ' '
            #     win.flip()
            def countdown():
                ''' This function displays a countdown from 8 to 1 on the screen '''
                win.flip()
                message = visual.TextStim(win, text = '8', height = 50)
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


            # All set up. Time to run the experiment!!!
            # Open a window (window opened at the beginning; screen = 0 is your computer, screen = 1 is the monitor)
#            win = visual.Window([1920, 1080], units = 'pix', screen = 1)
            ## To quit at any time: press command + q. This can be changed in File/Preferences/Key Bindings

            # Execute run picked at the beginning of the scan
            message.text = ' ' # clears the text
            win.flip() 
            # countdown(countdown_start_time)
            countdown()
            run_start_time = globalClock.getTime()
            execute_run(blocks, run_start_time, stim_per_run=stimPerRun)

            log_df = pd.DataFrame(log_dict)
            log_df.to_csv(log_filename)
            
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
            if key == 'q':
                output += u'user cancel, '
                break

t = globalClock.getTime()
win.flip() 

output += u"End of scan (vol 0..%d = %d of %s). Total duration = %7.3f sec" % (vol - 1, vol, MR_settings['volumes'], t)
print(output)

win.close()
core.quit()
