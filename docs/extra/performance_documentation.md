
# Performance Command

This command runs a performance test for a specific model ID and stores the results in a report file. 

## Introduction
It has been implemented prioritazing low impact when running the model rather than providing hyper-accurate up to date metrics. 
Thus, for the implementation we apply a _delta_ calculation for most metrics. It means we compute the metric before running the model's pipeline and the metric after running it. The difference between values is the impact of running the model (and associated software such as docker) in your machine.
Please notice, this technique can incur in minor deviations on values (e.g., if the operative system performs and update or you are mining bitcoins just when running the model, performance metrics will show worse values).

When performing the test, we run the following pipeline:
0. Start metrics gathering process.
1. Fetch the model. Equivalent to __ersilia fetch model_
2. Serve the model. Equivalent to _ersilia serve model_
3. Generate sample file for the model. Equivalent to _ersilia example -n 5 -f my_input.csv_
4. Run the model. Equivalent to _ersilia run -i my_input.csv -o my_output.csv_
5. Close the model. Equivalent to _ersilia close_
6. End metrics gathering proccess. Generate performance metrics associated with the pipeline mentioned above and store them in a text file.

## Parameters
The command can be customized via the following flags:
|Option / Argument  |Type  |Default Value  |Description  |
|--|--|--|-:|
|Model  |String  |None  |Model to be used for the evaluation pipeline  |
|--file_name, -f  |String  |report.txt  |File where the report is stored  |
|----sleep_time, -s |Int  |10  |Frequency of metrics collection. Lower frequency increases accuracy at the cost for resource footprint.  |

Execution example
````
ersilia performance eos4e40 --file_name report.txt --sleep_time 10
````

## Output
The report includes the following information:
* Hardware configuration. Basic information about your system, including CPU type and avaliable RAM.
* Model selected for evaluation.
* CPU ussage: Including MAX, MIN and AVG CPU Load during process execution.
* Memory ussage: Same as with CPU, measure memory. 
* Duration of test: Measure clock time in seconds.
* Average disk I/O ussage: We compute disk ussage at the start of the test. Then compute the
        lambda (increment) in disk ussage. We return the maximum increment. Ussage is measured
        in CPU time used for disk I/O operations (read and write) which is a good reflection of disk load.
* Average network ussage: Similar to disk, uses a lambda. In this case we compute megabytes received (sent has no impact on performance).

## Testing
Unitary test for CLI function are already implemented. We make sure the report is generated when the function is executed with a valid model, and we check we get an error otherwise. For validating the different performance values we compared them with a task manager (i.e., top command) and verified results are equivalent.

## Future work
List of possible improvements for the function:
* Provide the option to get result in variable devices (e.g., disk and console) and formats (e.g., JSON, HTML)
* Explore the option of implementing a higher footprint check and give the option of lightweight measure computation with lower accuracy or heavy-duty measure computation with higher accuracy (e.g., having the background process identify specific process ids and monitor only those).
* Recommendation: Implementation of different CLI operations (e.g., fetch, performance) should be in an isolated class, so we can use CLI, rest services, lambda functions or whatever in order to enact the functionality
* Recommendation: TBD Derived from previous issues, some cli runs return OKAY even when an exception triggers (i.e., invalid model)

## Further improvements
List of improvements done when executing the task:
* Fixed alphabetical order of functions in cmd.py
