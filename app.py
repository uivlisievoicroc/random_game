from flask import Flask, jsonify, render_template, request, session
import random
import time

app = Flask(__name__)
app.secret_key = "super_secret_key"

# Helper to check for prime numbers
def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

# Global array for player names
playerNames = []

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/set_players", methods=["POST"])
def set_players():
    data = request.json
    num_players = int(data.get("num_players", 5))
    session["num_players"] = num_players
    session["round"] = 0
    session["sums"] = [0] * num_players
    session["total_sum"] = 0
    session["prime_counts"] = {f"Player {i+1}": 0 for i in range(num_players)}
    session["amarel_sum"] = 0
    session["sfredelin_sum"] = 0
    session["prime_counts"]["Amarel"] = 0
    session["prime_counts"]["Sfredelin"] = 0
    session["trantarel_sum"] = 0
    session["prime_counts"]["Trantarel"] = 0
    session["sfredelin_mode"] = data.get("sfredelin_mode", "normal")
    return jsonify({"status": "ok", "num_players": num_players})

@app.route("/api/round")
def game_round():
    num_players = session.get("num_players", 5)
    sums = session.get("sums", [0] * num_players)
    amarel_sum = session.get("amarel_sum", 0)
    round_number = session.get("round", 0) + 1

    # Generate numbers
    players = [random.randint(1, 9) for _ in range(num_players)]
    amarel_num = random.randint(1, 9)

    # Update sums
    new_sums = [s + p for s, p in zip(sums, players)]
    amarel_sum += amarel_num
    sfredelin_mode = session.get("sfredelin_mode")
    sfredelin_sum = 0
    for idx, val in enumerate(new_sums):
        if idx % 2 == 0:
            sfredelin_sum += val
        else:
            sfredelin_sum -= val
    # Include Amarel only if the number of players is odd
    if len(new_sums) % 2 == 1:
        sfredelin_sum -= amarel_sum
    if sfredelin_mode == "almighty":
        sfredelin_sum = abs(sfredelin_sum)

    trantarel_sum = session.get("trantarel_sum", 0)
    # Same formula as Sfredelin, excluding Amarel logic
    current_value = 0
    for idx, val in enumerate(new_sums):
        if idx % 2 == 0:
            current_value += val
        else:
            current_value -= val
    trantarel_sum += current_value
    if sfredelin_mode == "almighty":
        trantarel_sum = abs(trantarel_sum)

    # Check primality
    player_primes = [is_prime(val) for val in new_sums]
    amarel_is_prime = is_prime(amarel_sum)
    sfredelin_is_prime = is_prime(sfredelin_sum)
    trantarel_is_prime = is_prime(trantarel_sum)

    # Update prime counts
    for i in range(num_players):
        if player_primes[i]:
            session["prime_counts"][f"Player {i+1}"] += 1
    if amarel_is_prime:
        session["prime_counts"]["Amarel"] += 1
    if sfredelin_is_prime:
        session["prime_counts"]["Sfredelin"] += 1
    if trantarel_is_prime:
        session["prime_counts"]["Trantarel"] += 1

    # Save state
    session["round"] = round_number
    session["sums"] = new_sums
    session["amarel_sum"] = amarel_sum
    session["sfredelin_sum"] = sfredelin_sum
    session["trantarel_sum"] = trantarel_sum

    print(f"Round {round_number}, players: {players}, sums: {new_sums}, amarel_sum: {amarel_sum}, sfredelin_sum: {sfredelin_sum}, trantarel_sum: {trantarel_sum}")
    return jsonify({
        "round": round_number,
        "players": players,
        "sums": new_sums,
        "amarel": amarel_num,
        "amarel_sum": amarel_sum,
        "sfredelin_sum": sfredelin_sum,
        "trantarel_sum": trantarel_sum,
        "primes": {
            "players": player_primes,
            "amarel": amarel_is_prime,
            "sfredelin": sfredelin_is_prime,
            "trantarel": trantarel_is_prime
        }
    })

if __name__ == "__main__":
    app.run(debug=True)