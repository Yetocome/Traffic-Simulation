import data, models, xlrd

# data processing
raw = xlrd.open_workbook('2017_MCM_Problem_C_Data.xlsx')
data.process_data(raw)

simulator = models.SingleLaneSimulator()

# for i, v in data.IncRoads.items():
#     simulator.run(v)
#
# for i, v in data.DecRoads.items():
#     simulator.run(v)


simulator.run([data.IncRoads[5][0]])
