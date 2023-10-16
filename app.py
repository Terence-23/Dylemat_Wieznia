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
from flask_socketio import SocketIO
# import time
# import json
# import multiprocessing as mp
import game
import matplotlib.pyplot as plt
import secrets

#globals
app = Flask(__name__)
app.secret_key = secrets.token_urlsafe(20)
socketio = SocketIO(app)
UID = 0
admin_pwd = "KE7LXLo%295LuFqVG8%Rb2FSB#LJ4opG"

# counter = 0

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

@app.route("/game", methods=['GET', 'POST'])
def game_page():
    if session.get("role") == "admin":
        return redirect(url_for("admin_panel"))
    if session.get("role") != "guest":
        return redirect(url_for("index"))
    if not is_game_running: return redirect(url_for("waiting_room"))
    ld =""
    if request.method == "POST": 
        uid = session.get("UID")
        print(uid)
        if request.form.get('action') == "zdrada":
            print(UID)
            print("ZDRAJCA!!!")
            ld="Zdrada"
            pStates[uid] = game.PDecisions.BETRAY
        elif request.form.get("action") == "współpraca":
            print(UID)
            print("Współpraca")
            ld="Współpraca"
            pStates[uid] = game.PDecisions.COOPERATE
        

    return render_template("game.html", last_decision=ld)

is_game_running = False

def game_state_change(gs):
    global is_game_running, plot_data, results
    if gs == GameSig.Start:
        is_game_running = True
        socketio.emit('redirect', {'url': url_for("game_page")})
        
    elif gs == GameSig.End:        
        is_game_running = False
        plot_data = None
        results = None
        socketio.emit('redirect', {'url': url_for("result_page")})

@app.route("/waiting")
def waiting_room():
    if is_game_running: return redirect(url_for("game_page"))
    return render_template("Waiting room.html")

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

def create_pairs(lst):
    pairs = [(lst[i], lst[i - 1]) for i in range(1, len(lst), 2)]
    return pairs

plot_data = None
results = {-1: 0}
def game_results(answers):
    print("calculating results")
    decisions = {key: value for key, value in answers.items() if value != game.PDecisions.NULL}
    # from itertools import combinations

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
    player_pairs = create_pairs(list(decisions.keys()))
    print(player_pairs)

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
    print("Results")
    for uid, result in player_results.items():
        print(f"{uid}: {result}")
        
    return player_results

def calc_results():
    global plot_data, results
    if plot_data == None:
        results = game_results(pStates)
        
        print(f"Results: {results}")
        x = ["Dwie zdrady", "Jedna zdrada", "Współpraca"]
        y = [list(results.values()).count(-4)//2, list(results.values()).count(0), list(results.values()).count(-2)//2]
        print(y)
        
        
        fig, ax = plt.subplots()
        ax.bar(x, y)
        
        ax.set_xlabel("")
        ax.set_ylabel('Liczba rozwiązań')
        ax.set_title('Dynamically Generated Bar Chart')

        # Save the Matplotlib plot to a BytesIO buffer
        buffer = BytesIO()
        # plt.savefig
        fig.savefig(buffer, format='svg')
        # plt.savefig("static/plot.png" )
        buffer.seek(0)
        
        # Encode the plot as base64 for embedding in HTML
        plot_data = str(buffer.read(), encoding="utf-8")
    return plot_data

@app.route("/result")
def result_page():
    # Generate the Matplotlib graph
    if not "role" in session: return redirect(url_for('index'))
    if session['role'] == 'admin': UID = -1
    else: UID = int(session['UID'])
    
    plot_data = calc_results()
    
    return render_template('plot.html',plot_data=plot_data, result=results.get(UID), svg_plot_data=plot_data)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if session.get("role") == "admin": return redirect(url_for('admin_panel'))
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
    




