# Testimonials
Some lovely folk in the British Antarctic Survey have provided testimonials 
describing their use of the ensembler...

__Clare Allen, running significant [WRF][1] batches, original motivator 
for the tool:__

> _The model-ensembler is a fantastic tool that saves time, reduces stress and 
significantly decreases the chance of human error when running many model 
configurations._

> _The model-ensembler was invaluable for my work as a postdoc at BAS while I was 
investigating many (Weather Research and Forecasting) WRF model configurations. 
The model parameters I wanted to change were stated in a file in a simple and 
intuitive format along with my model running requirements such as number of 
nodes to run the model. The model-ensembler only needed to be submitted once, 
and it would only submit the model runs after checking that there was enough 
space for the model data and that I had not exceeded my fair usage at that 
moment while using the academic supercomputer. Once a model run had completed, 
the model-ensembler automatically transferred the data to an archive space, 
freeing up space for the next model run. Altogether, this saved me a 
considerable amount of time, at least 1 hour per run, if not more, and this 
soon mounts up when you are submitting tens and hundreds of individual model 
runs. I did not have to set up each model directory, or model setup files. I 
did not have to check for space, nor submit each model run separately. Nor did 
I have to check or worry about space running out. As this is fully automated, 
there was much less chance that I would make a mistake and modify the model 
setup in an unintended way. Using the model-ensembler tool freed up my time, and 
enabled to focus more on the science without being interrupted due to the need 
to set more runs going. The model-ensembler tool is very versatile and can be 
utilised by many models or other computational processes (for example plotting 
a lot of data). The model-ensembler is an exceptional tool and I recommend to 
anyone who needs to submit batches of model runs._

__Rosie Williams, using for [WAVI][2] workflow executions:__

> _I'd say that it would take maybe one day to get an ensemble of 100 WAVI 
runs up and running, and less than an hour with the model ensembler. Then 
the resubmitting and monitoring of jobs would have taken up human time and 
led to down time, when jobs that had timed out were not resubmitted.... 
it's hard to estimate. Maybe if it was say one month of running time per 100 
jobs,  with them all running nicely the whole time in the model ensembler, 
that might have ended up taking an extra week maybe if the jobs had to be 
monitored and resubmitted manually (especially if they needed resubmitting 
on Friday nights!)... It's hard to put a number on how much time it saves._

> _It certainly saves a lot of frustrating and tedium too.....!_

> _In terms of human hours. With model ensembler: 1h set up, minimal monitoring. 
Max 1h/week checking everything is running. 3-5 hours maximum total. Without 
model-ensembler: 8h set up, 2-3 hours for 5 weeks checking and 
resubmitting jobs: approx 18-25 hours._

> _With the manual method, running say 1000 runs would be really horrible. 
With the ensembler, it'd be easy._


__Tom Andersson, used for [IceNet][3] drop and relearn parameter analysis:__

> _In terms of the drop-and-relearn experiment it would comprise about 2,000 
individual training runs, assuming we use 5 random seeds per run. Assuming 
it's 1 hour per training run (which I can't remember exactly but is the 
right order of magnitude) that's a bit over 2 months to compelte with no 
model ensembler parallelisation._

> _It would also have be be finickily set up with SLURM to stop the single job 
after N runs and resubmit or something. All that bespoke stuff could have 
taken me 2 weeks or so to get my head around. With the parallelisation of 
the model ensembler, say 4 job running at a time, we'd get the run-time 
down to 2 weeks, as well as removing the overhead of me having to fiddle 
around with submitting the SLURM jobs, which isn't my area of expertise._

> _So around 2.5 months to around 2 weeks._

[1]: https://github.com/wrf-model/WRF
[2]: https://github.com/RJArthern/WAVI.jl
[3]: https://www.nature.com/articles/s41467-021-25257-4
