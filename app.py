"""
# Actuartech IFRS 17 Dashboard
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import altair as alt
import mysql.connector
from datetime import datetime
import psycopg2
from sqlalchemy import create_engine

st.set_page_config(page_title="Actuartech IFRS 17 Data Management", layout="wide")

st.image("assets/Actuartech_logo.png")


hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        </style>
        """
#st.markdown(hide_menu_style, unsafe_allow_html=True)
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.title("IFRS 17 Reporting Dashboard")

border_style = '''
    border: 2px solid #f63366;
    border-radius: 5px;
    padding: 10px;
    margin-bottom: 10px;
'''

@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')



# Initialize connection.
# Uses st.experimental_singleton to only run once.
@st.cache_resource
def init_connection():
    host = st.secrets["mysql"]["host"]
    port = st.secrets["mysql"]["port"]
    user = st.secrets["mysql"]["user"]
    passw = st.secrets["mysql"]["password"]
    database = st.secrets["mysql"]["database"]
    
    # Create SQLAlchemy engine for MySQL connection
    engine = create_engine(f"mysql+pymysql://{user}:{passw}@{host}:{port}/{database}", echo=False)
    
    return engine


def run_query(query):
    try:
        # Get the cached connection engine
        engine = init_connection()
        
        # Use engine.connect() to create a connection and execute the query
        with engine.connect() as connection:
            result = pd.read_sql(query, connection)
        
        return result
    except Exception as e:
        print(f"Error: {e}")
        return None



def main():
    try:
        # Test the connection by running a simple query
        result = run_query("SELECT 1")
        st.write("Connection successful!")
    except Exception as e:
        st.write(f"Error connecting to the database: {e}")

def col_head(df):
    if len(df.columns) == 13:
        df.columns = headers1_GMM
    elif len(df.columns) == 14:
        df.columns = headers1_VFA

def measure_labels(df,measure):
    if len(df.columns) == 13:
        measure = ["absolute", "relative", "relative", "relative", "relative", "relative","total"]
    elif len(df.columns) == 14:
        measure = ["absolute", "relative", "relative", "relative","relative", "relative", "relative","total"]


def bar_chart(container,object_name,title,x,y):
    object_name = go.Figure()
    object_name = object_name.add_trace(go.Bar(x=x,y=y))
    object_name.update_layout(title = title, xaxis_title = "Period",yaxis_title = " ",yaxis=dict(tickformat=',.0f'))
    object_name.update_xaxes(tickvals=x.unique())
    container.plotly_chart(object_name,use_container_width=True)

def line_chart_max(container,object_name,title,x,y,format):
    object_name = go.Figure()
    object_name = object_name.add_trace(go.Scatter(x=x,y=y,mode='lines+markers'))
    object_name.update_layout(title = title,xaxis_title = "Period",yaxis_title = " ",yaxis= format)
    object_name.update_yaxes(range=[0, max(y)+0.15*max(y)])
    object_name.update_xaxes(tickvals=x.unique())
    container.plotly_chart(object_name,use_container_width=True)


def line_chart_100perc(container,object_name,title,x,y,format):
    object_name = go.Figure()
    object_name = object_name.add_trace(go.Scatter(x=x,y=y,mode='lines+markers'))
    object_name.update_layout(title = title,xaxis_title = "Period",yaxis_title = " ",yaxis= format)
    object_name.update_yaxes(range=[0, 1])
    object_name.update_xaxes(tickvals=x.unique())
    container.plotly_chart(object_name,use_container_width=True)

def group_bar_chart1(container,object_name,title,x,y_1,y_2,y_1_label,y_2_label):
    object_name = go.Figure()
    object_name = object_name.add_trace(go.Bar(x=x,y=y_1,name=y_1_label))
    object_name = object_name.add_scatter(x=x, y=y_2, mode='lines', name=y_2_label)
    object_name.update_layout(title = title, xaxis_title = "Period",yaxis_title = " ",yaxis=dict(tickformat=',.0f'))
    object_name.update_xaxes(tickvals=x.unique())
    container.plotly_chart(object_name,use_container_width=True)
    

def group_bar_chart2(container,object_name,title,y):
    object_name = pd.melt(y, id_vars=['Period','Product','Sub-Product'] ,var_name='Measure' , value_name='Value')
    object_name = alt.Chart(object_name).mark_bar().encode(x=alt.X('Measure:N', title=None),y=alt.X('Value:Q',title = None),
                        color='Measure:N',column=alt.X('Period',title =None)).configure_header(labelFontSize=12).configure_axisX(labelFontSize=8,labelAngle=45)
    object_name.title = title
    container.write(object_name.properties(width=200, height=200), use_container_width=True)

def waterfall(container,object_name,title,data, measure, start_column):
        object_name= go.Figure(go.Waterfall(name = "Waterfall Chart",orientation = "v",
                measure = measure,
                x = data.columns[start_column:len(data.columns)],
                y = data.iloc[0,start_column:len(data.columns)], textposition = "outside", decreasing = {"marker":{"color":"red"}},increasing = {"marker":{"color":"green"}}, totals = {"marker":{"color":"grey"}},
                connector = {"line":{"color":"rgb(63, 63, 63)"}}))
        object_name.update_layout(title = title,xaxis_title = "Measures",yaxis_title = " ",yaxis=dict(tickformat=',.0f'))
        container.plotly_chart(object_name, use_container_width=True )

def format_table(data):
    numeric_cols = data.select_dtypes(include='number').columns
    data[numeric_cols] = data[numeric_cols].applymap('{:,.2f}'.format)

def invert_signs(data):
    numeric_cols = data.select_dtypes(include='number').columns
    data[numeric_cols] = abs(data[numeric_cols])

            

conn = init_connection()

@st.cache_data(ttl=600)  # Caches data for 10 minutes (600 seconds)
def run_query(query):
    try:
        engine = init_connection()  # Assuming init_connection() returns an engine for MySQL
        with engine.connect() as connection:
            result = pd.read_sql(query, connection)
        return result
    except Exception as e:
        print(f"Error: {e}")
        return None
    

# BEL = run_query("SELECT * from BEL;")
# RA = run_query("SELECT * from RA;")
# CSM = run_query("SELECT * from CSM;")
# TCL = run_query("SELECT * from TCL;")
# AMC  = run_query("SELECT * from AMC")
# ARC  = run_query("SELECT * from ARC")
# Reins_BEL = run_query("SELECT * from Reins_BEL;")
# Reins_RA = run_query("SELECT * from Reins_RA;")
# Reins_CSM = run_query("SELECT * from Reins_CSM;")
# Reins_TCL = run_query("SELECT * from Reins_TCL;")
# Reins_AMC  = run_query("SELECT * from Reins_AMC")
# Reins_ARC  = run_query("SELECT * from Reins_ARC")


