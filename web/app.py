from quart import Quart, render_template, request
import datetime

app = Quart(__name__, template_folder='templates')

start_time = datetime.datetime.now()

@app.route('/')
async def index():
    page = int(request.args.get('page', 1))
    search_query = request.args.get('search', '')
    servers = None#[server for server in bot.guilds if search_query.lower() in server.name.lower() or search_query in server.id]
    total_servers = len(servers)
    total_pages = (total_servers + 19) // 20  # 20 Server pro Seite
    servers = servers[(page-1)*20:page*20]
    uptime = datetime.datetime.now() - start_time
    uptime_str = str(uptime).split('.')[0]  # Remove milliseconds
    return await render_template('index.html', uptime=uptime_str, servers=servers, page=page, total_servers=total_servers, total_pages=total_pages, search_query=search_query)

@app.route('/server/<server_id>')
async def server_info(server_id):
    server = next((server for server in bot.guilds if server.id == server_id), None)
    if server:
        if server.member_count == 0:
            server = await bot.fetch_server(server_id)
            await server.fill_members()
        owner = await bot.fetch_user(server.owner_id)
        return await render_template('server_info.html', server=server, owner=owner)
    return 'Server not found', 404

def create_app(bot_instance):
    global bot
    bot = bot_instance
    return app
