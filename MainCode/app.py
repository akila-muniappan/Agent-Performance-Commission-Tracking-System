from nicegui import ui, app
import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage
import httpx
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
client = httpx.Client(verify=False, timeout=None)

llm = ChatOpenAI(
    base_url="",//URL
    model="",//Model ID
    api_key="",//KEY
    http_client=client
)

# Removed the create_agent line - we'll use llm directly

with open('new_agent20.json', 'r') as file:
    agent_data = json.load(file)

users = {'admin': {'password': 'admin123', 'role': 'admin'}}
for agent_id in agent_data.keys():
    users[agent_id] = {'password': 'agent123', 'role': 'agent'}

premium_system_prompt = """
You are an expert Insurance Agent assistant. Considering Today's date as 21-Nov-2025, provide:
a. Total premiumAmount - Calculate total for each policy type
b. Average Tenure - Calculate tenure (months) based on policySoldDate & policyExpiryDate, then average
c. Agent Commission - 10% of Total premiumAmount
d. Count of Premiums - Total premiums sold in last 6 months
e. Agent Productivity - Percentage of total premiumAmount (last 6 months) against targetAmount
f. Average Policy Value - Average premiumAmount of policies sold in last 3 months
Provide output as JSON only.
"""

def calculate_metrics(agent_id):
    if agent_id not in agent_data:
        return None
    clients = str(agent_data[agent_id]['salesDetails'])
    
    # Use llm directly - no agent needed
    result = llm.invoke([
        {"role": "system", "content": premium_system_prompt},
        {"role": "user", "content": clients}
    ])
    
    try:
        # Extract the content from the AIMessage
        content = result.content.strip('```json').strip('```').strip()
        return json.loads(content)
    except:
        return result.content

@ui.page('/')
def home_page():
    with ui.column().classes('absolute-center items-center gap-8'):
        ui.label('Agent Performance & Commission System').classes('text-h4 text-center')
        ui.label('Select Login Type').classes('text-h6')
        with ui.row().classes('gap-4'):
            ui.button('Administrator Login', on_click=lambda: ui.navigate.to('/admin-login')).classes('w-48')
            ui.button('Agent Login', on_click=lambda: ui.navigate.to('/agent-login')).classes('w-48')

@ui.page('/admin-login')
def admin_login_page():
    def handle_admin_login():
        if username_input.value in users and users[username_input.value]['password'] == password_input.value and users[username_input.value]['role'] == 'admin':
            app.storage.user['username'] = username_input.value
            app.storage.user['role'] = 'admin'
            ui.navigate.to('/admin')
        else:
            ui.notify('Invalid admin credentials', color='negative')
    
    with ui.card().classes('absolute-center'):
        ui.label('Administrator Login').classes('text-h4 text-center')
        username_input = ui.input('Username', placeholder='Enter admin username').classes('w-64')
        password_input = ui.input('Password', placeholder='Enter password', password=True).classes('w-64')
        password_input.on('keydown.enter', handle_admin_login)
        ui.button('Login', on_click=handle_admin_login).classes('w-64')
        ui.button('Back', on_click=lambda: ui.navigate.to('/')).classes('w-64')

@ui.page('/agent-login')
def agent_login_page():
    def handle_agent_login():
        if username_input.value in users and users[username_input.value]['password'] == password_input.value and users[username_input.value]['role'] == 'agent':
            app.storage.user['username'] = username_input.value
            app.storage.user['role'] = 'agent'
            ui.navigate.to('/employee')
        else:
            ui.notify('Invalid agent credentials', color='negative')
    
    with ui.card().classes('absolute-center'):
        ui.label('Agent Login').classes('text-h4 text-center')
        username_input = ui.input('Agent ID', placeholder='Enter agent ID').classes('w-64')
        password_input = ui.input('Password', placeholder='Enter password', password=True).classes('w-64')
        password_input.on('keydown.enter', handle_agent_login)
        ui.button('Login', on_click=handle_agent_login).classes('w-64')
        ui.button('Back', on_click=lambda: ui.navigate.to('/')).classes('w-64')