BEL = run_query('SELECT * from `BEL`;')
RA = run_query('SELECT * from `RA`;')
CSM = run_query('SELECT * from `CSM`;')
TCL = run_query('SELECT * from `TCL`;')
AMC  = run_query('SELECT * from `AMC`;')
ARC  = run_query('SELECT * from `ARC`;')
Reins_BEL = run_query('SELECT * from `Reins_BEL`;')
Reins_RA = run_query('SELECT * from `Reins_RA`;')
Reins_CSM = run_query('SELECT * from `Reins_CSM`;')
Reins_TCL = run_query('SELECT * from `Reins_TCL`;')
Reins_AMC  = run_query('SELECT * from `Reins_AMC`;')
Reins_ARC  = run_query('SELECT * from `Reins_ARC`;')


headers1_GMM =["Index","Period", "Product", "Sub-Product", 
                    "Opening Balance",
                    "New Business",
                    "Change in Assumptions",
                    "Discounting-Unwinds",
                    "Experience Adjustment",
                    "Release to P&L",
                    "Adjustments to LIC",
                    "Onerous Contracts",
                    "Closing Balance"]


headers1_VFA =["Index","Period", "Product", "Sub-Product", 
                    "Opening Balance",
                    "New Business",
                    "Change in Assumptions",
                    "Discounting-Unwinds",
                    "Experience Adjustment",
                    "Change in Fair Value of UI",
                    "Release to P&L",
                    "Adjustments to LIC",
                    "Onerous Contracts",
                    "Closing Balance"]


headers2 = ["Period", "Product", "Sub-Product", "Measure", 'Opening Balance', 'CSM recognised in profit or loss for the services provided', 'Risk Adjustment recognised for the risk expired', 
                                'Experience adjustments', 'Changes that relate to current service', 'Changes in estimates that adjust the CSM', 'Changes in onerous contract losses or reversal of losses', 'Contracts initially recognised in the period', 'Changes that relate to future service',
                                  'Adjustments to liabilities for incurred claims', 'Changes that relate to past service', 'Insurance service result', 'Finance expenses from insurance contracts issued', 'Effects of movements in exchange rates', 'Investment Component and Premium Refund', 'Total recognised in comprehensive income',
                                    'Premiums received', 'Claims and other directly attributable expenses paid', 'Insurance acquisition cash flows', 'Total cash flows', 'Closing Balance']

headers3 = ["Period", "Measure", "Product", "Sub-Product", 'Opening Balance', 'Changes in the statement of profit and loss and OCI', 'Other contracts recognised', 
                                'Expected incurred claims and Expenses', 'Amortisation of insurance acquisition cash flows', 'Losses and reversals of losses on onerous contracts', 'Adjustments to liabilities for incurred claims', 
                                'Insurance service result', 'Net finance expenses from insurance contracts', 'Effect of movement in exchange rates', 'Investment components and premium refunds', 'Total changes in the statement of profit and loss and OCI', 
                                'Premiums received', 'Actual claims and other expenses paid', 'Insurance acquisition cash flows', 'Total cash flows', 'Other items transfer in the statement of financial position', 'Closing Balance']



Gross_BEL = pd.DataFrame(BEL)
col_head(Gross_BEL)
if 'Period' in Gross_BEL.columns:
    Gross_BEL['Period'] = pd.to_datetime(Gross_BEL['Period'], format='%d/%m/%Y').dt.date
else:
    print("The 'Period' column is missing!")
Gross_RA = pd.DataFrame(RA)
col_head(Gross_RA)
Gross_RA['Period'] = pd.to_datetime(Gross_RA['Period'],format = '%d/%m/%Y').dt.date
Gross_CSM = pd.DataFrame(CSM)
col_head(Gross_CSM)
Gross_CSM['Period'] = pd.to_datetime(Gross_CSM['Period'],format = '%d/%m/%Y').dt.date
Gross_TCL = pd.DataFrame(TCL)
col_head(Gross_TCL)
Gross_TCL['Period'] = pd.to_datetime(Gross_TCL['Period'],format = '%d/%m/%Y').dt.date
Reins_BEL = pd.DataFrame(Reins_BEL)
col_head(Reins_BEL)
Reins_BEL['Period'] = pd.to_datetime(Reins_BEL['Period'],format = '%d/%m/%Y').dt.date
Reins_RA = pd.DataFrame(Reins_RA)
col_head(Reins_RA)
Reins_RA['Period'] = pd.to_datetime(Reins_RA['Period'],format = '%d/%m/%Y').dt.date
Reins_CSM = pd.DataFrame(Reins_CSM)
col_head(Reins_CSM)
Reins_CSM['Period'] = pd.to_datetime(Reins_CSM['Period'],format = '%d/%m/%Y').dt.date
Reins_TCL = pd.DataFrame(Reins_TCL)
col_head(Reins_TCL)
Reins_TCL['Period'] = pd.to_datetime(Reins_TCL['Period'],format = '%d/%m/%Y').dt.date


Gross_AMC = pd.DataFrame(AMC,columns= headers2 )
Gross_AMC['Period'] = pd.to_datetime(Gross_AMC['Period'],format = '%d/%m/%Y').dt.date
Reins_AMC = pd.DataFrame(Reins_AMC,columns= headers2)
Reins_AMC['Period'] = pd.to_datetime(Reins_AMC['Period'],format = '%d/%m/%Y').dt.date


Gross_ARC = pd.DataFrame(ARC,columns=headers3 )
Gross_ARC['Period'] = pd.to_datetime(Gross_ARC['Period'],format = '%d/%m/%Y').dt.date
Reins_ARC = pd.DataFrame(Reins_ARC,columns=headers3 )
Reins_ARC['Period'] = pd.to_datetime(Reins_ARC['Period'],format = '%d/%m/%Y').dt.date

dashboard_tab, about_tab = st.tabs(["Dashboard", "About Us"])


with about_tab:
    about_con = st.container()
    about_con.write('#### About Us')
    st.write("This app is developed by Dupro Ltd (Actuartech). For further details, Contact info@actuartech.com")

with dashboard_tab:
    dashboard_gross_Reins_filter = st.expander("Filter by Contract Type")
    contract = dashboard_gross_Reins_filter.selectbox('#### Contract Type', ('Gross Contracts', 'Reinsurance Contracts'),key = "contract")
    if contract == "Gross Contracts":
        BEL = Gross_BEL
        RA = Gross_RA
        CSM = Gross_CSM
        TCL = Gross_TCL
        AMC = Gross_AMC
        ARC = Gross_ARC
    elif contract == "Reinsurance Contracts":
        BEL = Reins_BEL
        RA = Reins_RA
        CSM = Reins_CSM
        TCL = Reins_TCL
        AMC = Reins_AMC
        ARC = Reins_ARC
    recon_tab, disclosure_tab, kpi_tab = st.tabs(["Reconciliations","Disclosures","KPI"])
    
    
