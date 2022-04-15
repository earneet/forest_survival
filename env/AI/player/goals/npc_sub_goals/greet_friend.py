import numpy as np

from env.AI.player.goals.sub_goals.base_sub_goal import BaseSubGoal


class GreetFriend(BaseSubGoal):
    def __init__(self):
        super().__init__()

    def update(self, player) -> bool:
        players = self.get_around_player(player)
        if not players:     # no player nearby
            return False
        players.sort(key=lambda x: player.friend_ship[x.id] if x.id in player.friend_ship else float('inf'),
                     reverse=True)
        friend = players[0]
        distance = np.linalg.norm(friend.position - player.position)
        if distance < player.get_attack_range():
            player.greet(friend)
        else:
            player.move_to(friend.position)
        return True