@ui.page('/admin')
def admin_dashboard():
    if app.storage.user.get('role') != 'admin':
        ui.navigate.to('/')
        return
    
    def logout():
        app.storage.user.clear()
        ui.navigate.to('/')
    
    with ui.header().classes('items-center justify-between p-4'):
        ui.label('Administrator Dashboard').classes('text-h5')
        ui.button('Logout', on_click=logout, icon='logout')
    
    with ui.tabs().classes('w-full') as tabs:
        overview_tab = ui.tab('Overview')
        agents_tab = ui.tab('All Agents')
        add_agent_tab = ui.tab('Add Agent')
        reports_tab = ui.tab('Reports')
    
    with ui.tab_panels(tabs, value=overview_tab).classes('w-full p-4'):
        with ui.tab_panel(overview_tab):
            ui.label('System Overview').classes('text-h5 mb-4')
            
            total_agents = len(agent_data)
            total_policies = sum(len(data['salesDetails']['clients']) for data in agent_data.values())
            total_premium = sum(client['premiumAmount'] for data in agent_data.values() for client in data['salesDetails']['clients'])
            
            with ui.row().classes('w-full gap-4'):
                with ui.card().classes('flex-1'):
                    ui.label('Total Agents').classes('text-subtitle2')
                    ui.label(str(total_agents)).classes('text-h4')
                with ui.card().classes('flex-1'):
                    ui.label('Total Policies Sold').classes('text-subtitle2')
                    ui.label(str(total_policies)).classes('text-h4')
                with ui.card().classes('flex-1'):
                    ui.label('Total Premium Amount').classes('text-subtitle2')
                    ui.label(f'₹{total_premium:,}').classes('text-h4')
                with ui.card().classes('flex-1'):
                    ui.label('Total Commission (10%)').classes('text-subtitle2')
                    ui.label(f'₹{int(total_premium * 0.1):,}').classes('text-h4')
            
            ui.label('Top Performing Agents').classes('text-h6 mt-6 mb-2')
            top_agents = sorted(agent_data.items(), key=lambda x: sum(c['premiumAmount'] for c in x[1]['salesDetails']['clients']), reverse=True)[:5]
            
            columns = [
                {'name': 'id', 'label': 'Agent ID', 'field': 'id', 'align': 'left'},
                {'name': 'name', 'label': 'Name', 'field': 'name', 'align': 'left'},
                {'name': 'region', 'label': 'Region', 'field': 'region', 'align': 'left'},
                {'name': 'premium', 'label': 'Total Premium', 'field': 'premium', 'align': 'right'},
                {'name': 'commission', 'label': 'Commission', 'field': 'commission', 'align': 'right'},
            ]
            
            rows = []
            for agent_id, data in top_agents:
                total = sum(c['premiumAmount'] for c in data['salesDetails']['clients'])
                rows.append({
                    'id': agent_id,
                    'name': f"{data['firstName']} {data['lastName']}",
                    'region': data['salesDetails']['regionName'],
                    'premium': f"₹{total:,}",
                    'commission': f"₹{int(total * 0.1):,}"
                })
            
            ui.table(columns=columns, rows=rows, row_key='id').classes('w-full')
        
        with ui.tab_panel(agents_tab):
            ui.label('All Agents').classes('text-h5 mb-4')
            
            columns = [
                {'name': 'id', 'label': 'Agent ID', 'field': 'id', 'align': 'left'},
                {'name': 'name', 'label': 'Name', 'field': 'name', 'align': 'left'},
                {'name': 'email', 'label': 'Email', 'field': 'email', 'align': 'left'},
                {'name': 'region', 'label': 'Region', 'field': 'region', 'align': 'left'},
                {'name': 'target', 'label': 'Target', 'field': 'target', 'align': 'right'},
                {'name': 'policies', 'label': 'Policies', 'field': 'policies', 'align': 'right'},
            ]
            
            rows = []
            for agent_id, data in agent_data.items():
                rows.append({
                    'id': agent_id,
                    'name': f"{data['firstName']} {data['lastName']}",
                    'email': data['email'],
                    'region': data['salesDetails']['regionName'],
                    'target': f"₹{data['salesDetails']['targetAmount']:,}",
                    'policies': len(data['salesDetails']['clients'])
                })
            
            ui.table(columns=columns, rows=rows, row_key='id').classes('w-full')
        
        with ui.tab_panel(add_agent_tab):
            with ui.card().classes('p-4'):
                ui.label('Add New Agent').classes('text-h6 mb-4')
                agent_id_input = ui.input('Agent ID', placeholder='AGT-XXXXX').classes('w-full')
                first_name_input = ui.input('First Name').classes('w-full')
                last_name_input = ui.input('Last Name').classes('w-full')
                email_input = ui.input('Email').classes('w-full')
                phone_input = ui.input('Phone').classes('w-full')
                region_input = ui.input('Region').classes('w-full')
                target_input = ui.number('Target Amount', value=100000).classes('w-full')
                
                def add_agent():
                    if not agent_id_input.value or agent_id_input.value in agent_data:
                        ui.notify('Invalid or duplicate Agent ID', color='negative')
                        return
                    
                    new_agent = {
                        agent_id_input.value: {
                            "firstName": first_name_input.value,
                            "lastName": last_name_input.value,
                            "email": email_input.value,
                            "phone": phone_input.value,
                            "salesDetails": {
                                "regionName": region_input.value,
                                "targetAmount": target_input.value,
                                "clients": []
                            }
                        }
                    }
                    agent_data.update(new_agent)
                    users[agent_id_input.value] = {'password': 'agent123', 'role': 'agent'}
                    with open('new_agent20.json', 'w') as f:
                        json.dump(agent_data, f, indent=2)
                    ui.notify('Agent added successfully', color='positive')
                    agent_id_input.value = ''
                    first_name_input.value = ''
                    last_name_input.value = ''
                    email_input.value = ''
                    phone_input.value = ''
                    region_input.value = ''
                
                ui.button('Add Agent', on_click=add_agent, icon='add').classes('mt-4')
        
        with ui.tab_panel(reports_tab):
            ui.label('Export & Reports').classes('text-h5 mb-4')
            
            with ui.card().classes('p-4'):
                ui.label('Export Agent Data for Audit').classes('text-h6 mb-2')
                ui.label('Export all agent data including sales records and commission details').classes('text-caption mb-4')
                
                def export_data():
                    export_content = {
                        'export_date': '21-Nov-2025',
                        'total_agents': len(agent_data),
                        'agents': agent_data
                    }
                    with open('agent_report.json', 'w') as f:
                        json.dump(export_content, f, indent=2)
                    ui.notify('Data exported to agent_report.json', color='positive')
                
                ui.button('Export to JSON', on_click=export_data, icon='download')