#KPI's
    with kpi_tab:
        BEL_KPI, RA_KPI, CSM_KPI, Other_KPI = st.tabs(["Best Estimate Liabilities","Risk Adjustment","Contractual Service Margin", "Other's"])
        ######
        with BEL_KPI:
            dashboard_BEL_kpi_con = st.container()
            dashboard_BEL_kpi_con.write("<span style='color:blue; font-size: 15px;'> Dashboard > KPI > Best Estimate Liabilities",unsafe_allow_html=True)
            with st.expander("Additional Filters"):
                kpi_BEL_tab_prod_col, kpi_BEL_tab_sub_col = st.columns(2)     
                with kpi_BEL_tab_prod_col:
                    st.write('#### Product')
                    kpi_BEL_tab_product = st.selectbox('#### ', tuple(np.unique(BEL['Product'])),key = "kpi_BEL_tab_product")
                with kpi_BEL_tab_sub_col:
                    st.write('#### Subproduct')
                    kpi_BEL_tab_subproduct = st.selectbox('#### ', tuple(np.unique(BEL['Sub-Product'])),key = "kpi_BEL_tab_subproduct")
                
                kpi_BEL_tab_years = st.selectbox('Period',  tuple(np.unique(BEL['Period'])),key="kpi_BEL_tab_years")
            kpi_BEL_tab_graph_waterfall = st.container()
            kpi_BEL_tab_table_data = BEL.loc[(BEL["Product"] == str(kpi_BEL_tab_product)) & (BEL["Sub-Product"] == str(kpi_BEL_tab_subproduct))& (BEL['Period'] == (kpi_BEL_tab_years))]
            kpi_BEL_tab_table_data = kpi_BEL_tab_table_data.drop(['Adjustments to LIC', 'Onerous Contracts'], axis=1)
            kpi_BEL_tab_table_data.rename(columns = {'Release to P&L':'Incurred Claims'}, inplace = True)
            measure_BEL = []
            measure_labels(Gross_BEL,measure_BEL)
            waterfall(kpi_BEL_tab_graph_waterfall,kpi_BEL_tab_table_data,"Waterfall Chart",kpi_BEL_tab_table_data, measure_BEL,4)
            with st.expander("Additional Filters"):
                st.write('#### Period')
                BEL_copy = BEL.copy()
                AMC_copy = AMC.copy()
                invert_signs(BEL_copy)
                invert_signs(AMC_copy)
                
                kpi_BEL_tab2_min_year = st.selectbox('Start Period', BEL_copy["Period"].unique(),key  = "kpi_BEL_tab2_min_year")
                kpi_BEL_tab2_max_year = st.selectbox('End Period', BEL_copy["Period"].unique(),key = "kpi_BEL_tab2_max_year")
                    
            NewBS_BEL , Expected_release_BEL = st.columns(2)
            with NewBS_BEL:
                NewBS_BEL_graph = st.container()
                NewBS_BEL_graph_data = BEL_copy.loc[(BEL_copy["Product"] == str(kpi_BEL_tab_product)) & (BEL_copy["Sub-Product"] == str(kpi_BEL_tab_subproduct))].loc[(BEL_copy['Period'] >= kpi_BEL_tab2_min_year) & (BEL_copy['Period'] <= kpi_BEL_tab2_max_year), "New Business"]
                bar_chart(NewBS_BEL_graph,NewBS_BEL_graph_data,"New Business",BEL_copy["Period"],NewBS_BEL_graph_data)
                
            with Expected_release_BEL:
                Expected_release_BEL_graph = st.container()
                BEL_copy.rename(columns={"Release to P&L": "Incurred Claims"}, inplace=True)
                Expected_release_BEL_graph_data = BEL_copy.loc[(BEL_copy["Product"] == str(kpi_BEL_tab_product)) & (BEL_copy["Sub-Product"] == str(kpi_BEL_tab_subproduct))].loc[(BEL_copy['Period'] >= kpi_BEL_tab2_min_year) & (BEL_copy['Period'] <= kpi_BEL_tab2_max_year), "Incurred Claims"]
                line_chart_max(Expected_release_BEL_graph,Expected_release_BEL_graph_data,"Incurred Claims",BEL_copy["Period"],Expected_release_BEL_graph_data,dict(tickformat=',.0f'))
            
            
            BEL_C = pd.merge(BEL_copy.loc[:,['Period','Product','Sub-Product','Incurred Claims']],AMC_copy.loc[AMC_copy['Measure'] == "Present value of future cash flows"].loc[:,['Period','Product','Sub-Product','Claims and other directly attributable expenses paid']], on = ['Period','Product','Sub-Product'])
            BEL_C.rename(columns = {'Incurred Claims':'Expected Incurred Claims', 'Claims and other directly attributable expenses paid':'Actual Incurred Claims',}, inplace = True)
            Expected_vs_actual_release_BEL_graph = st.container()
            Expected_vs_actual_release_BEL_graph_data = BEL_C[(BEL_C["Product"] == str(kpi_BEL_tab_product)) & (BEL_C["Sub-Product"] == str(kpi_BEL_tab_subproduct))].loc[(BEL_C['Period'] >= kpi_BEL_tab2_min_year) & (BEL_C['Period'] <= kpi_BEL_tab2_max_year),:]
            group_bar_chart2(Expected_vs_actual_release_BEL_graph,Expected_vs_actual_release_BEL_graph_data,"Expected Incurred Claims Vs Actual Incurred Claims",Expected_vs_actual_release_BEL_graph_data)
            
            Released_Opening_ratio_BEL, remainingDur_vs_remaining_CSM__BEL =st.columns(2)
            with Released_Opening_ratio_BEL:
                Released_Opening_ratio_BEL_graph =st.container()
                BEL_M = BEL_copy.copy()
                BEL_M['Released_Opening_ratio'] = BEL_M.loc[:,'Incurred Claims']/BEL_M.loc[:,'Opening Balance']
                Released_Opening_ratio_BEL_graph_data = BEL_M.loc[(BEL_M["Product"] == str(kpi_BEL_tab_product)) & (BEL_M["Sub-Product"] == str(kpi_BEL_tab_subproduct))].loc[(BEL['Period'] >= kpi_BEL_tab2_min_year) & (BEL['Period'] <= kpi_BEL_tab2_max_year), "Released_Opening_ratio"]
                line_chart_100perc(Released_Opening_ratio_BEL_graph,Released_Opening_ratio_BEL_graph_data,"Expected Claims Vs Opening Balance",BEL_M["Period"],Released_Opening_ratio_BEL_graph_data,None)               
        ######
        with RA_KPI:
            dashboard_RA_kpi_con = st.container()
            dashboard_RA_kpi_con.write("<span style='color:blue; font-size: 15px;'> Dashboard > KPI > Risk Adjustment",unsafe_allow_html=True)
            with st.expander("Additional Filters"):
                kpi_RA_tab_prod_col, kpi_RA_tab_sub_col = st.columns(2)     
                with kpi_RA_tab_prod_col:
                    st.write('#### Product')
                    kpi_RA_tab_product = st.selectbox('#### ', tuple(np.unique(RA['Product'])),key = "kpi_RA_tab_product")
                with kpi_RA_tab_sub_col:
                    st.write('#### Subproduct')
                    kpi_RA_tab_subproduct = st.selectbox('#### ', tuple(np.unique(RA['Sub-Product'])),key = "kpi_RA_tab_subproduct")
                
                kpi_RA_tab_years = st.selectbox('Period',  tuple(np.unique(RA['Period'])),key="kpi_RA_tab_years")    
            kpi_RA_tab_graph_waterfall = st.container()
            kpi_RA_tab_table_data = RA.loc[(RA["Product"] == str(kpi_RA_tab_product)) & (RA["Sub-Product"] == str(kpi_RA_tab_subproduct))& (RA['Period'] == (kpi_RA_tab_years))]
            kpi_RA_tab_table_data = kpi_RA_tab_table_data.drop(['Adjustments to LIC', 'Onerous Contracts'], axis=1)
            measure_RA = []
            measure_labels(Gross_RA,measure_RA)
            waterfall(kpi_RA_tab_graph_waterfall,kpi_RA_tab_table_data,"Waterfall Chart",kpi_RA_tab_table_data, measure_RA,4)

            with st.expander("Additional Filters"):
                st.write('#### Period')
                RA_copy = RA.copy()
                invert_signs(RA_copy)    
                kpi_RA_tab2_min_year = st.selectbox('Start Period', RA_copy["Period"].unique(),key  = "kpi_RA_tab2_min_year")
                kpi_RA_tab2_max_year = st.selectbox('End Period', RA_copy["Period"].unique(),key = "kpi_RA_tab2_max_year")
                
            NewBS_RA , Expected_release_RA = st.columns(2)
            with NewBS_RA:
                NewBS_RA_graph = st.container()
                NewBS_RA_graph_data = RA_copy.loc[(RA_copy["Product"] == str(kpi_RA_tab_product)) & (RA_copy["Sub-Product"] == str(kpi_RA_tab_subproduct))].loc[(RA_copy['Period'] >= kpi_RA_tab2_min_year) & (RA_copy['Period'] <= kpi_RA_tab2_max_year), "New Business"]
                bar_chart(NewBS_RA_graph,NewBS_RA_graph_data,"New Business",RA_copy["Period"],NewBS_RA_graph_data)
            with Expected_release_RA:
                Expected_release_RA_graph = st.container()
                Expected_release_RA_graph_data = RA_copy.loc[(RA_copy["Product"] == str(kpi_RA_tab_product)) & (RA_copy["Sub-Product"] == str(kpi_RA_tab_subproduct))].loc[(RA_copy['Period'] >= kpi_RA_tab2_min_year) & (RA_copy['Period'] <= kpi_RA_tab2_max_year), "Release to P&L"]
                line_chart_max(Expected_release_RA_graph,Expected_release_RA_graph_data,"Expected Release",RA_copy["Period"],Expected_release_RA_graph_data,dict(tickformat=',.0f'))

            RA_C = pd.merge(RA_copy.loc[:,['Period','Product','Sub-Product','Release to P&L']],AMC_copy.loc[AMC_copy['Measure'] == "Risk Adjustment"].loc[:,['Period','Product','Sub-Product','Claims and other directly attributable expenses paid']], on = ['Period','Product','Sub-Product'])
            RA_C.rename(columns = {'Release to P&L':'Expected Release', 'Claims and other directly attributable expenses paid':'Actual Release',}, inplace = True)
            Expected_vs_actual_release_RA_graph = st.container()
            Expected_vs_actual_release_RA_graph_data = RA_C[(RA_C["Product"] == str(kpi_RA_tab_product)) & (RA_C["Sub-Product"] == str(kpi_RA_tab_subproduct))].loc[(RA_C['Period'] >= kpi_RA_tab2_min_year) & (RA_C['Period'] <= kpi_RA_tab2_max_year),:]
            group_bar_chart2(Expected_vs_actual_release_RA_graph,Expected_vs_actual_release_RA_graph_data,"Expected Release Vs Actual Release",Expected_vs_actual_release_RA_graph_data)
            
            Released_Opening_ratio_RA, Released_NB_ratio_RA =st.columns(2)
            with Released_Opening_ratio_RA:
                Released_Opening_ratio_RA_graph =st.container()
                RA_M = RA_copy.copy()
                RA_M['Released_Opening_ratio'] = RA_M.loc[:,'Release to P&L']/RA_M.loc[:,'Opening Balance']
                Released_Opening_ratio_RA_graph_data = RA_M.loc[(RA_M["Product"] == str(kpi_RA_tab_product)) & (RA_M["Sub-Product"] == str(kpi_RA_tab_subproduct))].loc[(RA_M['Period'] >= kpi_RA_tab2_min_year) & (RA_M['Period'] <= kpi_RA_tab2_max_year), "Released_Opening_ratio"]
                line_chart_100perc(Released_Opening_ratio_RA_graph,Released_Opening_ratio_RA_graph_data,"Expected Release Vs Opening Balance",RA_M["Period"],Released_Opening_ratio_RA_graph_data,None)
            with Released_NB_ratio_RA:
                RA_M['Released_NB_ratio'] = RA_M.loc[:,'Release to P&L']/RA_M.loc[:,'New Business']
                Released_NB_ratio_RA_graph =st.container()
                Released_NB_ratio_RA_graph_data = RA_M.loc[(RA_M["Product"] == str(kpi_RA_tab_product)) & (RA_M["Sub-Product"] == str(kpi_RA_tab_subproduct))].loc[(RA_M['Period'] >= kpi_RA_tab2_min_year) & (RA_M['Period'] <= kpi_RA_tab2_max_year), "Released_NB_ratio"]
                line_chart_100perc(Released_NB_ratio_RA_graph,Released_NB_ratio_RA_graph_data,"Expected Release Vs New Business",RA_M["Period"],Released_NB_ratio_RA_graph_data,None)
            
            RA_NB_BEL_NB_ratio, a = st.columns(2)
            with RA_NB_BEL_NB_ratio:
                RA_M['RA_NB_BEL_NB_ratio'] = RA_M.loc[:,'New Business']/BEL.loc[:,'New Business']
                RA_NB_BEL_NB_ratio_graph =st.container()
                RA_NB_BEL_NB_ratio_graph_data = RA_M.loc[(RA_M["Product"] == str(kpi_RA_tab_product)) & (RA_M["Sub-Product"] == str(kpi_RA_tab_subproduct))].loc[(RA_M['Period'] >= kpi_RA_tab2_min_year) & (RA_M['Period'] <= kpi_RA_tab2_max_year), "RA_NB_BEL_NB_ratio"]
                line_chart_100perc(RA_NB_BEL_NB_ratio_graph,RA_NB_BEL_NB_ratio_graph_data,"RA New Business Vs BEL New Business",RA_M["Period"],RA_NB_BEL_NB_ratio_graph_data,None)

        ######
        with CSM_KPI:
            dashboard_CSM_kpi_con = st.container()
            dashboard_CSM_kpi_con.write("<span style='color:blue; font-size: 15px;'> Dashboard > KPI > Contractual Service Margin",unsafe_allow_html=True)
            with st.expander("Additional Filters"):
                kpi_CSM_tab_prod_col, kpi_CSM_tab_sub_col = st.columns(2)     
                with kpi_CSM_tab_prod_col:
                    st.write('#### Product')
                    kpi_CSM_tab_product = st.selectbox('#### ', tuple(np.unique(CSM['Product'])),key = "kpi_CSM_tab_product")
                with kpi_CSM_tab_sub_col:
                    st.write('#### Subproduct')
                    kpi_CSM_tab_subproduct = st.selectbox('#### ', tuple(np.unique(CSM['Sub-Product'])),key = "kpi_CSM_tab_subproduct")

                
                kpi_CSM_tab_years = st.selectbox('Period',  tuple(np.unique(CSM['Period'])),key="kpi_CSM_tab_years")
            kpi_CSM_tab_graph_waterfall = st.container()
            kpi_CSM_tab_table_data = CSM.loc[(CSM["Product"] == str(kpi_CSM_tab_product)) & (CSM["Sub-Product"] == str(kpi_CSM_tab_subproduct))& (CSM['Period'] == (kpi_CSM_tab_years))]
            kpi_CSM_tab_table_data = kpi_CSM_tab_table_data.drop(['Adjustments to LIC', 'Onerous Contracts'], axis=1)
            measure_CSM = []
            measure_labels(Gross_CSM,measure_CSM)
            waterfall(kpi_CSM_tab_graph_waterfall,kpi_CSM_tab_table_data,"Waterfall Chart",kpi_CSM_tab_table_data, measure_CSM,4)
            
            with st.expander("Additional Filters"):
                st.write('#### Period')
                CSM_copy = CSM.copy()
                invert_signs(CSM_copy)
                kpi_CSM_tab2_min_year = st.selectbox('Start Period', CSM_copy["Period"].unique(),key  = "kpi_CSM_tab2_min_year")
                kpi_CSM_tab2_max_year = st.selectbox('End Period', CSM_copy["Period"].unique(),key = "kpi_CSM_tab2_max_year")

            NewBS_CSM , Expected_release_CSM = st.columns(2)
            with NewBS_CSM:
                NewBS_CSM_graph = st.container()
                NewBS_CSM_graph_data = CSM_copy.loc[(CSM_copy["Product"] == str(kpi_CSM_tab_product)) & (CSM_copy["Sub-Product"] == str(kpi_CSM_tab_subproduct))].loc[(CSM_copy['Period'] >= kpi_CSM_tab2_min_year) & (CSM_copy['Period'] <= kpi_CSM_tab2_max_year), "New Business"]
                bar_chart(NewBS_CSM_graph,NewBS_CSM_graph_data,"New Business",CSM_copy["Period"],NewBS_CSM_graph_data)
            with Expected_release_CSM:
                Expected_release_CSM_graph = st.container()
                Expected_release_CSM_graph_data = CSM_copy.loc[(CSM_copy["Product"] == str(kpi_CSM_tab_product)) & (CSM_copy["Sub-Product"] == str(kpi_CSM_tab_subproduct))].loc[(CSM_copy['Period'] >= kpi_CSM_tab2_min_year) & (CSM_copy['Period'] <= kpi_CSM_tab2_max_year), "Release to P&L"]
                line_chart_max(Expected_release_CSM_graph,Expected_release_CSM_graph_data,"Expected Release",CSM_copy["Period"],Expected_release_CSM_graph_data,dict(tickformat=',.0f'))
            
            Expected_vs_actual_release_CSM, Released_NB_ratio_CSM= st.columns(2)
            with Expected_vs_actual_release_CSM:
                CSM_C = pd.merge(CSM_copy.loc[:,['Period','Product','Sub-Product','Release to P&L']],AMC_copy.loc[AMC_copy['Measure'] == "Contractual Service Margin"].loc[:,['Period','Product','Sub-Product','Claims and other directly attributable expenses paid']], on = ['Period','Product','Sub-Product'])
                CSM_C.rename(columns = {'Release to P&L':'Expected Release', 'Claims and other directly attributable expenses paid':'Actual Release',}, inplace = True)
                Expected_vs_actual_release_CSM_graph = st.container()
                Expected_vs_actual_release_CSM_graph_data = CSM_C[(CSM_C["Product"] == str(kpi_CSM_tab_product)) & (CSM_C["Sub-Product"] == str(kpi_CSM_tab_subproduct))].loc[(CSM_C['Period'] >= kpi_CSM_tab2_min_year) & (CSM_C['Period'] <= kpi_CSM_tab2_max_year),:]
                group_bar_chart2(Expected_vs_actual_release_CSM_graph,Expected_vs_actual_release_CSM_graph_data,"Expected Release Vs Actual Release",Expected_vs_actual_release_CSM_graph_data)
                
            with Released_NB_ratio_CSM:
                CSM_M = CSM_copy.copy()
                CSM_M['Released_NB_ratio'] = CSM_M.loc[:,'Release to P&L']/CSM_M.loc[:,'New Business']
                Released_NB_ratio_CSM_graph =st.container()
                Released_NB_ratio_CSM_graph_data = CSM_M.loc[(CSM_M["Product"] == str(kpi_CSM_tab_product)) & (CSM_M["Sub-Product"] == str(kpi_CSM_tab_subproduct))].loc[(CSM_M['Period'] >= kpi_CSM_tab2_min_year) & (CSM_M['Period'] <= kpi_CSM_tab2_max_year), "Released_NB_ratio"]
                line_chart_100perc(Released_NB_ratio_CSM_graph,Released_NB_ratio_CSM_graph_data,"Expected Release Vs New Business",CSM_M["Period"],Released_NB_ratio_CSM_graph_data,None)
            
            CSM_NB_BEL_NB_ratio, NB_CSM_vs_NB_Prem= st.columns(2)
            with CSM_NB_BEL_NB_ratio:    
                CSM_M['CSM_NB_BEL_NB_ratio'] = CSM_M.loc[:,'New Business']/BEL_M.loc[:,'New Business']
                CSM_NB_BEL_NB_ratio_graph =st.container()
                CSM_NB_BEL_NB_ratio_graph_data = CSM_M.loc[(CSM_M["Product"] == str(kpi_CSM_tab_product)) & (CSM_M["Sub-Product"] == str(kpi_CSM_tab_subproduct))].loc[(CSM_M['Period'] >= kpi_CSM_tab2_min_year) & (CSM_M['Period'] <= kpi_CSM_tab2_max_year), "CSM_NB_BEL_NB_ratio"]
                line_chart_100perc(CSM_NB_BEL_NB_ratio_graph,CSM_NB_BEL_NB_ratio_graph_data,"CSM New Business Vs BEL New Business",CSM_M["Period"],CSM_NB_BEL_NB_ratio_graph_data,None)

            with NB_CSM_vs_NB_Prem:
                CSM_N = CSM_copy.copy()
                AMC.loc[AMC['Measure'] == "Total",'Premiums received'] = abs(AMC.loc[AMC['Measure'] == "Total",'Premiums received'])
                CSM_N = pd.merge(CSM_N.loc[:,['Period','Product','Sub-Product','New Business']],AMC.loc[AMC['Measure'] == "Total"].loc[:,['Period','Product','Sub-Product','Premiums received']], on = ['Period','Product','Sub-Product'])
                CSM_N.rename(columns = {'New Business':'New Business', 'Premiums received':'Premiums',}, inplace = True)
                NB_CSM_vs_NB_Prem_graph = st.container()
                NB_CSM_vs_NB_Prem_graph_data = CSM_N[(CSM_N["Product"] == str(kpi_CSM_tab_product)) & (CSM_N["Sub-Product"] == str(kpi_CSM_tab_subproduct))].loc[(CSM_N['Period'] >= kpi_CSM_tab2_min_year) & (CSM_N['Period'] <= kpi_CSM_tab2_max_year),:]
                #group_bar_chart2(NB_CSM_vs_NB_Prem_graph,NB_CSM_vs_NB_Prem_graph_data,"New Business Vs Premium",NB_CSM_vs_NB_Prem_graph_data)

                group_bar_chart1(NB_CSM_vs_NB_Prem_graph,NB_CSM_vs_NB_Prem_graph_data,"New Business Vs Premium",NB_CSM_vs_NB_Prem_graph_data['Period'],NB_CSM_vs_NB_Prem_graph_data['New Business'],NB_CSM_vs_NB_Prem_graph_data['Premiums'],"New Business","Premiums")
                
