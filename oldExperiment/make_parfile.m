%% 
path_stim = '/Volumes/gomez/data/deaf/princetonLoc/code/experiment/shined_all/';
 
%% Make conditions Key 
conditions_key = {0,1,2,3,4,5,6 ; 'Baseline','ASL','ASL Reversed','English','English Reversed','Spanish','Spanish Reversed'}';
save(fullfile(path_stim, 'conditions_key.m'),'conditions_key')
writecell(conditions_key,fullfile(path_stim, 'conditions_key.txt'))

%% The paradigm file is a simple ASCII text file that describes which stimulus was present when. You will need a separate paradigm file for each fMRI run/series. It contains at least 4 columns (any extra columns are ignored).
%   The first column is the onset time (in seconds) of the stimulus relative to the acquisition of the first STORED image in the series (i.e., not including discarded acquisitions or dummy scans).
%   The second column is a numeric ID that codes the condition/event type that was presented at that time.
%   The third column is the stimulus duration.
%   The fourth column is a weight used for parametric modulation analysis (see FsFastParametricModulation)

%% List of video orders of all the runs: 
open(fullfile(path_stim,'stim_file_names_order.txt'));
load(fullfile(path_stim,'stim_order_for_par.mat'))
exp_conditions = codes'; clear codes
 %%
N_stim = 2 + 8*7 + 2; % 2 blanks - beginning and end. then 8 repeats of 7 categories.
stim_duration = 5.5;
countdown = 6;
run_duration = N_stim* stim_duration + countdown; 

% Fix timing - start at one and not at zero! 


%%

for run=1:3
    format shortG
    parfile = nan(N_stim,4);%[];
    parfile(:,1) = round([1:stim_duration:[stim_duration*N_stim]],1);
    parfile(:,2) = floor(exp_conditions(:,run));
    parfile(:,3) = round(stim_duration * ones(N_stim,1),1);
    parfile(:,4) = floor(ones(N_stim,1));
%     parfile(:,5) = parfile(:,2);
%     for i = 1:length(conditions_key)
%         parfile(parfile(:,2)==i,5)={conditions_key{i,2}};
%     end  
    save([path_stim,'langloc_parfile_run',num2str(run),'.par'], 'parfile')
    clear parfile
end

%%