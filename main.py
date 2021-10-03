import streamlit as st
import pandas as pd
import plotly.express as px
from functools import reduce
import numpy
import plotly.graph_objects as go

#
df=pd.read_csv("ALL_AMAN.csv")
df['Date']=pd.to_datetime(df['Date'])
df['Month']=df['Date'].dt.month
df['Year']=df['Date'].dt.year
df['period']=df['Month'].astype(str) + "-" + df['Year'].astype(str)
df['period']=pd.to_datetime(df['period'])
df['per']=df['period'].dt.strftime("%Y-%b")

st.header("""
AMAN Hospital - Lost Encounters Dashboard""")

# Radiology
select = st.sidebar.selectbox("Select the department",['select','Radiology','Lab','Cardiac Lab','ENT','Ophthalmology','Urodynamics'])
dfred=df[['ordering_physician','Department','order_completed','guarantor','ordered_test','order_description','order_amount','per']]
dfrad=dfred[dfred['ordered_test'].isin(['X-Ray ','CT','MRI','Mammography','IR-procedure'])]

# radio completed
dfradcomp=dfrad[dfrad['order_completed']=='Yes'].agg(total_charged=('order_amount',sum))
dfradcomp= dfradcomp.reset_index()
dfradcomp['order_amount']=dfradcomp['order_amount'].astype(str)
print(dfradcomp)
# radio noncompleted
dfradnoncomp=dfrad[dfrad['order_completed']=='No'].agg(total_charged=('order_amount',sum))
dfradnoncomp=dfradnoncomp.reset_index()
dfradnoncomp['order_amount']=dfradnoncomp['order_amount'].astype(str)
print(dfradnoncomp)

radmerge=[dfradcomp,dfradnoncomp]
radmerging=reduce(lambda left,right:pd.merge(left,right,on=['index'],how='outer'),radmerge)
# radmerging=radmerging.rename(columns={'0_x':'Radiology_charged','0_y':'Radiology_Lost'})

df2=df[['Department','per','order_completed','order_amount','nationality ']]
print(df2)


if select=='Radiology':
    st.subheader("Period between Jan 2022 and March 2022")
    col1,col2 = st.columns(2)
    col1.metric("Total Radiology Charged","100,972 $")
    col2.metric("Total Radiology Lost orders","20,574 $",delta="-18%")

    st.sidebar.subheader("Radiology Lost Encounters by Department")
    selectb = st.sidebar.selectbox("Select The Period",df2['per'].unique())
    data = df2[df2['per']==selectb]
    data1=data[data['order_completed']=='Yes'].groupby('Department').agg(Total_Charged=('order_amount',sum))
    data1=data1.reset_index('Department')
    data2=data[data['order_completed']=='No'].groupby('Department').agg(Total_lost=('order_amount',sum))
    data2=data2.reset_index('Department')
    mer = [data1,data2]
    merging=reduce(lambda left,right:pd.merge(left,right,on=['Department'],how='outer'),mer)
    merging = merging.fillna(0)

    col1,col2=st.columns(2)
    with col1:
        st.subheader("Radiology billing by department")
        fig=px.histogram(data[data['order_completed'] == 'Yes'], x='Department', y='order_amount',color='Department',width=350)
        st.plotly_chart(fig)



    with col2:
        st.subheader("Radiology Lost billing by department")
        fig1=px.histogram(data[data['order_completed']=='No'],x='Department',y='order_amount',color='Department',width=350)
        st.plotly_chart(fig1)

    st.dataframe(merging)

    st.sidebar.subheader("Departments with Highest contribution to Radiology")
    datam=df2[df2['order_completed']=='Yes']
    multi = st.sidebar.multiselect("Select the department",df2['Department'].unique())
    if len(multi)>0:
        st.subheader("Radioloby Billing by Department and Nationality")
        datam1=datam[datam['Department'].isin(multi)]
        fig2=px.histogram(datam1,x='Department',y='order_amount',facet_col='nationality ',color='nationality ')
        st.plotly_chart(fig2)

    st.subheader("Lost Radiology Encounters by Physician name")
    df3=df[['ordering_physician','order_completed','order_description','order_amount','per']]
    df4=df3[df3['order_completed']=='Yes']
    df5=df4[['ordering_physician','order_amount']]
    df5=df5.groupby('ordering_physician').agg(total_amount_charged=('order_amount',sum))
    df5=df5.reset_index()
    df6=df3[df3['order_completed']=='No']
    df7=df6[['ordering_physician','order_amount']]
    df7=df7.groupby('ordering_physician').agg(total_amount_lost=('order_amount',sum))
    df7=df7.reset_index()
    merger = [df5,df7]
    mergering=reduce(lambda left,right:pd.merge(left,right,on=['ordering_physician'],how='outer'),merger)
    mergering['% Lost out of total ordered']=(mergering['total_amount_lost']/(mergering['total_amount_charged']+mergering['total_amount_lost'])*100).round(2).astype(str) +'%'
    st.write(mergering)


    st.sidebar.subheader("Lost Encounters by Test Type")
    selecta=st.sidebar.selectbox("select period",df3['per'].unique())
    selectc=st.sidebar.selectbox("select physician name",df3['ordering_physician'].unique())
    datap = df3[df3['order_completed'] == 'Yes']
    datapp=df3[df3['order_completed']=='No']
    datat= datap[datap['per']==selecta]
    datadd=datapp[datapp['per']==selecta]
    datat=datat[datat['ordering_physician']==selectc]
    datadd=datadd[datadd['ordering_physician']==selectc]
    col1,col2=st.columns(2)
    with col1:
        st.subheader("Test Orders Charged ")
        fig0 = px.histogram(datat, x='order_description', y='order_amount',width=375)
        st.plotly_chart(fig0)
    with col2:
        st.subheader("Lost Encounters by Test type")
        fig01=px.histogram(datadd,x='order_description',y='order_amount',width=375)
        st.plotly_chart(fig01)

    datatt=datat.groupby('order_description').agg(total_charged=('order_amount',sum))
    datatt=datatt.reset_index()

    datapi=datadd.groupby('order_description').agg(total_lost=('order_amount',sum))
    datapi=datapi.reset_index()
    col1,col2=st.columns(2)
    with col1:
        st.write(datatt)
    with col2:
        st.write(datapi)