@ui.page('/employee')
def employee_dashboard():
    if app.storage.user.get('role') != 'agent':
        ui.navigate.to('/')
        return
    
    agent_id = app.storage.user.get('username')
    
    if agent_id not in agent_data:
        ui.label('Agent data not found')
        return
    
    def logout():
        app.storage.user.clear()
        ui.navigate.to('/')
    
    data = agent_data[agent_id]
    
    with ui.header().classes('items-center justify-between p-4'):
        ui.label(f'Agent Dashboard - {agent_id}').classes('text-h5')
        ui.button('Logout', on_click=logout, icon='logout')
    
    with ui.column().classes('w-full p-4 gap-4'):
        with ui.card().classes('w-full p-4'):
            ui.label('Profile Information').classes('text-h6 mb-2')
            with ui.row().classes('w-full gap-8'):
                with ui.column():
                    ui.label(f"Name: {data['firstName']} {data['lastName']}").classes('text-body1')
                    ui.label(f"Email: {data['email']}").classes('text-body1')
                with ui.column():
                    ui.label(f"Phone: {data['phone']}").classes('text-body1')
                    ui.label(f"Region: {data['salesDetails']['regionName']}").classes('text-body1')
                with ui.column():
                    ui.label(f"Target: ₹{data['salesDetails']['targetAmount']:,}").classes('text-body1')
        
        ui.label('Performance Metrics & KPIs').classes('text-h5 mt-4')
        
        metrics_container = ui.row().classes('w-full gap-4')
        
        with metrics_container:
            ui.spinner(size='lg')
            ui.label('Calculating metrics...')
        
        async def load_metrics():
            metrics = await ui.run_cpu_bound(calculate_metrics, agent_id)
            metrics_container.clear()
            
            if metrics and isinstance(metrics, dict):
                with metrics_container:
                    with ui.card().classes('flex-1 p-4'):
                        ui.label('Total Premium').classes('text-subtitle2')
                        ui.label(f"₹{metrics.get('Total premiumAmount', 'N/A')}").classes('text-h5')
                    
                    with ui.card().classes('flex-1 p-4'):
                        ui.label('Commission Earned (10%)').classes('text-subtitle2')
                        ui.label(f"₹{metrics.get('Agent Commission', 'N/A')}").classes('text-h5')
                    
                    with ui.card().classes('flex-1 p-4'):
                        ui.label('Productivity').classes('text-subtitle2')
                        ui.label(f"{metrics.get('Agent Productivity', 'N/A')}").classes('text-h5')
                    
                    with ui.card().classes('flex-1 p-4'):
                        ui.label('Avg Tenure').classes('text-subtitle2')
                        ui.label(f"{metrics.get('Average Tenure', 'N/A')} months").classes('text-h5')
                    
                    with ui.card().classes('flex-1 p-4'):
                        ui.label('Policies (6 months)').classes('text-subtitle2')
                        ui.label(f"{metrics.get('Count of Premiums', 'N/A')}").classes('text-h5')
            else:
                with metrics_container:
                    ui.label('Unable to calculate metrics')
        
        ui.timer(0.1, load_metrics, once=True)
        
        ui.label('Policy Sales Records').classes('text-h5 mt-6')
        
        columns = [
            {'name': 'client', 'label': 'Client Name', 'field': 'client', 'align': 'left'},
            {'name': 'policy', 'label': 'Policy Number', 'field': 'policy', 'align': 'left'},
            {'name': 'type', 'label': 'Type', 'field': 'type', 'align': 'left'},
            {'name': 'premium', 'label': 'Premium', 'field': 'premium', 'align': 'right'},
            {'name': 'sold_date', 'label': 'Sold Date', 'field': 'sold_date', 'align': 'left'},
            {'name': 'expiry_date', 'label': 'Expiry Date', 'field': 'expiry_date', 'align': 'left'},
            {'name': 'status', 'label': 'Status', 'field': 'status', 'align': 'left'},
        ]
        
        rows = []
        for client in data['salesDetails']['clients']:
            rows.append({
                'client': client['name'],
                'policy': client['policyNumber'],
                'type': client['policyType'],
                'premium': f"₹{client['premiumAmount']:,}",
                'sold_date': client['policySoldDate'],
                'expiry_date': client['policyExpiryDate'],
                'status': client['status']
            })
        
        ui.table(columns=columns, rows=rows, row_key='policy').classes('w-full')

ui.run(title='Agent Performance System', port=8081, storage_secret='agent_system_secret_key')
