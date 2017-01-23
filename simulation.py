import data, models, xlrd

# data processing
raw = xlrd.open_workbook('2017_MCM_Problem_C_Data.xlsx')
data.process_data(raw)


simulator = models.SingleLaneSimulator([])