# by guarantor and period
    dfc = df[['per','guarantor','order_description','order_amount','order_completed']]
    print(dfc)
    st.sidebar.subheader("Lost Encounters by Guarantor")
    select1=st.sidebar.selectbox("select period",dfc['per'].unique(),key=10)
    select2=st.sidebar.selectbox("select guarantor",dfc['guarantor'].unique(),key=11)
    data10 =dfc[dfc['order_completed']=='Yes']
    data11=dfc[dfc['order_completed']=='No']
    data12=data10[data10['per']==select1]
    data13=data12[data12['guarantor']==select2]
    data14=data11[data11['per']==select1]
    data15=data14[data14['guarantor']==select2]
    col1,col2=st.columns(2)
    with col1:
        st.subheader("Orders Charged by Guarantor")
        fig10 = px.histogram(data13, x='order_description', y='order_amount', color='order_description',width=375)
        st.plotly_chart(fig10)
    with col2:
        st.subheader("Lost Encounter by Guarantor")
        fig11=px.histogram(data15,x='order_description',y='order_amount',width=375,color='order_description')
        st.plotly_chart(fig11)


    # col1,col2=st.columns(2)
    # with col1:
    #     st.subheader("Orders Charged in Radiology")
    #     fig20=go.Figure()
    #     fig20.add_trace(go.Bar(name="X-Ray Knee",x=data13['order_description'],y=data13['order_amount'],legendrank=1))
    #     # fig20.add_trace(go.Bar(name="CT",x=data13['order_description'],y=data13['order_amount'],legendrank=2))
    #
    #     st.plotly_chart(fig20)
# with col1:
#         st.subheader("CT Done by Department")
#         fig=go.Figure()
#         fig.add_trace(go.Bar(name="Neurology", x=mergf['Month'], y=mergf['CT_Neurology_Done'], legendrank=1))
#         fig.add_trace(go.Bar(name="Cardiology", x=mergf['Month'], y=mergf['CT_Cardiology_Done'], legendrank=2))
#         fig.add_trace(go.Bar(name="General_Surgery", x=mergf['Month'], y=mergf['CT_General_Surgery_Done'], legendrank=3))
#         fig.add_trace(go.Bar(name="ENT", x=mergf["Month"], y=mergf['CT_ENT_Done'], legendrank=4))
#         fig.update_layout(
#             autosize=False,
#             width=350,
#             height=350,
#             paper_bgcolor="LightSteelBlue",
#         )
#         fig.update_yaxes(showticklabels=False)
#         st.plotly_chart(fig)

# chart with day in x axis
dft= df[['procedure_time','Department','order_completed','ordered_test']]
dft=dft[dft['order_completed']=='Yes']
dft=dft.drop('order_completed',axis=1)
dft['procedure_time']=pd.to_datetime(dft['procedure_time'])
dft['hour']=dft['procedure_time'].dt.hour

print(dft)
print(dft.dtypes)
st.sidebar.subheader("Frequency of charges by day time")
selecto = st.sidebar.selectbox("Select Department",dft['Department'].unique())
dataf = dft[dft['Department']==selecto]
figg = px.histogram(dataf,x='hour',nbins=20,color='hour',barmode='group')
st.plotly_chart(figg)












