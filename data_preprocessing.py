import xlrd

data = xlrd.open_workbook('2017_MCM_Problem_C_Data.xlsx')
table = data.sheets()[0]

nrows = table.nrows
ncols = table.ncols

for i in range(nrows):
    for j in range(ncols):
        print(table.row_values(i)[j], end = " | ")
    print('')
