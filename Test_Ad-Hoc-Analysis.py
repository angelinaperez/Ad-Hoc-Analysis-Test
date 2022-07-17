import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
%matplotlib inline

filename = "transaction_data.json"
main_df = pd.read_json(filename)
main_df

###################################################################################################################

rawitem_df = main_df.drop("transaction_items", axis=1).join(
             main_df.transaction_items
             .str
             .split(";", expand=True)
             .stack()
             .reset_index(drop=True, level=1)
             .rename('transaction_items')           
             )
rawitem_df

rawitem_df["Month"] = pd.DatetimeIndex(rawitem_df["transaction_date"]).month
rawitem_df["Quantity"] = rawitem_df.transaction_items.str.split(",", expand=True)[2]
rawitem_df["Real Quantity"] = rawitem_df["Quantity"].str.extract("(\d+)").astype(int)
rawitem_df["Item"] = rawitem_df.transaction_items.str.split(",", expand=True)[1]
rawitem_df = rawitem_df.drop(["Quantity"], axis=1)
rawitem_df

ItemCount_df = rawitem_df.groupby(["Month", "Item"],as_index = False)["Real Quantity"].sum().pivot("Month", "Item").fillna(0)
ItemCount_df

ItemCount_df.plot.line(figsize=(25,10))
plt.title("# of Items Bought Every Month")

###################################################################################################################

def split_trans_items(x):
    order = x.split(';')
    item_list = []

    for pack in order:
        tmp_list = pack.split(',')
        item_list.append({"Category":tmp_list[0],"Item":tmp_list[1],"Quantity":[int(i) for i in tmp_list[-1] if i.isdigit()][0]})

    return item_list

main_df["transaction_date"] = pd.to_datetime(main_df["transaction_date"], format="%Y/%m/%d")
main_df["Parsed Items"] = main_df["transaction_items"].apply(split_trans_items)

values = pd.DataFrame(main_df[main_df["Parsed Items"].apply(len)==1]) 
values["Item Dictionary"] = values["Parsed Items"].apply(lambda x: x[0])
values["Category"] = values["Item Dictionary"].apply(lambda x: x["Category"])
values["Item"] = values["Item Dictionary"].apply(lambda x: x["Item"])
values["Quantity"] = values["Item Dictionary"].apply(lambda x: x["Quantity"])
values = values.drop_duplicates(subset="Item", keep="first")

values["Price Value"] = values["transaction_value"] / values["Quantity"]

ItemSale_df = pd.DataFrame(values[["Category", "Item","Price Value"]])
ItemSale_df

MonthlySales = ItemCount_df.copy()

for x in ItemCount_df["Real Quantity"].columns:
    multiplier = ItemSale_df.loc[ItemSale_df["Item"] == x]["Price Value"].values[0]
    MonthlySales[x] = ItemCount_df["Real Quantity"][x] * multiplier

MonthlySales = MonthlySales.drop(columns=["Real Quantity"])
MonthlySales

MonthlySales.plot.bar(figsize=(25,10))
plt.title("Item Count per Month")

MonthlySales.plot(subplots=True, layout=(2,4), figsize=(25,10))

###################################################################################################################

MonthlyTransactions = pd.pivot_table(
    rawitem_df.drop(columns=['transaction_value']), 
    values='Real Quantity', 
    index=['Month'],
    columns=['name'],
    aggfunc=any,
    fill_value = 0
)

MonthlyTransactions = MonthlyTransactions[MonthlyTransactions.columns].replace([True],1)
MonthlyTransactions

def ifRepeater(x):
    tmp_list = []
    for i in x.index:
        if i==1: tmp_list.append(0)
        else:
            if x[i-1] and x[i]: tmp_list.append(1)
            else: tmp_list.append(0)

    return tmp_list

repeaters = MonthlyTransactions.apply(ifRepeater)
repeaters

repeaters_df = repeaters.transpose().apply(pd.value_counts).transpose()[1]
repeaters_df.loc[1] = 0
repeaters_df

repeaters_df.plot(figsize=(25,10))
plt.title("# of Repeaters per month")

def isInactive(x):
    tmp_list = []
    for i in x.index:
        if i==1: tmp_list.append(0) 
        else:
            if any(x[:i]): 
                if x[i]==0: tmp_list.append(1) 
                else: tmp_list.append(0)
            else:
                tmp_list.append(0)
    return tmp_list

inactives_df = inactives.transpose().apply(pd.value_counts).transpose()[1]
inactives_df.loc[1] = 0
inactives_df

inactives_df = inactives.transpose().apply(pd.value_counts).transpose()[1]
inactives_df.loc[1] = 0
inactives_df

inactives_df.loc[2:].plot(figsize=(25,10))
plt.title("Inactives per month")

def isEngaged(x):
    tmp_list = []
    for i in x.index:
        tmp_list.append(all(x[:i])) #if all previous month and in current month there is a transaction, append 1 to tmp_list otherwise 0
    return [1 if i else 0 for i in tmp_list]

engaged_df = engaged.transpose().apply(pd.value_counts).transpose()[1]
engaged_df.loc[1] = 0
engaged_df

engaged_df = engaged.transpose().apply(pd.value_counts).transpose()[1]
engaged_df.loc[1] = 0
engaged_df

engaged_df.plot(figsize=(25,10))

def isNew(x):
    tmp_list = []
    for i in x.index:
        if any(x[:i]):  
            tmp_list.append(1)
            break
        else:
            tmp_list.append(0)
    while (len(tmp_list) != len(x)):
        tmp_list.append(0)
    return tmp_list

new = MonthlyTransactions.apply(isNew)
new

new_df = new.transpose().apply(pd.value_counts).loc[1]
new_df

new_df.plot(figsize=(25,10))
plt.title("New per month")

def isNonRepeater(x):
    if x.tolist().count(1)==1: 
        return x  #if input 'x' pd series have only one '1'
    else: 
        return [0]*6  #otherwise return [0,0,0,0,0,0]
    
nonRepeater = MonthlyTransactions.apply(isNonRepeater) 
nonRepeater

nonRepeater_df = nonRepeater.transpose().apply(pd.value_counts).loc[1]
nonRepeater_df.loc[1] = 0
nonRepeater_df

nonRepeater_df.plot(figsize=(25,10))
plt.title("Non-Repeaters per month")

customerStatus_df = pd.DataFrame({
  "Repeater":repeaters_df,
  "Inactive":inactives_df,
  "Engaged":engaged_df,
  "New":new_df,
  "Non Repeater":nonRepeater_df
})

customerStatus_df

customerStatus_df.plot.bar(figsize=(25,15))
plt.title("Customer Traffic")

customerStatus_df["Non Repeater"].plot.bar(figsize=(25,15), color="purple")
plt.title("Non Repeater")

customerStatus_df["New"].plot.bar(figsize=(25,15), color="r")
plt.title("New")

customerStatus_df["Engaged"].plot.bar(figsize=(25,15), color="g")
plt.title("Engaged")

customerStatus_df["Inactive"].plot.bar(figsize=(25,15), color="orange")
plt.title("Inactive")

customerStatus_df["Repeater"].plot.bar(figsize=(25,15))
plt.title("Repeater")