#RECONCILIATIONS
    with recon_tab:    
        rec_output_tab, rec_charts_tab = st.tabs(["🗃 Output Mapped Tables", "📈 Charts"])
        data_BEL = BEL.copy()
        data_RA = RA.copy()
        data_CSM = CSM.copy()
        data_TCL = TCL.copy()
        with rec_output_tab:
            rec_output_tab_container = st.container()
            rec_output_tab_container.write("<span style='color:blue; font-size: 15px;'> Dashboard > Reconciliations > Output Mapped Tables",unsafe_allow_html=True)
            with st.expander("Additional Filters"):
                rec_output_tab_prod_col, rec_output_tab_sub_col = st.columns(2)
                with rec_output_tab_prod_col:
                    st.write('#### Product')
                    rec_output_tab_product = st.selectbox('#### ', tuple(np.unique(data_BEL['Product'])),key = "rec_output_tab_product")
                with rec_output_tab_sub_col:
                    st.write('#### Subproduct')
                    rec_output_tab_subproduct = st.selectbox('#### ', tuple(np.unique(data_BEL['Sub-Product'])),key = "rec_output_tab_subproduct")
                
                st.write('#### Period')
                rec_output_tab_min_year = st.selectbox('Start Period', data_BEL["Period"].unique(),key  = "rec_output_tab_min_year")
                rec_output_tab_max_year = st.selectbox('End Period', data_BEL["Period"].unique(),key = "rec_output_tab_max_year")
                
            st.write(str('#### ' + str("Best Estimate Liability")))
            rec_output_tab_BEL_table_data = st.container()
            rec_output_tab_BEL_table_data = data_BEL.loc[(data_BEL["Product"] == str(rec_output_tab_product)) & (data_BEL["Sub-Product"] == str(rec_output_tab_subproduct))].loc[(data_BEL['Period'] >= rec_output_tab_min_year) & (data_BEL['Period'] <= rec_output_tab_max_year),:] 
            format_table(rec_output_tab_BEL_table_data)
            rec_output_tab_BEL_table_data = rec_output_tab_BEL_table_data.set_index("Period")
            rec_output_tab_BEL_table_data = rec_output_tab_BEL_table_data.iloc[:,3:len(rec_output_tab_BEL_table_data.columns)]
            rec_output_tab_BEL_table_data_tr = rec_output_tab_BEL_table_data.transpose()
            st.dataframe(rec_output_tab_BEL_table_data_tr,use_container_width=True)
            file_name = str("ifrs17_BEL" + "-" + str(rec_output_tab_product) + "-" + str(rec_output_tab_subproduct) + "-" + str(rec_output_tab_min_year) + "-" + str(rec_output_tab_min_year) + ".csv")
            csv = convert_df(rec_output_tab_BEL_table_data_tr.reset_index())
            st.download_button("📥 Download Table as CSV",csv,file_name,"text/csv",key="rec_output_tab_BEL_table_data")
            
            st.write(str('#### ' + str("Risk Adjustment")))
            rec_output_tab_RA_table_data = st.container()
            rec_output_tab_RA_table_data = data_RA.loc[(data_RA["Product"] == str(rec_output_tab_product)) & (data_RA["Sub-Product"] == str(rec_output_tab_subproduct))].loc[(data_RA['Period'] >= rec_output_tab_min_year) & (data_RA['Period'] <= rec_output_tab_max_year), :] 
            format_table(rec_output_tab_RA_table_data)
            rec_output_tab_RA_table_data = rec_output_tab_RA_table_data.set_index("Period")
            rec_output_tab_RA_table_data = rec_output_tab_RA_table_data.iloc[:,3:len(rec_output_tab_RA_table_data.columns)]
            rec_output_tab_RA_table_data_tr = rec_output_tab_RA_table_data.transpose()
            st.dataframe(rec_output_tab_RA_table_data_tr,use_container_width=True)
            file_name = str("ifrs17_RA" + "-" + str(rec_output_tab_product) + "-" + str(rec_output_tab_subproduct) + "-" + str(rec_output_tab_min_year) + "-" + str(rec_output_tab_min_year) + ".csv")
            csv = convert_df(rec_output_tab_RA_table_data_tr.reset_index())
            st.download_button( "📥 Download Table as CSV", csv, file_name, "text/csv", key="rec_output_tab_RA_table_data" )
            
            st.write(str('#### ' + str("Contractual Service Margin")))
            rec_output_tab_CSM_table_data = st.container()
            rec_output_tab_CSM_table_data = data_CSM.loc[(data_CSM["Product"] == str(rec_output_tab_product)) & (data_CSM["Sub-Product"] == str(rec_output_tab_subproduct))].loc[(data_CSM['Period'] >= rec_output_tab_min_year) & (data_CSM['Period'] <= rec_output_tab_max_year), :] 
            format_table(rec_output_tab_CSM_table_data)
            rec_output_tab_CSM_table_data = rec_output_tab_CSM_table_data.set_index("Period")
            rec_output_tab_CSM_table_data = rec_output_tab_CSM_table_data.iloc[:,3:len(rec_output_tab_CSM_table_data.columns)]
            rec_output_tab_CSM_table_data_tr = rec_output_tab_CSM_table_data.transpose()
            st.dataframe(rec_output_tab_CSM_table_data_tr,use_container_width=True)
            file_name = str("ifrs17_CSM" + "-" + str(rec_output_tab_product) + "-" + str(rec_output_tab_subproduct) + "-" + str(rec_output_tab_min_year) + "-" + str(rec_output_tab_min_year) + ".csv")
            csv = convert_df(rec_output_tab_CSM_table_data_tr.reset_index())
            st.download_button( "📥 Download Table as CSV", csv, file_name, "text/csv", key="rec_output_tab_CSM_table_data" )

            st.write(str('#### ' + str("Insurance Contract Liability")))
            data_TCL['Period'] = pd.to_datetime(data_TCL['Period']).dt.date
            rec_output_tab_TCL_table_data = st.container()
            rec_output_tab_TCL_table_data = data_TCL.loc[(data_TCL["Product"] == str(rec_output_tab_product)) & (data_TCL["Sub-Product"] == str(rec_output_tab_subproduct))].loc[(data_TCL['Period'] >= rec_output_tab_min_year) & (data_TCL['Period'] <= rec_output_tab_max_year), :] 
            format_table(rec_output_tab_TCL_table_data)
            rec_output_tab_TCL_table_data = rec_output_tab_TCL_table_data.set_index("Period")
            rec_output_tab_TCL_table_data = rec_output_tab_TCL_table_data.iloc[:,3:len(rec_output_tab_TCL_table_data.columns)]
            rec_output_tab_TCL_table_data_tr = rec_output_tab_TCL_table_data.transpose()
            st.dataframe(rec_output_tab_TCL_table_data_tr,use_container_width=True)
            file_name = str("ifrs17_TCL" + "-" + str(rec_output_tab_product) + "-" + str(rec_output_tab_subproduct) + "-" + str(rec_output_tab_min_year) + "-" + str(rec_output_tab_min_year) + ".csv")
            csv = convert_df(rec_output_tab_TCL_table_data_tr.reset_index())
            st.download_button( "📥 Download Table as CSV", csv, file_name, "text/csv", key="rec_output_tab_TCL_table_data" )

        with rec_charts_tab:
            rec_charts_tab_container = st.container()
            rec_charts_tab_container.write("<span style='color:blue; font-size: 15px;'> Dashboard > Reconciliations > Charts",unsafe_allow_html=True)
            with st.expander("Additional Filters"):
                rec_charts_tab_recon_col, rec_charts_tab_prod_col, rec_charts_tab_sub_col = st.columns(3)
                with rec_charts_tab_recon_col:
                    rec_charts_tab_recon_container = st.container()
                    rec_charts_tab_recon_container.write('#### Accounts')
                    recon = rec_charts_tab_recon_container.selectbox('#### ', ('Reconciliation of Best Estimate Liability', 'Reconciliation of Contractual Service Margin', 'Reconciliation of Risk Adjustment', 'Reconciliation of Insurance Contract Liability'),key = "rec_charts_tab_container")
                    if recon == "Reconciliation of Best Estimate Liability":
                        data = BEL.copy()
                        data.rename(columns = {'Release to P&L':'Incurred Claims'}, inplace = True)
                    elif recon == "Reconciliation of Contractual Service Margin":
                        data = CSM.copy()
                    elif recon == "Reconciliation of Risk Adjustment":
                        data = RA.copy()
                    elif recon == "Reconciliation of Insurance Contract Liability":
                        data = TCL.copy()
                
                with rec_charts_tab_prod_col:
                    st.write('#### Product')
                    rec_charts_tab_product = st.selectbox('#### ', tuple(np.unique(data['Product'])),key = "rec_charts_tab_product")
                with rec_charts_tab_sub_col:
                    st.write('#### Subproduct')
                    rec_charts_tab_subproduct = st.selectbox('#### ', tuple(np.unique(data['Sub-Product'])),key = "rec_charts_tab_subproduct")
                
                rec_charts_tab_years = st.selectbox('Period',  tuple(np.unique(data['Period'])),key="rec_charts_tab_years")
            rec_charts_tab_graph_waterfall = st.container()
            rec_charts_tab_table_data = data.loc[(data["Product"] == str(rec_charts_tab_product)) & (data["Sub-Product"] == str(rec_charts_tab_subproduct))& (data['Period'] == (rec_charts_tab_years))]    
            rec_charts_tab_table_data = rec_charts_tab_table_data.drop(['Adjustments to LIC', 'Onerous Contracts'], axis=1)
            measure_data = []
            measure_labels(Gross_BEL,measure_data)
            waterfall(rec_charts_tab_graph_waterfall,rec_charts_tab_table_data,"Waterfall Chart",rec_charts_tab_table_data, measure_data,4)
            
            with st.expander("Additional Filters"):
                data_copy = data.copy() 
                invert_signs(data_copy)
                container_measure = st.container()
                container_measure.write('#### Measure')
                measure_values = data_copy.columns
                list_of_measures = tuple(measure_values[4:len(measure_values)])
                measure = container_measure.selectbox("#### ", list_of_measures)
                st.write('#### Period')
                rec_charts_tab_min_year = st.selectbox('Start Period', data_copy["Period"].unique(),key  = "rec_charts_tab_min_year")
                rec_charts_tab_max_year = st.selectbox('End Period', data_copy["Period"].unique(),key = "rec_charts_tab_max_year")
                
            graph_measure = st.container()
            graph_measure.write('#### ' + str(recon) + '\n' + '##### ' + str(measure))
            graph_data = data_copy.loc[(data_copy["Product"] == str(rec_charts_tab_product)) & (data_copy["Sub-Product"] == str(rec_charts_tab_subproduct))].loc[(data_copy['Period'] >= rec_charts_tab_min_year) & (data_copy['Period'] <= rec_charts_tab_max_year), str(measure)]
            bar_chart(graph_measure,graph_data,"",data_copy["Period"],graph_data)  

