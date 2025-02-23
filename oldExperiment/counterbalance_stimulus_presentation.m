%
% For body Localizer - counterbalance stimulus presentation with 50% 2-back. 
%
% This script uses the function make_orders.m to Counterbalance categories
% 
% Makes csv files that the psychopy experiment needs,
% And makes .par files that we use for the contrasts. 
% 
%
%%

clear 

% define path to stimuli
path_experiment  = fullfile('/Volumes/gomez/data/deaf/princetonLoc/code/experiment');
path_stimuli = fullfile(path_experiment,'shined');

% Addpath 
addpath(genpath(path_experiment))
cd(path_experiment)
addpath('/Volumes/gomez/code') % for functions used in make_orders 

% Define Experiment Properties: 
num_conds = 8;               % number of categories (faces, bodies, etc)
num_trials_per_cond = num_conds; % num blocks/trials of each category. This has to be a function of num_conds for make_orders to work
num_stim_per_block = 8;      % How many stim (of a single category) are presented within each block
num_orders = 4;              % number of runs
num_blocks_per_run = num_conds * num_trials_per_cond; % trials = blocks

% % Counterbalance categories: using make_orders.m
orders = make_orders(num_conds, num_trials_per_cond, num_orders); % counterbalance categories 
orders = [orders; zeros(3,num_orders)]; % Add three baseline blocks at end of each run
col_names = {'run1';'run2';'run3';'run4'} % Add column names to the exported csv file
orders_w_colnames = [col_names'; num2cell(orders)]; % merge orders with column names
writecell(orders_w_colnames,[path_experiment '/blocks_runs.csv']) % Export to csv file
disp('created block_runs.csv')
clear col_names orders_w_colnames

%% assign specific stimuli per trial in a counterbalanced manner: 

% make 2back_half_conditions.csv file
% This file is required to run the localizer experiment.
% It holds the counterbalanced stimulus names, with 2-back embedded.
% It has columns as the number of conditions x num of runs, 
% as follows: 
% r1c1	r2c1	r3c1	r4c1	r1c2	r2c2	r3c2	r4c2	r1c3	r2c3	r3c3	r4c3	r1c4	r2c4	r3c4	r4c4	r1c5	r2c5	r3c5	r4c5	r1c6	r2c6	r3c6	r4c6		
% Each column holds the stimuli file names for each condition within a
% single run, for example: 
    %face/SHINEd_face-159.jpg
    %face/SHINEd_face-41.jpg
%   .....
% 


col_length = num_stim_per_block * num_trials_per_cond; % The length of the column would be equal to the number of stimuli from each category that is presented in each run.
num_cols = (num_conds-1) * num_orders;  % The number of columns will be defined as (num_conds -1) bc num_conds includes the baseline condition that doesn't need shuffling and thus is not included in the file. 
num_stim_per_cond = num_stim_per_block * num_trials_per_cond * num_orders;% number of stimuli of each type - ACROSS ALL RUNS

stimulus_order = cell(1,num_cols);      % This will be the output file. 

% load category names - 
% Those would be the shined subfolders names, loaded using the dir() function.
all_conds = dir(path_stimuli);
all_conds = {all_conds(3:end).name} % print those into the command line to make sure it looks ok. 

writecell(all_conds,[path_experiment '/categories_order_key.csv']) % Export to csv file


%
%% Fill in stimulus filenames into our output array - stimulus_order
%

for cond = 1:(num_conds-1) % (num_conds-1) bc num_cond includes baseline, for which we don't need to shuffle stimuli
    
    cond_name = all_conds{cond}; % face/body/etc
    all_stimuli_in_dir = dir(fullfile(path_stimuli,cond_name));   % Load all stimuli for this condition
    filenames{cond} = {all_stimuli_in_dir(3:end).name};
    N_stim = length(filenames{cond});                  % N stim in this condition
%     rand_order = randi(N_stim,num_stim_per_cond,1); % random order of stimuli: randi(N_stim) 

    for run = 1:num_orders
        col_ind = ((num_orders)*(cond-1)+run);
%         row_range = col_length*(run-1)+1 : col_length*run; % select a row-range from rand_order
%         stimulus_order{:,col_ind} = filenames{c}(rand_order(row_range))';
%         stimulus_order{:,col_ind} = filenames{cond}(randperm(N_stim,num_stim_per_block))';% NON-REPEATING random integers between 1 and N_stim using the randperm function
        

        for block = 1:num_trials_per_cond
            block_row_range = num_stim_per_block*(block-1)+1 : num_stim_per_block*block; % select a row-range from rand_order
            
            stimulus_order(block_row_range,col_ind) = filenames{cond}(randperm(N_stim,num_stim_per_block))';% NON-REPEATING random integers between 1 and N_stim using the randperm function
        end
        
        % Make 50% of the blocks 2-back 
        zeros_ones_nback   = repmat([0,1], 1,  num_trials_per_cond); % 50% n-back trials
        balanced_2back(:,col_ind)  = zeros_ones_nback(randperm(num_trials_per_cond));      % randomize order: Shuffled indices with no return
    
    end
    
    clear all_stimuli_in_dir zeros_ones_nback N_stim row_range col_ind %rand_order
end

clear cond run block
% 
% %
% % using randperm for selecting the stimuli within each block, we should
% % have no accidental repeats. Now we will push repeats into 50% of the
% % trials to make them 2-back. (we will have some checks later too)
% %
% is_2back    = [0 1];  
% 
% for run = 1:num_orders
%     temp   = repmat(is_2back,1,  num_blocks_per_run/length(is_2back)); % 50% n-back trials
%     balanced_2back(:,run)   = temp(randperm(num_blocks_per_run));      % randomize order: Shuffled indices with no return
%     clear temp
% end

%% replace stimuli in 50% of trials to make them 2-back 
% The 2-back stimulus could be inserted only in slots 3-8 in the blocks
% defines as 2-back blocks in the variable [balanced_2back].

for cond = 1:(num_conds-1) % (num_conds-1) bc num_cond includes baseline, for which we don't need to shuffle stimuli
    
    for run = 1:num_orders
        
        % select which column in the [stimulus_order] array we want to edit
        % to insert the 2-back stimuli:
        col_ind = ((num_orders)*(cond-1)+run); % This is bc of the wierd organization of the stimulus_order columns...
        
        for block = 1:num_trials_per_cond

            if balanced_2back(block,col_ind)==1
                
                % Pick where in the block the repetition/2back is inserted.
                rand_2back_location = randi([3,num_stim_per_block]); % Note that the repetition stimulus could only be inserted in slots 3-8 within the 2-back block.
                
                % change stimulus in this location to be equal to the
                % stimulus in location N-2
                block_row_range = (block-1)*num_stim_per_block+1 : block*num_stim_per_block; % Identify the right rows within the stimulus_order column of interest
%                 stimulus_order{col_ind}{block_row_range(rand_2back_location)} = stimulus_order{col_ind}{block_row_range(rand_2back_location-2)};
                stimulus_order{block_row_range(rand_2back_location),col_ind} = stimulus_order{block_row_range(rand_2back_location-2),col_ind};
            end
        end
    end
end


%%  Add column titles and save out as csv file: 

column_names = {};
counter = 0;
for cond = 1:(num_conds-1) % (num_conds-1) bc num_cond includes baseline, for which we don't need to shuffle stimuli
    for run = 1:num_orders
        counter=counter+1;
        column_names{counter} = ['r' num2str(run) 'c' num2str(cond) ]
    end
end
clear run cond 

% Add column names to stimulus_order:
if length(column_names) == size(stimulus_order,2)
     stimulus_order_2export = [column_names;stimulus_order];  
else
    disp('mismatch in column name length! will not export file!')
end

% Save as csv file 
writecell(stimulus_order_2export,'2back_half_conditions.csv') 
writematrix(balanced_2back,'balanced_2back_key.csv') 
disp('Exported 2back_half_conditions.csv and balanced_2back_key.csv')

%% %%%%%%%%%%%%%%%%%%%%%
% CREATE PAR FILES
%%%%%%%%%%%%%%%%%%%%%%%
% N_stim = 2 + 8*7 + 2; % 2 blanks - beginning and end. then 8 repeats of 7 categories.
% stim_duration = 5.5;
% Fix timing - start at one and not at zero! 

N_blocks = num_blocks_per_run + 3; % 64+ 3 blanks at end of each run % num_blocks_per_run = 64
block_duration = 4; %  each block = 8 stim x 2Hz = 4sec
countdown = 8;

exp_conditions = orders;

conditions_key = {'baseline',all_conds{:}}
for run=1:num_orders
    format shortG
%     parfile = nan(N_blocks,5);%[];
    parfile = nan(N_blocks,4);%[];
    parfile(:,1) = round([1:block_duration:[block_duration*N_blocks]],1);
    parfile(:,2) = floor(exp_conditions(:,run));
    parfile(:,3) = round(block_duration * ones(N_blocks,1),1);
    parfile(:,4) = floor(ones(N_blocks,1));
    
    col_five=cell(N_blocks,1);

    for i = 1:length(parfile)
        col_five{i} = conditions_key{parfile(i,2)+1};
    end
    
    parfile = [num2cell(parfile),col_five]
%     parfile(:,5) = parfile(:,2);
%     for i = 1:length(conditions_key)
% %         parfile(parfile(:,2)==i,5)={conditions_key{i,2}};
% %         parfile(parfile(:,2)==i,5)={conditions_key{i}};
%         parfile(parfile(:,2)==i,5)=conditions_key{i};
%     end  
%     save(fullfile(path_experiment,['BodyLoc_parfile_run',num2str(run),'.par']), 'parfile')
    writecell(parfile, fullfile(path_experiment,['BodyLoc_parfile_run',num2str(run),'.par']),'FileType','text', 'Delimiter','tab')
    clear parfile
end


run_duration = N_blocks* block_duration + countdown; 
N_TRs = ceil(run_duration/2); % In scanner we set it to 139 and fit well!

%%