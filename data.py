import xlrd
import models

data = xlrd.open_workbook('2017_MCM_Problem_C_Data.xlsx')
table = data.sheets()[0]

nrows = table.nrows
ncols = table.ncols

IncRoads = {5: [], 90: [], 405: [], 520: []}
DecRoads = {5: [], 90: [], 405: [], 520: []}

# First Loop
for i in range(1, nrows):
    Route_ID = table.row_values(i)[0]
    SectionLength = table.row_values(i)[2] - table.row_values(i)[1]
    AvgDailyPeakDemand = table.row_values(i)[3]*0.08 # Get the peak hour demand from data
    RoadType = table.row_values(i)[4]
    DecLanes = table.row_values(i)[5]
    IncLanes = table.row_values(i)[6]
    # print('DecLanes/IncLanes', DecLanes, IncLanes)
    comment = table.row_values(i)[8]
    IncDemand = AvgDailyPeakDemand*IncLanes/(DecLanes+IncLanes)
    DecDemand = AvgDailyPeakDemand*DecLanes/(DecLanes+IncLanes)
    incSec = models.Section(SectionLength, IncDemand, IncLanes)
    IncRoads[Route_ID].append(incSec)
    decSec = models.Section(SectionLength, DecDemand, DecLanes)
    DecRoads[Route_ID].append(decSec)

    try:
        incSec.set_delta_demand(IncDemand-IncRoads[Route_ID][-2].demand)
    except IndexError:
        incSec.set_delta_demand(0)

    try:
        decSec.set_next_sec_lanes(DecRoads[Route_ID][-2].lanes)
    except IndexError:
        decSec.set_next_sec_lanes(DecLanes)

    # if there is a comment, it is an intersection section
    if 'Joins' in comment or 'Intersection' in comment or 'intersection' in comment:
        incSec.set_if_intersection()
        decSec.set_if_intersection()

    if RoadType == 'SR':
        incSec.set_ramp_capability(20)
        decSec.set_ramp_capability(20)

# Second Loop
for v in IncRoads.values():
    for i in range(v.__len__()-1):
        incSec = v[i]
        try:
            incSec.set_next_sec_lanes(v[i+1].lanes)
        except IndexError:
            print('?????') # Set lanes with default value

for v in DecRoads.values():
    for i in range(v.__len__()-1):
        decSec = v[i]
        try:
            decSec.set_delta_demand(decSec.demand-v[i+1].demand)
        except IndexError:
            print('?????') # Set lanes with default value

for v in IncRoads.values():
    for sec in v:
        sec.ramp_build()

for v in DecRoads.values():
    for sec in v:
        sec.ramp_build()

if __name__ == '__main__':
    for id, val in IncRoads.items():
        print(id, 'Inc Direction with', val.__len__(), 'sections')
        for sec in val:
            sec.show_my_parameters()
    for id, val in DecRoads.items():
        print(id, 'Dec Direction with', val.__len__(), 'sections')
        for sec in val:
            sec.show_my_parameters()
