#imports
import base64
from enum import Enum
from io import BytesIO
from flask import (
    Flask, 
    render_template, 
    session,
    redirect,
    request,
    url_for
)
from flask_socketio import SocketIO, emit
import time
import json
import multiprocessing as mp
import game
import matplotlib.pyplot as plt

#globals
app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
socketio = SocketIO(app)
UID = 0
admin_pwd = "KE7LXLo%295LuFqVG8%Rb2FSB#LJ4opG"

counter = 0

connected_sockets = set()
pStates = {-1: game.PDecisions.NULL}


class GameSig(Enum):
    Start = 0
    End = 1

#pages
@socketio.on('connect')
def handle_connect():
    # Add the socket to the set of connected sockets
    connected_sockets.add(request.sid)

@socketio.on('disconnect')
def handle_disconnect():
    # Remove the socket from the set of connected sockets when it disconnects
    connected_sockets.remove(request.sid)
    

def update_counter():
    global counter
    print(json.dumps({'counter': counter}))
    while True:
        counter += 1
        socketio.emit('update_counter', {'counter': counter})
        print(f"Updated. New value:{counter}")
        time.sleep(2)  # Update the counter every 5 seconds

@app.route("/game", methods=['GET', 'POST'])
def game_page():
    if session.get("role") != "guest":
        return redirect(url_for("index"))
    if request.method == "POST": 
        uid = session.get("UID")
        print(uid)
        if request.form.get('action') == "zdrada":
            print("ZDRAJCA!!!")
            pStates[uid] = game.PDecisions.BETRAY
        elif request.form.get("action") == "współpraca":
            print("Współpraca")
            pStates[uid] = game.PDecisions.COOPERATE
        

    return render_template("game.html")

def game_state_change(gs):
    if gs == GameSig.Start:
        socketio.emit('redirect', {'url': url_for("game_page")})
    elif gs == GameSig.End:
        socketio.emit('redirect', {'url': url_for("result_page")})


@app.route("/admin_panel", methods=['GET', 'POST'])
def admin_panel():
    global plot_data, pStates, results
    if session.get("role") != "admin":
        return redirect(url_for("index"))
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'start':
            game_state_change(GameSig.Start)
            pStates = {-1: game.PDecisions.NULL}
            results = {-1: 0}
            plot_data = None
            return render_template("admin_panel.html")

        elif action == 'end':
            game_state_change(GameSig.End)
            return redirect(url_for("result_page"))
    
    return render_template("admin_panel.html")

plot_data = None
results = {-1: 0}
def game_results(answers):
    decisions = {key: value for key, value in answers.items() if value != game.PDecisions.NULL}
    from itertools import combinations

    # Define the result table
    result_table = {
        (game.PDecisions.COOPERATE, game.PDecisions.COOPERATE): (-2, -2),
        (game.PDecisions.COOPERATE, game.PDecisions.BETRAY): (-5, 0),
        (game.PDecisions.BETRAY, game.PDecisions.COOPERATE): (0, -5),
        (game.PDecisions.BETRAY, game.PDecisions.BETRAY): (-4, -4)
    }

    # Initialize dictionaries to store results for each player
    player_results = {}
    # decisions = {}
    # for i in f:
    #     print(i)
    #     decisions[i[0]] = i[1]

    # Generate pairs of players to play one game each
    player_pairs = list(combinations(decisions.keys(), 2))

    # Iterate through player pairs and calculate results
    for player1, player2 in player_pairs:
        decision1 = decisions[player1]
        decision2 = decisions[player2]
        
        result = result_table.get((decision1, decision2))
        
        if result:
            player1_result, player2_result = result
            # Update results for both players
            player_results[player1] = player1_result
            player_results[player2] = player2_result

    # Print the results for each player
    for uid, result in player_results.items():
        print(f"{uid}: {result}")
        
    return player_results

def calc_results():
    global plot_data, results
    if plot_data == None:
        results = game_results(pStates)
        print(f"Results:\n{results}")
        x = ["Dwie zdrady", "Jedna zdrada", "Współpraca"]
        y = [results.values().count(-4)//2, results.values().count(0), results.values().count(-2)//2]
        
        plt.bar(x, y)
        plt.xlabel('możliwości')
        plt.ylabel('Liczba rozwiązań')
        plt.title('Dynamically Generated Bar Chart')

        # Save the Matplotlib plot to a BytesIO buffer
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        
        # Encode the plot as base64 for embedding in HTML
        plot_data = base64.b64encode(buffer.read()).decode('utf-8')
    return plot_data

@app.route("/result")
def result_page():
    # Generate the Matplotlib graph
    if not "role" in session: return redirect(url_for('index'))
    if session['role'] == 'admin': UID = -1
    else: UID = int(session['UID'])
    
    plot_data = calc_results()
    
    return render_template('plot.html', plot_data=plot_data, result=results.get(UID))

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        print(f"logging in with password: {request.form['password']} which is {'good' if request.form['password'] == admin_pwd else 'bad'}")
        if request.form["password"] == admin_pwd:
            session['role'] = 'admin'
            return redirect(url_for('admin_panel'))
        else:
            return redirect(url_for('login'))
    else:
        return render_template("login.html")

@app.route("/")
def index():
    global UID
    role = request.args.get("role")
    print(role)
    if role == "admin":
        if'role' in session and session['role'] == 'admin':
            redirect(url_for('admin_panel'))
        return redirect(url_for("login"))
    elif role == "guest":
        if 'role' in session and session["role"] == "guest":
           return redirect(url_for('game_page')) 
        session["role"] = "guest"
        session["UID"] = UID
        UID += 1
        return redirect(url_for('game_page'))
    else:
        return render_template('start_page.html')
    

if __name__ == '__main__':
    

    app.run(debug=True)
    
    socketio.run(app, debug=True)
    




