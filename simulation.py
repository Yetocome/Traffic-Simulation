import data, models, xlrd, time


start = time.clock()
# data processing
raw = xlrd.open_workbook('2017_MCM_Problem_C_Data.xlsx')
data.process_data(raw)

simulator = models.SingleLaneSimulator(5) # set virtual hours in simulator

ratio = 0.5

for i, v in data.IncRoads.items():
    simulator.run(v, ratio)

for i, v in data.DecRoads.items():
    simulator.run(v, ratio)


# simulator.run([data.IncRoads[5][20]], 0.5)

end = time.clock()
print('It costs',end-start,'seconds.')
