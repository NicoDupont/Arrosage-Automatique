"""
* -----------------------------------------------------------------------------------
* Last update :   16/05/2024
* Arrosage Automatique / IrriPi
* Calculate the watering sequence (start and end of each zone by sequence)(only current day)
* -----------------------------------------------------------------------------------
"""

import pandas as pd
import datetime



def ComputeSequence(sequence_number,reference_date,zone,global_time_coefficient,delay_time_sequence,min_runtime,max_runtime,logger) -> pd.DataFrame:
    
    def StartingDate(min1):
        starting = reference_date + datetime.timedelta(minutes = int(min1)) + datetime.timedelta(seconds = delay_time_sequence)
        return starting

    def EndDate(min1,min2):
        end = reference_date + datetime.timedelta(minutes = int(min1) + int(min2))
        return end

    seq = pd.DataFrame()
    logger.debug('calculate sequence for irrigation sequence number : '+str(sequence_number))
    # remove non active solenoid valve from the dataframe
    sv= zone[zone.active.eq(1) & zone.sequence.str.contains(sequence_number)]

    if not sv.empty:
        logger.debug("zone dans la sequence:")
        logger.debug(sv.head())
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
                runtime = sv.at[i,'duration']
                if  runtime >= min_runtime and runtime <= max_runtime:
                    cumul += runtime 
                else: 
                    if runtime < min_runtime:
                        cumul += min_runtime 
                    else: 
                        cumul += max_runtime 

        sv['StartingDate'] = sv.apply(lambda row: StartingDate(row["cumul"]), axis=1)
        sv['EndDate'] = sv.apply(lambda row: EndDate(row["cumul"],row["duration"]), axis=1)
        sv['sequence'] = sequence_number       
        logger.debug("Head sequence calculée seq : "+str(sequence_number))
        logger.debug(sv.head())
        
        seq = sv[["sequence","order","StartingDate","EndDate"]]
    else:
        logger.warning("Pas de zone dans cette sequence :"+str(sequence_number))
        
    return seq
