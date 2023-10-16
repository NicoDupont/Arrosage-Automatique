"""
* -----------------------------------------------------------------------------------
* Last update :   12/09/2023
* Irripi
* Calculate the watering sequence
* -----------------------------------------------------------------------------------
"""

import pandas as pd
import datetime

def ComputeSequence(sequence_number,reference_date,data,global_time_coefficient,delay_time_sequence,min_runtime,max_runtime,debug):
    seq = 'empty'
    for s in range(0,sequence_number):
        s+=1
        if 1==1:
            #print('calculate sequence for irrigation')
            # delete non active solenoid valve
            sv= data[data.active.eq(1) & data.sequence == s] 
            #sv= sv[sv.sequence.eq(1)]
            if not sv.empty:
                # sort by order, group by sequence order and compute real duration
                sv = sv.sort_values(by=['order'])
                sv = sv.groupby(['order'], as_index = False).agg({'duration': [max],'coef':[max]})
                sv['duration'] = ( sv['duration'] * (sv['coef']/100) * (global_time_coefficient/100) ) 
                sv.columns = ["order", "duration", "coef"]

                #compute beginning and end for each sequence
                svlen = len(sv.index)
                sv['cumul'] = 0
                cumul = 0
                for i in range(0,svlen):
                        sv.at[i,'cumul'] = cumul
                        #runtime = ( sv.at[i,'duration'] * (sv.at[i,'coef']/100) * (global_time_coefficient/100) )
                        runtime = sv.at[i,'duration']
                        if  runtime >= min_runtime and runtime <= max_runtime:
                            cumul += runtime 
                        else: 
                            if runtime < min_runtime:
                                cumul += min_runtime 
                            else: 
                                cumul += max_runtime 
                        
                def StartingDate(min1):
                    starting = reference_date + datetime.timedelta(minutes = int(min1)) + datetime.timedelta(seconds = delay_time_sequence)
                    return starting

                def EndDate(min1,min2):
                    end = reference_date + datetime.timedelta(minutes = int(min1) + int(min2))
                    return end

                sv['StartingDate'] = sv.apply(lambda row: StartingDate(row["cumul"]), axis=1)
                sv['EndDate'] = sv.apply(lambda row: EndDate(row["cumul"],row["duration"]), axis=1)

                if debug:
                    print(sv.head())

                if sv.empty and debug:
                    print("empty")
                
                seq = sv[["order","StartingDate","EndDate"]]
            
    return seq
