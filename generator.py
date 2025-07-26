import requests

def generate_random_number():
    """
    Returns a truly random integer between 1 and 9 from random.org.
    Raises an exception if the request fails or the result is invalid.
    """
    response = requests.get(
        "https://www.random.org/integers/?num=1&min=1&max=9&col=1&base=10&format=plain&rnd=new",
        timeout=10
    )
    text = response.text.strip()
    if not text.isdigit():
        raise ValueError(f"Random.org error: {text}")
    return int(text)

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
    sfredelin_sum = sum(new_sums) - amarel_sum

    # Check primality
    player_primes = [is_prime(val) for val in new_sums]
    amarel_is_prime = is_prime(amarel_sum)
    sfredelin_is_prime = is_prime(sfredelin_sum)

    # Update prime counts
    for i in range(num_players):
        if player_primes[i]:
            session["prime_counts"][f"Player {i+1}"] += 1
    if amarel_is_prime:
        session["prime_counts"]["Amarel"] += 1
    if sfredelin_is_prime:
        session["prime_counts"]["Sfredelin"] += 1

    # Save state
    session["round"] = round_number
    session["sums"] = new_sums
    session["amarel_sum"] = amarel_sum
    session["sfredelin_sum"] = sfredelin_sum

    return jsonify({
        "round": round_number,
        "players": players,
        "sums": new_sums,
        "amarel": amarel_num,
        "amarel_sum": amarel_sum,
        "sfredelin_sum": sfredelin_sum,
        "primes": {
            "players": player_primes,
            "amarel": amarel_is_prime,
            "sfredelin": sfredelin_is_prime
        }
    })