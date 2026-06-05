import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output
from db_config import DB_CONFIG

DB_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
engine = create_engine(DB_URL)

def query(sql):
    return pd.read_sql(sql, engine)

dept_payroll = query("""
    SELECT department,
           ROUND(AVG(net_salary)::numeric,0)  AS avg_salary,
           ROUND(SUM(net_salary)::numeric,0)  AS total_payroll,
           COUNT(*)                            AS headcount,
           ROUND(AVG(overtime_pay)::numeric,0) AS avg_overtime
    FROM payroll GROUP BY department ORDER BY total_payroll DESC
""")

monthly = query("""
    SELECT pay_year, pay_month,
           ROUND(AVG(net_salary)::numeric,0) AS avg_salary,
           ROUND(SUM(net_salary)::numeric,0) AS total_payroll
    FROM payroll GROUP BY pay_year, pay_month ORDER BY pay_year, pay_month
""")
monthly['period'] = monthly['pay_year'].astype(str)+'-'+monthly['pay_month'].astype(str).str.zfill(2)

role_data = query("""
    SELECT job_role,
           ROUND(AVG(base_salary)::numeric,0) AS avg_base,
           ROUND(AVG(bonus)::numeric,0)       AS avg_bonus,
           ROUND(AVG(net_salary)::numeric,0)  AS avg_net,
           COUNT(*)                            AS headcount
    FROM payroll GROUP BY job_role ORDER BY avg_net DESC
""")

overtime = query("""
    SELECT department, location,
           SUM(CASE WHEN overtime_flag=1 THEN 1 ELSE 0 END) AS overtime_count,
           COUNT(*)                                           AS total,
           ROUND(100.0*SUM(CASE WHEN overtime_flag=1 THEN 1 ELSE 0 END)/COUNT(*),1) AS ot_rate
    FROM payroll GROUP BY department, location ORDER BY ot_rate DESC
""")

app = Dash(__name__)
DEPTS = ['All'] + sorted(dept_payroll['department'].tolist())

app.layout = html.Div([
    html.H1("Payroll Analytics Dashboard",
            style={'fontFamily':'Arial','marginBottom':'8px','fontSize':'22px'}),
    html.P("SQL-driven analytics on 100,000 payroll records | PostgreSQL + Plotly Dash",
           style={'color':'#6B7280','marginBottom':'20px','fontSize':'13px'}),

    html.Div([
        html.Div([html.P("Total Records", style={'fontSize':'12px','color':'#6B7280','margin':'0'}),
                  html.P("100,000",style={'fontSize':'22px','fontWeight':'500','margin':'0'})],
                 style={'background':'#F3F4F6','borderRadius':'8px','padding':'12px','flex':'1'}),
        html.Div([html.P("Departments",style={'fontSize':'12px','color':'#6B7280','margin':'0'}),
                  html.P(str(len(dept_payroll)),style={'fontSize':'22px','fontWeight':'500','margin':'0'})],
                 style={'background':'#F3F4F6','borderRadius':'8px','padding':'12px','flex':'1'}),
        html.Div([html.P("Avg Net Salary",style={'fontSize':'12px','color':'#6B7280','margin':'0'}),
                  html.P(f"₹{int(dept_payroll['avg_salary'].mean()):,}",
                         style={'fontSize':'22px','fontWeight':'500','margin':'0'})],
                 style={'background':'#F3F4F6','borderRadius':'8px','padding':'12px','flex':'1'}),
        html.Div([html.P("Date Range",style={'fontSize':'12px','color':'#6B7280','margin':'0'}),
                  html.P("2022–2024",style={'fontSize':'22px','fontWeight':'500','margin':'0'})],
                 style={'background':'#F3F4F6','borderRadius':'8px','padding':'12px','flex':'1'}),
    ], style={'display':'flex','gap':'12px','marginBottom':'20px'}),

    html.Div([
        html.Label("Filter by Department:", style={'fontSize':'13px','fontWeight':'500'}),
        dcc.Dropdown(id='dept-filter', options=[{'label':d,'value':d} for d in DEPTS],
                     value='All', clearable=False,
                     style={'width':'300px','marginTop':'4px'}),
    ], style={'marginBottom':'20px'}),

    html.Div([
        dcc.Graph(id='dept-bar'),
        dcc.Graph(id='monthly-trend'),
    ], style={'display':'grid','gridTemplateColumns':'1fr 1fr','gap':'16px'}),

    html.Div([
        dcc.Graph(id='role-chart'),
        dcc.Graph(id='overtime-chart'),
    ], style={'display':'grid','gridTemplateColumns':'1fr 1fr','gap':'16px','marginTop':'16px'}),

], style={'fontFamily':'Arial','padding':'24px','maxWidth':'1200px','margin':'0 auto'})

@app.callback(
    [Output('dept-bar','figure'), Output('monthly-trend','figure'),
     Output('role-chart','figure'), Output('overtime-chart','figure')],
    Input('dept-filter','value')
)
def update(dept):
    dp = dept_payroll if dept=='All' else dept_payroll[dept_payroll['department']==dept]
    ot = overtime     if dept=='All' else overtime[overtime['department']==dept]

    fig1 = px.bar(dp, x='department', y='avg_salary', color='headcount',
                  title='Average net salary by department',
                  color_continuous_scale='Blues',
                  labels={'avg_salary':'Avg Net Salary (₹)','headcount':'Headcount'})
    fig1.update_layout(showlegend=False, plot_bgcolor='white', paper_bgcolor='white')

    fig2 = px.line(monthly, x='period', y='total_payroll',
                   title='Monthly total payroll trend (2022–2024)',
                   labels={'total_payroll':'Total Payroll (₹)','period':'Month'})
    fig2.update_traces(line_color='#378ADD', line_width=2)
    fig2.update_layout(plot_bgcolor='white', paper_bgcolor='white')
    fig2.update_xaxes(tickangle=45, nticks=12)

    fig3 = px.bar(role_data, x='job_role', y=['avg_base','avg_bonus'],
                  title='Base salary vs bonus by job role', barmode='stack',
                  labels={'value':'Amount (₹)','variable':'Component'},
                  color_discrete_map={'avg_base':'#378ADD','avg_bonus':'#1D9E75'})
    fig3.update_layout(plot_bgcolor='white', paper_bgcolor='white')

    fig4 = px.bar(ot.head(10), x='department', y='ot_rate', color='location',
                  title='Overtime rate (%) by department and location',
                  labels={'ot_rate':'Overtime Rate (%)','location':'Location'})
    fig4.update_layout(plot_bgcolor='white', paper_bgcolor='white')

    return fig1, fig2, fig3, fig4

if __name__ == '__main__':
    app.run(debug=True)