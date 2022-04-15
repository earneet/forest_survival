from collections import defaultdict
from os import path
import json

# from deepselector.constant import sub_goal_2_idx

parent_dir = path.dirname(__file__)
log_dir = path.join(parent_dir, "..", "logs")

goals = defaultdict(int)


def analysis():
    total = 0
    with open(path.join(log_dir, "log_0.log"), "r") as f:
        for line in f.readlines():
            data = json.loads(line)
            players = data["players"]
            for p in players:
                goals[p["sub_goal"]] += 1
                total += 1

    print(f"total: {total} ")
    print(goals)


if __name__ == "__main__":
    analysis()