#DISCLOSURES
    with disclosure_tab:
        disc_output_tab, disc_charts_tab = st.tabs(["🗃 Output Mapped Tables", "📈 Charts"]) 

                   
        with disc_output_tab: 
            disclosure_output_container = st.container()
            disclosure_output_container.write("<span style='color:blue; font-size: 15px;'> Dashboard > Disclosures > Output Mapped Tables",unsafe_allow_html=True)
            
            with st.expander("Additional Filters"):
                disc_outputs_tab_recon_col, disc_output_tab_prod_col, disc_output_tab_sub_col,disc_output_tab_measure = st.columns(4)
                with disc_outputs_tab_recon_col:
                    disc_outputs_tab_recon_col = st.container()
                    disc_outputs_tab_recon_col.write('#### Notes')
                    disc = disc_outputs_tab_recon_col.selectbox('#### ', ('Analysis Of Measurement Component', 'Analysis Of Remaining Coverages'),key = "disc_outputs_tab_container")
                    if disc == "Analysis Of Measurement Component":
                        data = AMC
                    elif disc == "Analysis Of Remaining Coverages":
                        data = ARC

                with disc_output_tab_prod_col:
                    st.write('#### Product')
                    disc_output_tab_product = st.selectbox('#### ', tuple(np.unique(data['Product'])),key = "disc_output_tab_product")
        
                with disc_output_tab_sub_col:
                    st.write('#### Subproduct')
                    disc_output_tab_subproduct = st.selectbox('#### ', tuple(np.unique(data['Sub-Product'])),key = "disc_output_tab_subproduct")
                
                with disc_output_tab_measure:
                    st.write('#### Measure')
                    disc_output_tab_measure = st.selectbox('#### ', tuple(np.unique(data['Measure'])),key = "disc_outputs_tab_measure") 

                st.write('#### Period')
                disc_output_tab_min_year = st.selectbox('Start Period', data["Period"].unique(),key  = "disc_output_tab_min_year")
                disc_output_tab_max_year = st.selectbox('End Period', data["Period"].unique(),key = "disc_output_tab_max_year")
                
            st.write(str('#### ') + str(disc) + '\n' + str(disc_output_tab_measure))
            disc_output_tab_table_data = st.container()
            disc_output_tab_table_data = data.loc[(data["Product"] == str(disc_output_tab_product)) & (data["Sub-Product"] == str(disc_output_tab_subproduct)) & (data['Measure'] == str(disc_output_tab_measure))].loc[(data['Period'] >= disc_output_tab_min_year) & (data['Period'] <= disc_output_tab_max_year), :] 
            format_table(disc_output_tab_table_data)
            disc_output_tab_table_data = disc_output_tab_table_data.set_index("Period")
            disc_output_tab_table_data = disc_output_tab_table_data.iloc[:,3:len(disc_output_tab_table_data.columns)]
            disc_output_tab_table_data_tr = disc_output_tab_table_data.transpose()
            st.dataframe(disc_output_tab_table_data_tr,use_container_width=True)
            file_name = str("ifrs17" + "-" + str(disc) + "-" + str (disc_output_tab_measure) + str(disc_output_tab_product) + "-" + str(disc_output_tab_subproduct) + "-" + str(disc_output_tab_min_year) + "-" + str(disc_output_tab_max_year) + ".csv") 
            csv = convert_df(disc_output_tab_table_data_tr.reset_index()) 
            st.download_button( "📥 Download Table as CSV", csv, file_name, "text/csv", key="disc_output_tab_table_data_tr" )
            
        with disc_charts_tab:
            disclosure_charts_container = st.container()
            disclosure_charts_container.write("<span style='color:blue; font-size: 15px;'> Dashboard > Disclosures > Charts",unsafe_allow_html=True)
            with st.expander("Additional Filters"):
                disc_charts_tab_recon_col, disc_charts_tab_measure_col, disc_charts_tab_prod_col, disc_charts_tab_sub_col = st.columns(4)
                with disc_charts_tab_recon_col:
                    disc_charts_tab_container = st.container()
                    disc_charts_tab_container.write('#### Notes')
                    disc = disc_charts_tab_container.selectbox('#### ', ('Analysis Of Measurement Component', 'Analysis Of Remaining Coverages'),key = "disc_charts_tab_container")
                    if disc == "Analysis Of Measurement Component":
                        data = AMC
                        data = data.drop(['Changes that relate to current service', 'Changes that relate to future service','Insurance service result', 'Investment Component and Premium Refund', 'Total recognised in comprehensive income','Total cash flows'],axis = 1)
                        measure_disc = ["absolute","relative","relative","relative","relative","relative","relative","relative","relative","relative","relative","relative","relative","relative","total"]
                    elif disc == "Analysis Of Remaining Coverages":
                        data = ARC
                        data = data.drop(['Insurance service result', 'Investment components and premium refunds', 'Total changes in the statement of profit and loss and OCI', 'Total cash flows'],axis = 1)
                        measure_disc = ["absolute","relative","relative","relative","relative","relative","relative","relative","relative","relative","relative","relative","relative","total"]
                
                with disc_charts_tab_prod_col:
                    st.write('#### Product')
                    disc_charts_tab_product = st.selectbox('#### ', tuple(np.unique(data['Product'])),key = "disc_charts_tab_product")
            
                with disc_charts_tab_sub_col:
                    st.write('#### Subproduct')
                    disc_charts_tab_subproduct = st.selectbox('#### ', tuple(np.unique(data['Sub-Product'])),key = "disc_charts_tab_subproduct")

                
                with disc_charts_tab_measure_col:
                    st.write('#### Measure')
                    disc_charts_tab_measure = st.selectbox('#### ', tuple(np.unique(data['Measure'])),key = "disc_charts_tab_measure") 
                
                disc_charts_tab_years = st.selectbox('Period ',  tuple(np.unique(data['Period'])),key="disc_charts_tab_years")
            disc_charts_tab_graph_waterfall = st.container()
            disc_charts_tab_table_data = data.loc[(data["Measure"] == str(disc_charts_tab_measure)) & (data["Product"] == str(disc_charts_tab_product)) & (data["Sub-Product"] == str(disc_charts_tab_subproduct))& (data['Period'] == disc_charts_tab_years)]
            waterfall(disc_charts_tab_graph_waterfall,disc_charts_tab_table_data,"Waterfall Chart",disc_charts_tab_table_data, measure_disc,4)
            
            with st.expander("Additional Filters"):
                disc_charts_tab2_prod_col, disc_charts_tab2_sub_col = st.columns(2)
                data_copy = data.copy()
                invert_signs(data_copy)
                                
                with disc_charts_tab2_prod_col:
                    st.write('#### Product')
                    disc_charts_tab2_product = st.selectbox('#### ', tuple(np.unique(data_copy['Product'])),key = "disc_charts_tab2_product")

                with disc_charts_tab2_sub_col:
                    st.write('#### Subproduct')
                    disc_charts_tab2_subproduct = st.selectbox('#### ', tuple(np.unique(data_copy['Sub-Product'])),key = "disc_charts_tab2_subproduct")
            
                st.write('#### Period')
                disc_charts_tab_min_year = st.selectbox('Start Period', data_copy["Period"].unique(),key  = "disc_charts_tab_min_year")
                disc_charts_tab_max_year = st.selectbox('End Period', data_copy["Period"].unique(),key = "disc_charts_tab_max_year")
                
                container_measure = st.container()
                container_measure.write('#### Measure')
                measure_values = data_copy.columns
                list_of_measures = tuple(measure_values[4:len(measure_values)])
                measure = container_measure.selectbox("#### ", list_of_measures)
                
            graph_measure = st.container()
            graph_data = data_copy.loc[(data_copy["Product"] == str(disc_charts_tab2_product)) & (data_copy["Sub-Product"] == str(disc_charts_tab2_subproduct))].loc[(data_copy['Period'] >= disc_charts_tab_min_year) & (data_copy['Period'] <= disc_charts_tab_max_year), str(measure)]
            bar_chart(graph_measure,graph_data,"",data_copy["Period"],graph_data)

st.info('To save the current dashboard page, use CTRL + P.', icon="ℹ️")

if __name__ == "__main__":
    main()
